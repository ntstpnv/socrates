from asyncio import Lock
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from time import perf_counter_ns

from maxapi.context import MemoryContext
from maxapi.types import MessageCallback

from bot.limiters import Injection
from bot.messages.buttons import Payload
from bot.settings import LOCKS, logger


type Input = Callable[[MessageCallback, MemoryContext, Payload], Awaitable[None]]
type Output = Callable[[MessageCallback, MemoryContext, User], Awaitable[None]]


class User:
    __slots__ = ("id", "full_name", "payload", "data", "_metrics")

    def __init__(self, event: MessageCallback, payload: Payload) -> None:
        self.id = event.callback.user.user_id
        self.full_name = event.callback.user.full_name

        self.payload = payload

        self._metrics = {}

    @property
    def step(self) -> int:
        return self.payload.step

    @property
    def next_step(self) -> int:
        return self.payload.step + 1

    @property
    def metrics(self) -> str:
        return " ".join(f"{name}={value}" for name, value in self._metrics.items())

    @asynccontextmanager
    async def timer(self, name: str) -> AsyncIterator[None]:
        timestamp = perf_counter_ns()
        try:
            yield
        finally:
            self._metrics[name] = (perf_counter_ns() - timestamp) // 1_000_000

    @asynccontextmanager
    async def transactor(self, context: MemoryContext) -> AsyncIterator[None]:
        Injection.set(self.id, self.full_name, self.step)
        try:
            await context.update_data(step=self.next_step)
            yield
            logger.info("%s %s | %s | %s", self.id, self.full_name, self.step, self.metrics)
        except Exception:
            await context.update_data(step=self.step)
            raise
        finally:
            Injection.reset()


def callback_lock(handler: Output) -> Input:
    async def wrapper(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
        user = User(event, payload)

        async with LOCKS.setdefault(user.id, Lock()):
            user.data = await context.get_data()

            if user.step != user.data.get("step", 1):
                logger.info("%s %s | %s | debounce", user.id, user.full_name, user.step)
                return None

            async with user.transactor(context):
                return await handler(event, context, user)

    return wrapper
