from typing import Iterable

from maxapi.types import Attachment, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder


def attachments_builder(
    data: Iterable[str],
    equal: bool = True,
) -> list[Attachment]:
    attachment = InlineKeyboardBuilder()

    row = []
    for i, element in enumerate(data, 1):
        text = element if equal else str(i)
        row.append(CallbackButton(text=text, payload=element))
        if len(row) == 2:
            attachment.row(*row)
            row = []
    if row:
        attachment.row(*row)

    return [attachment.as_markup()]


def text_builder(start: str, data: Iterable[str]) -> str:
    text = [start]
    for i, element in enumerate(data, 1):
        text.append(f"{i} {element}")

    return "\n".join(text)
