from typing import Iterable

from maxapi.types import Attachment, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


def _builder(buttons: list[CallbackButton], n: int) -> list[Attachment]:
    attachments = InlineKeyboardBuilder()
    attachments.add(*buttons)
    attachments.adjust(n)

    return [attachments.as_markup()]


def _from_iterable(data: Iterable[str]) -> list[CallbackButton]:
    return [CallbackButton(text=i, payload=i) for i in data]


def _from_dict(data: dict[str, str]) -> list[CallbackButton]:
    return [CallbackButton(text=v, payload=k) for k, v in data.items()]


def _from_enumerate_dict(data: dict[str, str]) -> list[CallbackButton]:
    return [CallbackButton(text=f"{i:02d}", payload=k) for i, (k, _) in enumerate(data.items(), 1)]


def get_state1_attachments(groups: dict[str, str]) -> list[Attachment]:
    return _builder(_from_dict(groups), 2)


def get_state2_attachments(students: dict[str, str]) -> list[Attachment]:
    return _builder(_from_dict(students), 2)


def get_state3_attachments(test: dict[str, str]) -> list[Attachment]:
    return _builder(_from_enumerate_dict(test), 4)


def get_state4_attachments(confirms: Iterable[str]) -> list[Attachment]:
    return _builder(_from_iterable(confirms), 1)


def get_question_attachments(options: Iterable[str]) -> list[Attachment]:
    return _builder(_from_iterable(options), 2)
