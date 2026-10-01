from contextlib import nullcontext
from contextvars import ContextVar
from time import perf_counter_ns

from aiohttp import ClientResponse, ClientSession
from aiohttp.typedefs import StrOrURL
from aiolimiter import AsyncLimiter
from yarl import URL

from bot.settings import logger


class Injection:
    _limiter = ContextVar[AsyncLimiter | None]("_limiter", default=None)
    _user = ContextVar[str | None]("_user", default=None)
    _state = ContextVar[str | None]("_state", default=None)

    @classmethod
    def set(cls, limiter: AsyncLimiter | None, user: str | None, state: str | None) -> None:
        cls._limiter.set(limiter)
        cls._user.set(user)
        cls._state.set(state)

    @classmethod
    def get(cls) -> tuple[AsyncLimiter | None, str | None, str | None]:
        return cls._limiter.get(), cls._user.get(), cls._state.get()

    @classmethod
    def reset(cls):
        cls._limiter.set(None)
        cls._user.set(None)
        cls._state.set(None)


_request = ClientSession._request


class Limiter:
    total = AsyncLimiter(30, 1)

    @staticmethod
    async def request(self, method: str, str_or_url: StrOrURL, **kwargs) -> ClientResponse:
        t1 = t2 = t3 = perf_counter_ns()
        status = None
        limiter, user, state = Injection.get()

        user_limiter = limiter or nullcontext()

        try:
            async with user_limiter:
                t2 = perf_counter_ns()
                async with Limiter.total:
                    t3 = perf_counter_ns()
                    response = await _request(self, method, str_or_url, **kwargs)
                    status = response.status
                    return response
        finally:
            t4 = perf_counter_ns()
            logger.info(
                "%s | %s | %s %s wait=%s wait=%s request=%s total=%s status=%s",
                user,
                state,
                method,
                URL(str_or_url).path,
                (t2 - t1) // 1_000_000,
                (t3 - t2) // 1_000_000,
                (t4 - t3) // 1_000_000,
                (t4 - t1) // 1_000_000,
                status,
            )

    @classmethod
    def activate(cls) -> None:
        ClientSession._request = cls.request
