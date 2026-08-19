from asyncio import Lock
from collections.abc import Awaitable, Callable
from functools import wraps

from maxapi.context import MemoryContext
from maxapi.types import MessageCallback

from bot.logger import logger
from bot.settings import LOCKS
from bot.utils.attachments import Payload

type Handler = Callable[[MessageCallback, MemoryContext, Payload], Awaitable[None]]


def callback_lock(handler: Handler) -> Handler:
    @wraps(handler)
    async def wrapper(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
        logger.info(
            "%s | step=%s | %s",
            event.callback.user.user_id,
            payload.step,
            event.callback.user.full_name,
        )

        async with LOCKS.setdefault(event.callback.user.user_id, Lock()):
            data = await context.get_data()

            if not data.get("step"):
                await context.update_data(step=3)
            elif data.get("step") == payload.step:
                await context.update_data(step=payload.step + 1)
            else:
                logger.info("%s | step=%s | debounce", event.callback.user.user_id, payload.step)
                return None

            return await handler(event, context, payload)

    return wrapper
