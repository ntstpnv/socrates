from asyncio import Lock, Semaphore
from ssl import create_default_context
from time import time_ns
from uuid import uuid4

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from sqlalchemy import Row

from bot.caches.paths import Paths
from bot.caches.texts import GigaChatText
from bot.contexts import Context
from bot.settings import AUTHORIZATION_KEY, logger


class GigaChat:
    _SEMAPHORE = Semaphore(1)
    _LOCK = Lock()

    _session = None
    _SSL = create_default_context(cafile=Paths.CERTIFICATE)
    _TIMEOUT = ClientTimeout(total=30, connect=10, sock_read=10)

    _access_token: str | None = None
    _expires_at: int | None = None

    @classmethod
    async def _refresh_session(cls) -> None:
        if not cls._session or cls._session.closed:
            cls._session = ClientSession(
                connector=TCPConnector(ssl=cls._SSL),
                timeout=cls._TIMEOUT,
            )

    @classmethod
    async def close(cls) -> None:
        if cls._session and not cls._session.closed:
            await cls._session.close()
        cls._session = None

    @classmethod
    async def _get_access_token(cls) -> str:
        async with cls._LOCK:
            if cls._access_token and time_ns() < cls._expires_at:
                return cls._access_token

            await cls._refresh_session()

            async with cls._session.post(
                "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "RqUID": f"{uuid4()}",
                    "Authorization": f"Basic {AUTHORIZATION_KEY}",
                },
                data={
                    "scope": "GIGACHAT_API_PERS",
                },
            ) as response:
                response.raise_for_status()
                data = await response.json()

            cls._access_token = data["access_token"]
            cls._expires_at = data["expires_at"] * 1_000_000 - 60_000_000_000

            return data["access_token"]

    @classmethod
    async def ask(cls, context: Context, pairs: list[Row]) -> str:
        async with cls._SEMAPHORE:
            try:
                access_token = await cls._get_access_token()

                await cls._refresh_session()

                async with cls._session.post(
                    "https://api.giga.chat/v2/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    },
                    json={
                        "model": "GigaChat-2",
                        "messages": [
                            {
                                "role": "system",
                                "content": [
                                    {
                                        "text": GigaChatText.PROMPT,
                                    },
                                ],
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": f"{pairs}",
                                    },
                                ],
                            },
                        ],
                        "model_options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "max_tokens": 1000,
                        },
                    },
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                logger.info(
                    "%s | reason=%s input=%s cached=%s output=%s",
                    context.user,
                    data["finish_reason"],
                    data["usage"]["input_tokens"],
                    data["usage"]["input_tokens_details"]["cached_tokens"],
                    data["usage"]["output_tokens"],
                )

                return data["messages"][0]["content"][0]["text"]

            except Exception as error:
                logger.info("%s\n%s", context.user, error)
                return "Не удалось сформировать рекомендации"
