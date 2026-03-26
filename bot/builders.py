from typing import Iterable

from maxapi.types import Attachment as Attachment
from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from sqlalchemy import Row


def _builder(buttons: list[CallbackButton], n: int) -> list[Attachment]:
    attachments = InlineKeyboardBuilder()
    attachments.add(*buttons)
    attachments.adjust(n)

    return [attachments.as_markup()]


def _from_rows(rows: list[Row]) -> list[CallbackButton]:
    return [CallbackButton(text=row.name, payload=f"{row.id}={row.name}") for row in rows]


def _from_iterable(items: Iterable[str]) -> list[CallbackButton]:
    return [CallbackButton(text=item, payload=item) for item in items]


class AttachmentBuilder:
    @staticmethod
    def from_rows(rows: list[Row], n: int = 2) -> list[Attachment]:
        return _builder(_from_rows(rows), n)

    @staticmethod
    def from_iterable(items: Iterable[str], n: int) -> list[Attachment]:
        return _builder(_from_iterable(items), n)
