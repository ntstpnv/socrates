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
    AdminText,
    CommandText,
    UserAttachment,
    UserStatement,
    UserText,
)
from bot.settings import ADMINS, TOKEN
from bot.utils.attachments import AttachmentFactory
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
async def admin_selects_group(event: MessageCreated, context: MemoryContext):
    if event.from_user.user_id not in ADMINS:
        await context.clear()
        return

    groups = await get_rows(AdminStatement.GET_GROUPS)
    attachments = AttachmentFactory.from_rows(groups, 1)

    message = await event.message.answer(AdminText.SELECT_GROUP, attachments)
    await context.update_data(message_id=message.message.body.mid)

    await context.set_state(States.ADMIN2)


@dp.message_callback(States.ADMIN2)
async def admin_selects_test(event: MessageCreated, context: MemoryContext):
    group_id, _, group = event.callback.payload.partition("=")
    group_id = int(group_id)
    await context.update_data(group_id=group_id, group=group)

    data = await context.get_data()

    tests = await get_rows(AdminStatement.GET_TESTS, group_id)
    attachments = AttachmentFactory.from_rows(tests, 1)

    await event.bot.edit_message(data["message_id"], AdminText.SELECT_TEST, attachments)

    await context.set_state(States.ADMIN3)


@dp.message_callback(States.ADMIN3)
async def admin_gets_results(event: MessageCreated, context: MemoryContext):
    test_id, _, test = event.callback.payload.partition("=")
    test_id = int(test_id)

    data = await context.get_data()

    results = await get_rows(AdminStatement.GET_RESULTS, data["group_id"], test_id)

    texts = [f"Группа: {data['group']}", f"Тест: {test}\n"]
    for r in results:
        if r.user_id:
            mistakes = " ".join(a for a in r.answers.split() if not a.endswith("1"))
            mistakes = mistakes + "\n" if mistakes else ""
            texts.append(f"{r.name}: {r.points} из 30\n{r.user_id} {r.full_name}\n{mistakes}")
        else:
            texts.append(f"{r.name}\n")

    text = "\n".join(texts)
    attachments = [InputMediaBuffer(text.encode("utf-8"), "results.txt")]

    await event.message.delete()
    await event.bot.send_message(event.chat.chat_id, attachments=attachments)

    await context.clear()
    return


@dp.message_created(None, CommandStart())
async def user_selects_group(event: MessageCreated, context: MemoryContext):
    await context.update_data(user_id=event.from_user.user_id, full_name=event.from_user.full_name)

    groups = await get_rows(UserStatement.GET_GROUPS)
    attachments = AttachmentFactory.from_rows(groups)

    message = await event.message.answer(UserText.SELECT_GROUP, attachments)
    await context.update_data(message_id=message.message.body.mid)

    await context.set_state(States.USER2)


@dp.message_callback(States.USER2)
async def user_selects_student(event: MessageCallback, context: MemoryContext):
    group_id, _, group = event.callback.payload.partition("=")
    group_id = int(group_id)
    await context.update_data(group_id=group_id, group=group)

    data = await context.get_data()

    students = await get_rows(UserStatement.GET_STUDENTS, group_id)
    attachments = AttachmentFactory.from_rows(students)

    await event.bot.edit_message(data["message_id"], UserText.SELECT_STUDENT, attachments)

    await context.set_state(States.USER3)


@dp.message_callback(States.USER3)
async def user_selects_test(event: MessageCallback, context: MemoryContext):
    student_id, _, student = event.callback.payload.partition("=")
    student_id = int(student_id)
    await context.update_data(student_id=student_id, student=student)

    data = await context.get_data()

    tests = await get_rows(UserStatement.GET_TESTS)
    attachments = AttachmentFactory.from_rows(tests)

    await event.bot.edit_message(data["message_id"], UserText.SELECT_TEST, attachments)

    await context.set_state(States.USER4)


@dp.message_callback(States.USER4)
async def user_confirms_selection(event: MessageCallback, context: MemoryContext):
    test_id, _, test = event.callback.payload.partition("=")
    test_id = int(test_id)
    await context.update_data(test_id=test_id, test=test)

    data = await context.get_data()

    text = (
        f"<code>Шаг 4:\n"
        f"Подтвердите правильность выбора\n"
        f"\n"
        f"Група: {'\u200b'.join(data['group'])}\n"
        f"Студент: {data['student']}\n"
        f"Тест: {test}</code>"
    )

    await event.bot.edit_message(data["message_id"], text, UserAttachment.CONFIRM)

    await context.set_state(States.USER5)


@dp.message_callback(States.USER5)
async def user_gets_first_question(event: MessageCallback, context: MemoryContext):
    data = await context.get_data()

    if event.callback.payload == "Выбрать заново":
        await event.bot.edit_message(data["message_id"], CommandText.STOP)

        await context.clear()
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
            f"<code>{progress_bar}{task.question}\n\n"
            f"[1] {'\u200b'.join(order[new_order[0]])}\n"
            f"[2] {'\u200b'.join(order[new_order[1]])}\n"
            f"[3] {'\u200b'.join(order[new_order[2]])}\n"
            f"[4] {'\u200b'.join(order[new_order[3]])}</code>"
        )

    text = messages.popleft()

    await context.update_data(
        messages=messages,
        options=options,
        answers=[],
        points=0,
        started_at=datetime.now(),
    )

    await event.bot.edit_message(data["message_id"], text, UserAttachment.OPTIONS)

    await context.set_state(States.USER6)


@dp.message_callback(States.USER6)
async def user_gets_next_question(event: MessageCallback, context: MemoryContext):
    data = await context.get_data()

    answer = data["options"].popleft()[event.callback.payload]
    data["answers"].append(answer)
    await context.update_data(answers=data["answers"])

    if answer.endswith("1"):
        data["points"] += 1
        await context.update_data(points=data["points"])

    if not data["messages"]:
        finished_at = datetime.now()

        await add_result(
            data["user_id"],
            data["full_name"],
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
            f"<code>Группа: {'\u200b'.join(data['group'])}\n"
            f"Студент: {data['student']}\n"
            f"Тест: {data['test']}\n"
            f"Дата: {'\u200b'.join(finished_at.strftime('%H:%M %d.%m.%Y'))}\n"
            f"Результат: {data['points']} из 30</code>",
        )

        await context.clear()
        return

    text = data["messages"].popleft()
    await context.update_data(messages=data["messages"])

    await event.bot.edit_message(data["message_id"], text, UserAttachment.OPTIONS)


@dp.message_created(Command("stop"))
async def stop(event: MessageCreated, context: MemoryContext):
    data = await context.get_data()

    if message_id := data.get("message_id"):
        await event.bot.edit_message(message_id, CommandText.STOP)

    await context.clear()
    return


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    run(main())
