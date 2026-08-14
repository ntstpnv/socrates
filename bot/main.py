from asyncio import run
from collections import deque
from datetime import datetime
from random import choice

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
)
from bot.decorators import callback_lock
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
    if event.from_user.user_id not in ADMINS:
        return

    text = f"<code>Дата: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}\nАктивные пользователи: {len(LOCKS)}</code>"

    groups = await get_rows(AdminStatement.GET_GROUPS)
    attachments = AttachmentFactory.from_rows(2, groups, 2)

    message = await event.message.answer(text, attachments)
    await context.update_data(message_id=message.message.body.mid)

    await context.set_state(States.ADMIN2)


@dp.message_callback(States.ADMIN2, Payload.filter())
@callback_lock
async def admin_selects_test(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    data = await context.get_data()

    await context.update_data(group_id=payload.id, group=payload.name)

    text = f"<code>Группа: {payload.name}</code>"

    tests = await get_rows(AdminStatement.GET_TESTS, payload.id)
    attachments = AttachmentFactory.from_rows(data["step"], tests, 1)

    await event.bot.edit_message(data["message_id"], text, attachments)

    await context.set_state(States.ADMIN3)


@dp.message_callback(States.ADMIN3, Payload.filter())
@callback_lock
async def admin_gets_results(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    data = await context.get_data()

    results = await get_rows(AdminStatement.GET_RESULTS, data["group_id"], payload.id)

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

    await event.message.delete()
    await event.bot.send_message(event.chat.chat_id, attachments=attachments)

    await context.clear()
    LOCKS.pop(event.from_user.user_id, None)
    return


@dp.message_created(None, CommandStart())
async def user_selects_group(event: MessageCreated, context: MemoryContext) -> None:
    groups = await get_rows(UserStatement.GET_GROUPS)
    attachments = AttachmentFactory.from_rows(2, groups, 2)

    message = await event.message.answer(UserText.SELECT_GROUP, attachments)
    await context.update_data(message_id=message.message.body.mid)

    await context.set_state(States.USER2)


@dp.message_callback(States.USER2, Payload.filter())
@callback_lock
async def user_selects_student(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    data = await context.get_data()

    await context.update_data(group_id=payload.id, group=payload.name)

    students = await get_rows(UserStatement.GET_STUDENTS, payload.id)
    attachments = AttachmentFactory.from_rows(data["step"], students, 2)

    await event.bot.edit_message(data["message_id"], UserText.SELECT_STUDENT, attachments)

    await context.set_state(States.USER3)


@dp.message_callback(States.USER3, Payload.filter())
@callback_lock
async def user_selects_test(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    data = await context.get_data()

    await context.update_data(student_id=payload.id, student=payload.name)

    tests = await get_rows(UserStatement.GET_TESTS)
    attachments = AttachmentFactory.from_rows(data["step"], tests, 2)

    await event.bot.edit_message(data["message_id"], UserText.SELECT_TEST, attachments)

    await context.set_state(States.USER4)


@dp.message_callback(States.USER4, Payload.filter())
@callback_lock
async def user_confirms_selection(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    data = await context.get_data()

    await context.update_data(test_id=payload.id, test=payload.name)

    text = (
        f"<code>Шаг 4:\n"
        f"Подтвердите правильность выбора\n"
        f"\n"
        f"Група: {data['group']}\n"
        f"Студент: {data['student']}\n"
        f"Тест: {payload.name}</code>"
    )

    attachments = AttachmentFactory.from_items(data["step"], ("Начать тест", "Выбрать заново"), 1)

    await event.bot.edit_message(data["message_id"], text, attachments)

    await context.set_state(States.USER5)


@dp.message_callback(States.USER5, Payload.filter())
@callback_lock
async def user_gets_first_question(event: MessageCallback, context: MemoryContext, payload: Payload) -> None:
    data = await context.get_data()

    if payload.item == "Выбрать заново":
        await event.bot.edit_message(data["message_id"], CommonText.STOP)

        await context.clear()
        LOCKS.pop(event.from_user.user_id, None)
        return

    tasks = await get_rows(UserStatement.GET_TASKS, data["test_id"])
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

    await event.bot.edit_message(data["message_id"], text, attachments)

    await context.set_state(States.USER6)


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
            event.from_user.user_id,
            event.from_user.full_name,
            data["group_id"],
            data["student_id"],
            data["test_id"],
            " ".join(sorted(data["answers"], key=lambda a: (len(a), a))),
            data["points"],
            finished_at,
            finished_at - data["started_at"],
        )

        await event.bot.edit_message(
            data["message_id"],
            f"<code>Группа: {data['group']}\n"
            f"Студент: {data['student']}\n"
            f"Тест: {data['test']}\n"
            f"Дата: {finished_at.strftime('%H:%M %d.%m.%Y')}\n"
            f"Результат: {data['points']} из 30</code>",
        )

        await context.clear()
        LOCKS.pop(event.from_user.user_id, None)
        return

    text = data["messages"].popleft()
    await context.update_data(messages=data["messages"])

    attachments = AttachmentFactory.from_items(data["step"], ("1", "2", "3", "4"), 4)

    await event.bot.edit_message(data["message_id"], text, attachments)


@dp.message_created(Command("stop"))
async def stop(event: MessageCreated, context: MemoryContext) -> None:
    data = await context.get_data()

    if message_id := data.get("message_id"):
        await event.bot.edit_message(message_id, CommonText.STOP)

    await context.clear()
    LOCKS.pop(event.from_user.user_id, None)
    return


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    run(main())
