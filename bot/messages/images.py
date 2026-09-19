from asyncio import get_running_loop
from io import BytesIO

from maxapi.types import InputMediaBuffer
from PIL import Image, ImageDraw, ImageFont

from bot.caches.paths import Paths


class ImageFactory:
    _BACKGROUND = Image.new("1", (1000, 1000), 1)
    _FONT = ImageFont.truetype(Paths.FONT, 38)

    EXECUTOR = None

    @classmethod
    def _create(cls, text: str) -> bytes:
        image = cls._BACKGROUND.copy()
        ImageDraw.Draw(image).multiline_text((0, 0), text, 0, cls._FONT)
        buffer = BytesIO()
        image.save(buffer, "WEBP", lossless=True, quality=60, method=1)

        return buffer.getvalue()

    @classmethod
    async def _to_bytes(cls, text: str) -> bytes:
        return await get_running_loop().run_in_executor(cls.EXECUTOR, cls._create, text)

    @classmethod
    async def from_text(cls, text: str) -> InputMediaBuffer:
        return InputMediaBuffer(await cls._to_bytes(text))
