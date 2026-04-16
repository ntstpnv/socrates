from typing import Iterable

from maxapi.filters.callback_payload import CallbackPayload
from maxapi.types import Attachment, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from sqlalchemy import Row


def _create(buttons: list[CallbackButton], sizes: int) -> list[Attachment]:
    attachments = InlineKeyboardBuilder()
    attachments.add(*buttons)
    attachments.adjust(sizes)

    return [attachments.as_markup()]


class Payload(CallbackPayload):
    id: int
    name: str


def _pack_payload(row: Row) -> str:
    return Payload(id=row.id, name=row.name).pack()


def _from_row(row: Row) -> CallbackButton:
    return CallbackButton(text=row.name, payload=_pack_payload(row))


def _from_item(item: str) -> CallbackButton:
    return CallbackButton(text=item, payload=item)


class AttachmentFactory:
    @staticmethod
    def from_rows(rows: list[Row], sizes: int = 2) -> list[Attachment]:
        return _create([_from_row(row) for row in rows], sizes)

    @staticmethod
    def from_items(items: Iterable[str], sizes: int = 1) -> list[Attachment]:
        return _create([_from_item(item) for item in items], sizes)
