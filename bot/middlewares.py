from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from maxapi.enums import ChatType
from maxapi.types import MessageCallback, MessageCreated

from bot.contexts import Context
from bot.limiters import Injection
from bot.messages.buttons import Payload
from bot.settings import logger
from bot.states import Admin, User


type Branch = type[Admin] | type[User]
type MessageCreatedDecorator = Callable[[MessageCreatedWrapper], MessageCreatedWrapper]
type MessageCreatedWrapper = Callable[[MessageCreated, Context], Awaitable[None]]

type MessageCallbackWrapper = Callable[[MessageCallback, Context, Payload], Awaitable[None]]


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


def branch_lock(branch: Branch) -> MessageCreatedDecorator:
    def decorator(handler: MessageCreatedWrapper) -> MessageCreatedWrapper:
        async def wrapper(event: MessageCreated, context: Context) -> None:
            if event.message.sender is None:
                return None
            if event.message.sender.is_bot:
                return None
            if event.message.recipient.chat_type != ChatType.DIALOG:
                return None
            if context.full_name is None:
                context.full_name = event.message.sender.full_name

            async with context.lock:
                if context.step:
                    return None

                context.branch = branch

                async with transactor(context):
                    return await handler(event, context)

        return wrapper

    return decorator


def callback_lock(handler: MessageCallbackWrapper) -> MessageCallbackWrapper:
    async def wrapper(event: MessageCallback, context: Context, payload: Payload) -> None:
        if event.message is None:
            return None

        async with context.lock:
            if payload.step != context.step:
                logger.info("%s | %s | debounce", context.user, context.state)
                return None

            async with transactor(context):
                return await handler(event, context, payload)

    return wrapper
