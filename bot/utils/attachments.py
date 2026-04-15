from typing import Iterable

from maxapi.types import Attachment, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from sqlalchemy import Row


def _creator(buttons: list[CallbackButton], sizes: int) -> list[Attachment]:
    attachments = InlineKeyboardBuilder()
    attachments.add(*buttons)
    attachments.adjust(sizes)

    return [attachments.as_markup()]


def _from_row(row: Row) -> CallbackButton:
    return CallbackButton(text=row.name, payload=f"{row.id}={row.name}")


def _from_item(item: str) -> CallbackButton:
    return CallbackButton(text=item, payload=item)


class AttachmentFactory:
    @staticmethod
    def from_rows(rows: list[Row], sizes: int = 2) -> list[Attachment]:
        return _creator([_from_row(row) for row in rows], sizes)

    @staticmethod
    def from_items(items: Iterable[str], sizes: int) -> list[Attachment]:
        return _creator([_from_item(item) for item in items], sizes)
