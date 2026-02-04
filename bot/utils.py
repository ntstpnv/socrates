from typing import Iterable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def reply_markup_builder(
    data: Iterable[str],
    equal: bool = True,
) -> InlineKeyboardMarkup:
    row, inline_keyboard = [], []
    for i, element in enumerate(data, 1):
        text = element if equal else str(i)
        row.append(InlineKeyboardButton(text, callback_data=element))
        if len(row) == 2:
            inline_keyboard.append(row)
            row = []
    if row:
        inline_keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard)


def text_builder(
    start: str,
    data: Iterable[str],
) -> str:
    text = [start]
    for i, element in enumerate(data, 1):
        text.append(f"{i} {element}")

    return "\n".join(text)
