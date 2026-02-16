from asyncio import sleep
from base64 import b64decode, b64encode
from collections import deque
from random import choice, sample
from time import time

from aiohttp import ClientSession
from orjson import OPT_SORT_KEYS, dumps, loads
from telegram import Update
from telegram.ext import (
    AIORateLimiter,
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)

from bot.cache import PROGRESS_BARS, REPLY_MARKUP, TEXT, VARIANTS, students
from bot.config import BOT_TOKEN, HEADERS, URL_API, URL_RAW
from bot.utils import reply_markup_builder


async def update_log(g: str, n: str, t: str, r: str) -> None:
    url = f"{URL_API}log.json"

    async with ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            response_dict = loads(await response.read())
            log_str = b64decode(response_dict["content"]).decode()
            log_dict = loads(log_str) if log_str else {}
            log_dict.setdefault(g, {}).setdefault(n, {}).setdefault(t, []).append(r)

        async with session.put(
            url,
            json={
                "message": "+=",
                "content": b64encode(dumps(log_dict, option=OPT_SORT_KEYS)).decode(),
                "sha": response_dict["sha"],
            },
            headers=HEADERS,
        ) as _:
            pass


async def select_group(u: Update, c: CallbackContext) -> int:
    c.user_data["chat_id"] = u.message.chat_id

    await sleep(0.4)
    c.user_data["message_id"] = (
        await u.message.reply_text(TEXT.STATE1, reply_markup=REPLY_MARKUP.STATE1)
    ).message_id

    return STATE2


async def select_name(u: Update, c: CallbackContext) -> int:
    await u.callback_query.answer()
    c.user_data["group"] = u.callback_query.data

    reply_markup = reply_markup_builder(students[c.user_data["group"]])

    await sleep(0.4)
    await u.callback_query.edit_message_text(TEXT.STATE2, reply_markup=reply_markup)

    return STATE3


async def select_test(u: Update, c: CallbackContext) -> int:
    await u.callback_query.answer()
    c.user_data["name"] = f"{u.callback_query.data} {u.callback_query.from_user.id}"

    await sleep(0.4)
    await u.callback_query.edit_message_text(
        TEXT.STATE3, reply_markup=REPLY_MARKUP.STATE3
    )

    return STATE4


async def preparation(u: Update, c: CallbackContext) -> int:
    await u.callback_query.answer()
    c.user_data["test_id"] = u.callback_query.data

    url = f"{URL_RAW}tests/{c.user_data['test_id']}.json"
    async with ClientSession() as session:
        async with session.get(url) as response:
            test = loads(await response.text())

    numbers = sample(list(test), 30)
    a_deque, q_deque = deque(), deque()
    for number, progress_bar in zip(numbers, PROGRESS_BARS):
        a1, a2, a3, a4 = choice(VARIANTS)
        a_deque.append(
            {
                "1": number + a1,
                "2": number + a2,
                "3": number + a3,
                "4": number + a4,
            }
        )
        question = test[number]
        q_deque.append(
            f"{progress_bar}{question['0']}\n\n"
            f"1 {question[a1]}\n"
            f"2 {question[a2]}\n"
            f"3 {question[a3]}\n"
            f"4 {question[a4]}"
        )

    c.user_data["A"] = a_deque
    c.user_data["points"], c.user_data["M"] = 0, []

    text = q_deque.popleft()
    c.user_data["Q"] = q_deque

    c.user_data["start_time"] = int(time())

    await u.callback_query.edit_message_text(text, reply_markup=REPLY_MARKUP.QUESTION)

    return STATE5


async def next_question(u: Update, c: CallbackContext) -> int:
    await u.callback_query.answer()
    answer = c.user_data["A"].popleft()[u.callback_query.data]

    if answer.endswith("1"):
        c.user_data["points"] += 1
    else:
        c.user_data["M"].append(answer)

    if not c.user_data["Q"]:
        finish_time = int(time())
        execution_time = finish_time - c.user_data["start_time"]
        mistakes = " ".join(sorted(c.user_data["M"]))

        await update_log(
            c.user_data["group"],
            c.user_data["name"],
            c.user_data["test_id"],
            f"{finish_time}={execution_time}={c.user_data['points']}={mistakes}",
        )

        await u.callback_query.edit_message_text(
            f"Результат: {c.user_data['points']} из 30"
        )

        return ConversationHandler.END

    text = c.user_data["Q"].popleft()

    await sleep(0.4)
    await u.callback_query.edit_message_text(text, reply_markup=REPLY_MARKUP.QUESTION)

    return STATE5


async def stop(u: Update, c: CallbackContext) -> int:
    await c.bot.delete_message(c.user_data["chat_id"], c.user_data["message_id"])
    await u.message.reply_text(TEXT.STOP)

    return ConversationHandler.END


if __name__ == "__main__":
    application = (
        Application.builder().rate_limiter(AIORateLimiter()).token(BOT_TOKEN).build()
    )

    conversation = ConversationHandler(
        [CommandHandler("start", select_group)],
        {
            (STATE2 := 2): [CallbackQueryHandler(select_name)],
            (STATE3 := 3): [CallbackQueryHandler(select_test)],
            (STATE4 := 4): [CallbackQueryHandler(preparation)],
            (STATE5 := 5): [CallbackQueryHandler(next_question)],
        },
        [CommandHandler("stop", stop)],
    )

    application.add_handler(conversation)

    application.run_polling(drop_pending_updates=True)
