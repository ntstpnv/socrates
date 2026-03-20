from asyncio import run
from datetime import datetime

from maxapi import Bot, Dispatcher
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.enums.parse_mode import ParseMode
from maxapi.types import Command, CommandStart, MessageCallback, MessageCreated

from bot.builders.attachments import get_state2_attachments
from bot.builders.texts import get_state4_text
from bot.caches import ATTACHMENTS, GROUPS, STUDENTS, TESTS, TEXTS
from bot.settings import BOT_TOKEN
from bot.utils import test_preparation, test_result


bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


class States(StatesGroup):
    STATE2 = State()
    STATE3 = State()
    STATE4 = State()
    STATE5 = State()
    STATE6 = State()


@dp.message_created(None, CommandStart())
async def select_group(event: MessageCreated, context: MemoryContext):
    await context.update_data(user_id=event.from_user.user_id)

    message = await event.message.answer(TEXTS.STATE1, ATTACHMENTS.STATE1)
    await context.update_data(message_id=message.message.body.mid)

    await context.set_state(States.STATE2)


@dp.message_callback(States.STATE2)
async def select_student(event: MessageCallback, context: MemoryContext):
    group_id = event.callback.payload
    await context.update_data(group_id=group_id, group=GROUPS[group_id])

    data = await context.get_data()
    students = {
        student_id: student.name
        for student_id, student in STUDENTS.items()
        if student.group_id == group_id
    }
    attachments = get_state2_attachments(students)
    await event.bot.edit_message(data["message_id"], TEXTS.STATE2, attachments)

    await context.set_state(States.STATE3)


@dp.message_callback(States.STATE3)
async def select_test(event: MessageCallback, context: MemoryContext):
    student_id = event.callback.payload
    await context.update_data(student_id=student_id, student=STUDENTS[student_id].name)

    data = await context.get_data()
    await event.bot.edit_message(data["message_id"], TEXTS.STATE3, ATTACHMENTS.STATE3)

    await context.set_state(States.STATE4)


@dp.message_callback(States.STATE4)
async def get_confirm(event: MessageCallback, context: MemoryContext):
    test_id = event.callback.payload
    await context.update_data(test_id=test_id, test=TESTS[test_id])

    data = await context.get_data()
    text = get_state4_text(TEXTS.STATE4, data["group"], data["student"], data["test"])
    await event.bot.edit_message(data["message_id"], text, ATTACHMENTS.STATE4)

    await context.set_state(States.STATE5)


@dp.message_callback(States.STATE5)
async def first_question(event: MessageCallback, context: MemoryContext):
    data = await context.get_data()

    if event.callback.payload == "Прервать тест":
        if message_id := data.get("message_id"):
            await event.bot.delete_message(message_id)
            await event.message.answer(TEXTS.STOP)

        await context.clear()
        return

    text = await test_preparation(context)
    await event.bot.edit_message(data["message_id"], text, ATTACHMENTS.QUESTION)

    await context.set_state(States.STATE6)


@dp.message_callback(States.STATE6)
async def next_question(event: MessageCallback, context: MemoryContext):
    option = event.callback.payload

    data = await context.get_data()
    answer = data["options"].popleft()[option]

    if answer.endswith("1"):
        data["points"] += 1
        await context.update_data(points=data["points"])
    else:
        data["mistakes"].append(answer)
        await context.update_data(mistakes=data["mistakes"])

    if not data["tasks"]:
        await test_result(data)

        await event.bot.edit_message(
            data["message_id"],
            f"<code>Группа: {data['group']}\n"
            f"Студент: {data['student']}\n"
            f"Тест: {data['test']}\n"
            f"Дата: {datetime.now().strftime('%H:%M %d.%m.%Y')}\n"
            f"Результат: {data['points']} из 30</code>",
        )

        await context.clear()
        return

    text = data["tasks"].popleft()
    await context.update_data(tasks=data["tasks"])
    await event.bot.edit_message(data["message_id"], text, ATTACHMENTS.QUESTION)


@dp.message_created(Command("stop"))
async def stop(event: MessageCreated, context: MemoryContext):
    data = await context.get_data()

    if message_id := data.get("message_id"):
        await event.bot.delete_message(message_id)
        await event.message.answer(TEXTS.STOP)

    await context.clear()


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    run(main())
