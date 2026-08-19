from asyncio import run
from collections import deque
from datetime import datetime
from random import choice
from time import perf_counter

from maxapi import Bot, Dispatcher
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.enums.parse_mode import ParseMode
from maxapi.filters.command import Command, CommandStart
from maxapi.types import InputMediaBuffer, MessageCallback, MessageCreated

from bot.caches import (
    PERMUTATIONS,
    PROGRESS_BARS,
    AdminStatement,
    CommonText,
    UserStatement,
    UserText,
    Item,
)
from bot.decorators import callback_lock
from bot.logger import logger
from bot.settings import ADMINS, LOCKS, TOKEN
from bot.utils.attachments import AttachmentFactory, Payload
from bot.utils.results import add_result
from bot.utils.rows import get_rows


dp = Dispatcher()
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)


class States(StatesGroup):
    ADMIN2 = State()
    ADMIN3 = State()
    USER2 = State()
    USER3 = State()
    USER4 = State()
    USER5 = State()
    USER6 = State()


@dp.message_created(None, Command("admin"))
async def admin_selects_group(event: MessageCreated, context: MemoryContext) -> None:
    _, user_id = event.get_ids()

    if user_id is None or user_id not in ADMINS:
        return

    text = f"<code>Дата: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}</code>"

    groups = await get_rows(user_id, AdminStatement.GET_GROUPS)

    attachments = AttachmentFactory.from_rows(2, groups, 2)

    await context.set_state(States.ADMIN2)

    t0_answer = perf_counter()
    message = await event.message.answer(text, attachments)
    t_answer = perf_counter() - t0_answer

    logger.info("%s | admin_selects_group | t_answer=%.3fs", user_id, t_answer)

    if message is None or message.message.body is None:
        return

    await context.update_data(message_id=message.message.body.mid)


