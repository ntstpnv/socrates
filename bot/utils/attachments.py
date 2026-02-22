from typing import Iterable

from maxapi.types import Attachment, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from bot.cache import students


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


def students_attachments(group: str) -> list[Attachment]:
    return attachments_builder(students[group])
