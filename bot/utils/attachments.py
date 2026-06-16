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
    step: int
    id: int | None
    name: str | None
    item: str | None


def _pack_from_row(step: int, row: Row) -> str:
    return Payload(step=step, id=row.id, name=row.name, item=None).pack()


def _pack_from_item(step: int, item: str) -> str:
    return Payload(step=step, id=None, name=None, item=item).pack()


def _from_row(step: int, row: Row) -> CallbackButton:
    return CallbackButton(text=row.name, payload=_pack_from_row(step, row))


def _from_item(step: int, item: str) -> CallbackButton:
    return CallbackButton(text=item, payload=_pack_from_item(step, item))


class AttachmentFactory:
    @staticmethod
    def from_rows(step: int, rows: list[Row], sizes: int) -> list[Attachment]:
        return _create([_from_row(step, row) for row in rows], sizes)

    @staticmethod
    def from_items(step: int, items: Iterable[str], sizes: int) -> list[Attachment]:
        return _create([_from_item(step, item) for item in items], sizes)