@dp.message_callback(States.ADMIN2, Payload.filter())
@callback_lock
async def admin_selects_test(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    await context.update_data(group_id=payload.id, group=payload.name)

    text = f"<code>Группа: {payload.name}</code>"

    tests = await get_rows(event.callback.user.user_id, AdminStatement.GET_TESTS, payload.id)

    attachments = AttachmentFactory.from_rows(payload.step + 1, tests, 1)

    await context.set_state(States.ADMIN3)

    t0_edit = perf_counter()
    await event.edit(text, attachments)
    t_edit = perf_counter() - t0_edit

    logger.info("%s | admin_selects_test | t_edit=%.3fs", event.callback.user.user_id, t_edit)


@dp.message_callback(States.ADMIN3, Payload.filter())
@callback_lock
async def admin_gets_results(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    chat_id, user_id = event.get_ids()

    data = await context.get_data()

    results = await get_rows(user_id, AdminStatement.GET_RESULTS, data["group_id"], payload.id)

    texts = [f"Группа: {data['group']}", f"Тест: {payload.name}\n"]
    for r in results:
        if r.user_id:
            mistakes = " ".join(a for a in r.answers.split() if not a.endswith("1"))
            mistakes = mistakes + "\n" if mistakes else ""
            texts.append(f"{r.name}: {r.points} из 30\n{r.user_id} {r.full_name}\n{mistakes}")
        else:
            texts.append(f"{r.name}\n")

    text = "\n".join(texts)
    attachments = [InputMediaBuffer(text.encode("utf-8-sig"), "results.txt")]

    await event.delete()

    await bot.send_message(chat_id, user_id, attachments=attachments)

    await clear(event.callback.user.user_id, context)


@dp.message_created(None, CommandStart())
async def user_selects_group(event: MessageCreated, context: MemoryContext) -> None:
    _, user_id = event.get_ids()

    if user_id is None:
        return

    groups = await get_rows(user_id, UserStatement.GET_GROUPS)

    attachments = AttachmentFactory.from_rows(2, groups, 2)

    await context.set_state(States.USER2)

    t0_answer = perf_counter()
    message = await event.message.answer(UserText.SELECT_GROUP, attachments)
    t_answer = perf_counter() - t0_answer

    logger.info("%s | user_selects_group | t_answer=%.3fs", user_id, t_answer)

    if message is None or message.message.body is None:
        return

    await context.update_data(message_id=message.message.body.mid)


@dp.message_callback(States.USER2, Payload.filter())
@callback_lock
async def user_selects_student(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    await context.update_data(group_id=payload.id, group=payload.name)

    students = await get_rows(event.callback.user.user_id, UserStatement.GET_STUDENTS, payload.id)

    attachments = AttachmentFactory.from_rows(payload.step + 1, students, 2)

    await context.set_state(States.USER3)

    t0_edit = perf_counter()
    await event.edit(UserText.SELECT_STUDENT, attachments)
    t_edit = perf_counter() - t0_edit

    logger.info("%s | user_selects_student | t_edit=%.3fs", event.callback.user.user_id, t_edit)


@dp.message_callback(States.USER3, Payload.filter())
@callback_lock
async def user_selects_test(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    await context.update_data(student_id=payload.id, student=payload.name)

    tests = await get_rows(event.callback.user.user_id, UserStatement.GET_TESTS)

    attachments = AttachmentFactory.from_rows(payload.step + 1, tests, 2)

    await context.set_state(States.USER4)

    t0_edit = perf_counter()
    await event.edit(UserText.SELECT_TEST, attachments)
    t_edit = perf_counter() - t0_edit

    logger.info("%s | user_selects_test | t_edit=%.3fs", event.callback.user.user_id, t_edit)


@dp.message_callback(States.USER4, Payload.filter())
@callback_lock
async def user_confirms_selection(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    await context.update_data(test_id=payload.id, test=payload.name)

    data = await context.get_data()

    text = (
        f"<code>Шаг 4:\n"
        f"Подтвердите правильность выбора\n"
        f"\n"
        f"Група: {data['group']}\n"
        f"Студент: {data['student']}\n"
        f"Тест: {data['test']}</code>"
    )

    attachments = AttachmentFactory.from_items(data["step"], ("Начать тест", "Выбрать заново"), 1)

    await context.set_state(States.USER5)

    t0_edit = perf_counter()
    await event.edit(text, attachments)
    t_edit = perf_counter() - t0_edit

    logger.info("%s | user_confirms_selection | t_edit=%.3fs", event.callback.user.user_id, t_edit)


@dp.message_callback(States.USER5, Payload.filter())
@callback_lock
async def user_gets_first_question(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    if payload.item == "Выбрать заново":
        await event.edit(CommonText.STOP)
        await clear(event.callback.user.user_id, context)
        return

    data = await context.get_data()

    tasks = await get_rows(event.callback.user.user_id, UserStatement.GET_TASKS, data["test_id"])

    messages, options = deque(), deque()

    for task, progress_bar in zip(tasks, PROGRESS_BARS):
        order = {
            "1": task.option1,
            "2": task.option2,
            "3": task.option3,
            "4": task.option4,
        }
        new_order = choice(PERMUTATIONS)
        options.append(
            {
                "1": f"{task.id}-{new_order[0]}",
                "2": f"{task.id}-{new_order[1]}",
                "3": f"{task.id}-{new_order[2]}",
                "4": f"{task.id}-{new_order[3]}",
            }
        )
        messages.append(
            f"<code>{progress_bar}"
            f"{task.question}\n"
            f"\n"
            f"[1] {order[new_order[0]]}\n"
            f"[2] {order[new_order[1]]}\n"
            f"[3] {order[new_order[2]]}\n"
            f"[4] {order[new_order[3]]}</code>"
        )

    text = messages.popleft()

    await context.update_data(
        messages=messages,
        options=options,
        answers=[],
        points=0,
        started_at=datetime.now(),
    )

    attachments = AttachmentFactory.from_items(data["step"], ("1", "2", "3", "4"), 4)

    await context.set_state(States.USER6)

    t0_edit = perf_counter()
    await event.edit(text, attachments)
    t_edit = perf_counter() - t0_edit

    logger.info("%s | user_gets_first_question | t_edit=%.3fs", event.callback.user.user_id, t_edit)


@dp.message_callback(States.USER6, Payload.filter())
@callback_lock
async def user_gets_next_question(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    data = await context.get_data()

    answer = data["options"].popleft()[payload.item]
    await context.update_data(options=data["options"])

    data["answers"].append(answer)
    await context.update_data(answers=data["answers"])

    if answer.endswith("1"):
        data["points"] += 1
        await context.update_data(points=data["points"])

    if not data["messages"]:
        finished_at = datetime.now()

        await add_result(
            event.callback.user.user_id,
            event.callback.user.full_name,
            data["group_id"],
            data["student_id"],
            data["test_id"],
            " ".join(sorted(data["answers"], key=lambda a: (len(a), a))),
            data["points"],
            finished_at,
            finished_at - data["started_at"],
        )

        await event.edit(
            f"<code>Группа: {data['group']}\n"
            f"Студент: {data['student']}\n"
            f"Тест: {data['test']}\n"
            f"Дата: {finished_at.strftime('%H:%M %d.%m.%Y')}\n"
            f"Результат: {data['points']} из 30</code>",
        )

        await clear(event.callback.user.user_id, context)
        return

    text = data["messages"].popleft()
    await context.update_data(messages=data["messages"])

    attachments = AttachmentFactory.from_items(data["step"], ("1", "2", "3", "4"), 4)

    t0_edit = perf_counter()
    await event.edit(text, attachments)
    t_edit = perf_counter() - t0_edit

    logger.info("%s | user_gets_next_question | t_edit=%.3fs", event.callback.user.user_id, t_edit)


@dp.message_created(Command("stop"))
async def stop(event: MessageCreated, context: MemoryContext) -> None:
    _, user_id = event.get_ids()

    if user_id is None:
        return

    data = await context.get_data()

    if message_id := data.get("message_id", ""):
        await bot.edit_message(message_id, CommonText.STOP)
    else:
        logger.info("%s | stop | empty_message_id", user_id)

    await clear(user_id, context)


async def clear(user_id: int, context: MemoryContext) -> None:
    await context.clear()
    LOCKS.pop(user_id, None)
    logger.info("%s | clear", user_id)
    return


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    run(main())
