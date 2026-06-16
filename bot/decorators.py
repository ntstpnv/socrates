from asyncio import Lock
from collections.abc import Awaitable, Callable
from functools import wraps

from maxapi.context import MemoryContext
from maxapi.types import MessageCallback

from bot.settings import LOCKS
from bot.utils.attachments import Payload


def callback_lock[**P](handler: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
    @wraps(handler)
    async def wrapper(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
        async with LOCKS.setdefault(event.from_user.user_id, Lock()):
            data = await context.get_data()

            if not data.get("step"):
                await context.update_data(step=3)
            elif data.get("step") == payload.step:
                await context.update_data(step=payload.step + 1)
            else:
                return None

            return await handler(event, context, payload)

    return wrapper
