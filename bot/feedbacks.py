from asyncio import Lock

from aiofiles import open

from bot.caches.paths import Paths


class Feedback:
    _lock = Lock()

    @classmethod
    async def save(cls, text: str) -> None:
        Paths.FEEDBACKS.parent.mkdir(parents=True, exist_ok=True)

        async with cls._lock:
            async with open(Paths.FEEDBACKS, "a", encoding="utf-8") as file:
                await file.write(f"{text}\n\n")
