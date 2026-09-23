from collections import defaultdict
from contextlib import nullcontext
from contextvars import ContextVar
from time import perf_counter_ns

from aiohttp import ClientResponse, ClientSession
from aiohttp.typedefs import StrOrURL
from aiolimiter import AsyncLimiter
from yarl import URL

from bot.settings import logger


class Injection:
    _user_id: ContextVar[int | None] = ContextVar("_user_id", default=None)
    _full_name: ContextVar[str | None] = ContextVar("_full_name", default=None)
    _step: ContextVar[int | None] = ContextVar("_step", default=None)

    @classmethod
    def set(cls, user_id: int, full_name: str, step: int) -> None:
        cls._user_id.set(user_id)
        cls._full_name.set(full_name)
        cls._step.set(step)

    @classmethod
    def get(cls) -> tuple[int | None, str | None, int | None]:
        return cls._user_id.get(), cls._full_name.get(), cls._step.get()

    @classmethod
    def reset(cls):
        cls._user_id.set(None)
        cls._full_name.set(None)
        cls._step.set(None)


_request = ClientSession._request


class Limiter:
    total = AsyncLimiter(30, 1)
    users = defaultdict(lambda: AsyncLimiter(2, 1))

    @classmethod
    def user(cls, user_id: int | None):
        return cls.users[user_id] if user_id else nullcontext()

    @staticmethod
    async def request(
        self,
        method: str,
        str_or_url: StrOrURL,
        **kwargs,
    ) -> ClientResponse:
        t1 = t2 = perf_counter_ns()
        status = None

        user_id, full_name, step = Injection.get()

        try:
            async with Limiter.user(user_id), Limiter.total:
                t2 = perf_counter_ns()
                response = await _request(
                    self,
                    method,
                    str_or_url,
                    **kwargs,
                )
                status = response.status
                return response
        finally:
            t3 = perf_counter_ns()
            logger.info(
                "%s %s | %s | %s %s wait=%s request=%s status=%s",
                user_id,
                full_name,
                step,
                method,
                URL(str_or_url).path,
                (t2 - t1) // 1_000_000,
                (t3 - t2) // 1_000_000,
                status,
            )


ClientSession._request = Limiter.request
