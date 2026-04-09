from asyncio import run
from collections import deque
from datetime import datetime
from random import choice

from maxapi import Bot, Dispatcher
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.enums.parse_mode import ParseMode
from maxapi.filters.command import Command, CommandStart
from maxapi.types import InputMediaBuffer, MessageCallback, MessageCreated

from bot.builders import AttachmentBuilder, RowBuilder
from bot.caches import ATTACHMENTS, PERMUTATIONS, PROGRESS_BARS, TEXTS
from bot.settings import ADMINS, TOKEN


bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


class States(StatesGroup):
    ADMIN2 = State()
    ADMIN3 = State()
    STUDENT2 = State()
    STUDENT3 = State()
    STUDENT4 = State()
    STUDENT5 = State()
    STUDENT6 = State()


@dp.message_created(None, Command("admin"))
async def select_group_(event: MessageCreated, context: MemoryContext):
    if event.from_user.user_id not in ADMINS:
        await context.clear()
        return

    groups = await RowBuilder.select_group_()
    attachments = AttachmentBuilder.from_rows(groups)

    message = await event.message.answer(TEXTS.ADMIN1, attachments)
    await context.update_data(message_id=message.message.body.mid)

    await context.set_state(States.ADMIN2)


@dp.message_callback(States.ADMIN2)
async def select_test_(event: MessageCreated, context: MemoryContext):
    group_id, _, group = event.callback.payload.partition("=")
    group_id = int(group_id)
    await context.update_data(group_id=group_id, group=group)

    data = await context.get_data()

    tests = await RowBuilder.select_test_(group_id)
    attachments = AttachmentBuilder.from_rows(tests)

    await event.bot.edit_message(data["message_id"], TEXTS.ADMIN2, attachments)

    await context.set_state(States.ADMIN3)


@dp.message_callback(States.ADMIN3)
async def get_results(event: MessageCreated, context: MemoryContext):
    test_id, _, test = event.callback.payload.partition("=")
    test_id = int(test_id)

    data = await context.get_data()

    results = await RowBuilder.get_results(data["group_id"], test_id)

    texts = [f"Группа: {data['group']}", f"Тест: {test}\n"]
    for r in results:
        if r.user_id:
            mistakes = " ".join(a for a in r.answers.split() if not a.endswith("1"))
            texts.append(
                f"{r.name}: {r.points} из 30\n{r.user_id} {r.full_name.strip()}\n{mistakes}\n"
            )
        else:
            texts.append(f"{r.name}\n")

    text = "\n".join(texts)
    attachments = [InputMediaBuffer(text.encode("utf-8"), "results.txt")]

    await event.message.delete()
    await event.bot.send_message(event.chat.chat_id, attachments=attachments)

    await context.clear()
    return


@dp.message_created(None, CommandStart())
async def select_group(event: MessageCreated, context: MemoryContext):
    await context.update_data(user_id=event.from_user.user_id, full_name=event.from_user.full_name)

    groups = await RowBuilder.select_group()
    attachments = AttachmentBuilder.from_rows(groups)

    message = await event.message.answer(TEXTS.STUDENT1, attachments)
    await context.update_data(message_id=message.message.body.mid)

    await context.set_state(States.STUDENT2)


@dp.message_callback(States.STUDENT2)
async def select_student(event: MessageCallback, context: MemoryContext):
    group_id, _, group = event.callback.payload.partition("=")
    group_id = int(group_id)
    await context.update_data(group_id=group_id, group=group)

    data = await context.get_data()

    students = await RowBuilder.select_student(group_id)
    attachments = AttachmentBuilder.from_rows(students)

    await event.bot.edit_message(data["message_id"], TEXTS.STUDENT2, attachments)

    await context.set_state(States.STUDENT3)


@dp.message_callback(States.STUDENT3)
async def select_test(event: MessageCallback, context: MemoryContext):
    student_id, _, student = event.callback.payload.partition("=")
    student_id = int(student_id)
    await context.update_data(student_id=student_id, student=student)

    data = await context.get_data()

    tests = await RowBuilder.select_test()
    attachments = AttachmentBuilder.from_rows(tests)

    await event.bot.edit_message(data["message_id"], TEXTS.STUDENT3, attachments)

    await context.set_state(States.STUDENT4)


@dp.message_callback(States.STUDENT4)
async def get_confirm(event: MessageCallback, context: MemoryContext):
    test_id, _, test = event.callback.payload.partition("=")
    test_id = int(test_id)
    await context.update_data(test_id=test_id, test=test)

    data = await context.get_data()

    text = (
        f"<code>Шаг 4:\n"
        f"Подтвердите правильность выбора\n\n"
        f"Група: {data['group']}\n"
        f"Студент: {data['student']}\n"
        f"Тест: {test}</code>"
    )

    await event.bot.edit_message(data["message_id"], text, ATTACHMENTS.STUDENT4)

    await context.set_state(States.STUDENT5)


@dp.message_callback(States.STUDENT5)
async def first_question(event: MessageCallback, context: MemoryContext):
    data = await context.get_data()

    if event.callback.payload == "Выбрать заново":
        await event.bot.edit_message(data["message_id"], TEXTS.STOP)

        await context.clear()
        return

    tasks = await RowBuilder.first_question(data["test_id"])
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
            f"(1) {order[new_order[0]]}\n"
            f"(2) {order[new_order[1]]}\n"
            f"(3) {order[new_order[2]]}\n"
            f"(4) {order[new_order[3]]}</code>"
        )

    text = messages.popleft()

    await context.update_data(
        messages=messages,
        options=options,
        answers=[],
        points=0,
        started_at=datetime.now(),
    )

    await event.bot.edit_message(data["message_id"], text, ATTACHMENTS.QUESTION)

    await context.set_state(States.STUDENT6)


@dp.message_callback(States.STUDENT6)
async def next_question(event: MessageCallback, context: MemoryContext):
    option = event.callback.payload

    data = await context.get_data()

    answer = data["options"].popleft()[option]
    data["answers"].append(answer)
    await context.update_data(answers=data["answers"])

    if answer.endswith("1"):
        data["points"] += 1
        await context.update_data(points=data["points"])

    if not data["messages"]:
        finished_at = datetime.now()

        await RowBuilder.add_result(
            data["user_id"],
            data["full_name"],
            data["group_id"],
            data["student_id"],
            data["test_id"],
            data["started_at"],
            finished_at,
            " ".join(sorted(data["answers"], key=lambda a: (len(a), a))),
            data["points"],
        )

        await event.bot.edit_message(
            data["message_id"],
            f"<code>Группа: {data['group'].replace('-', '_')}\n"
            f"Студент: {data['student']}\n"
            f"Тест: {data['test']}\n"
            f"Дата: {finished_at.strftime('%H_%M %d_%m_%Y')}\n"
            f"Результат: {data['points']} из 30</code>",
        )

        await context.clear()
        return

    text = data["messages"].popleft()
    await context.update_data(messages=data["messages"])

    await event.bot.edit_message(data["message_id"], text, ATTACHMENTS.QUESTION)


@dp.message_created(Command("stop"))
async def stop(event: MessageCreated, context: MemoryContext):
    data = await context.get_data()

    if message_id := data.get("message_id"):
        await event.bot.edit_message(message_id, TEXTS.STOP)

    await context.clear()
    return


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    run(main())
