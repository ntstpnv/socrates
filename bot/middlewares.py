from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from maxapi.enums import ChatType
from maxapi.types import MessageCallback, MessageCreated

from bot.contexts import Context
from bot.limiters import Injection
from bot.messages.buttons import Payload
from bot.settings import logger


type MessageCallbackType = Callable[[MessageCallback, Context, Payload], Awaitable[None]]
type MessageCreatedType = Callable[[MessageCreated, Context], Awaitable[None]]


@asynccontextmanager
async def transactor(context: Context) -> AsyncGenerator[None, None]:
    context.next_state()
    Injection.set(context.limiter, context.user, context.state)
    try:
        yield
    except Exception:
        context.rollback()
        raise
    finally:
        Injection.reset()


def begin_lock(handler: MessageCreatedType) -> MessageCreatedType:
    async def wrapper(event: MessageCreated, context: Context) -> None:
        if event.message.sender is None:
            return None
        elif event.message.recipient.chat_type != ChatType.DIALOG:
            return None
        elif event.message.body is None:
            return None
        elif event.message.body.text is None:
            return None
        elif context.user_id is None:
            return None
        elif context.full_name is None:
            context.full_name = event.message.sender.full_name

        async with context.lock:
            if context.step:
                return None

            context.set_branch(event.message.body.text)

            async with transactor(context):
                return await handler(event, context)

    return wrapper


def callback_lock(handler: MessageCallbackType) -> MessageCallbackType:
    async def wrapper(event: MessageCallback, context: Context, payload: Payload) -> None:
        if event.message is None:
            return None
        elif event.message.sender is None:
            return None
        elif event.message.recipient.chat_type != ChatType.DIALOG:
            return None

        async with context.lock:
            if payload.step != context.step:
                logger.info("%s | %s | debounce", context.user, context.state)
                return None

            async with transactor(context):
                return await handler(event, context, payload)

    return wrapper
