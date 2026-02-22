from asyncio import run

from maxapi import Bot, Dispatcher
from maxapi.context import MemoryContext, State, StatesGroup
from maxapi.types import Command, CommandStart, MessageCallback, MessageCreated

from bot import settings
from bot.cache import ATTACHMENTS, TEXT, catalog, students
from bot.utils.attachments import attachments_builder
from bot.utils.preparation import test_preparation
from bot.utils.result import test_result


bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()


class States(StatesGroup):
    STATE2 = State()
    STATE3 = State()
    STATE4 = State()
    STATE5 = State()


@dp.message_created(None, CommandStart())
async def select_group(event: MessageCreated, context: MemoryContext):
    message = await event.message.answer(TEXT.STATE1, ATTACHMENTS.STATE1)
    await context.update_data(message_id=message.message.body.mid)

    await context.set_state(States.STATE2)


@dp.message_callback(States.STATE2)
async def select_name(event: MessageCallback, context: MemoryContext):
    group = event.callback.payload
    await event.answer(notification=group)
    await context.update_data(group=group)

    data = await context.get_data()
    attachments = attachments_builder(students[group])
    await event.bot.edit_message(data["message_id"], TEXT.STATE2, attachments)

    await context.set_state(States.STATE3)


@dp.message_callback(States.STATE3)
async def select_test(event: MessageCallback, context: MemoryContext):
    student = event.callback.payload
    await event.answer(notification=student)
    await context.update_data(name=f"{student} {event.from_user.user_id}")

    data = await context.get_data()
    await event.bot.edit_message(data["message_id"], TEXT.STATE3, ATTACHMENTS.STATE3)

    await context.set_state(States.STATE4)


@dp.message_callback(States.STATE4)
async def first_question(event: MessageCallback, context: MemoryContext):
    test_id = event.callback.payload
    await event.answer(notification=catalog[test_id])

    data = await context.get_data()
    text = await test_preparation(test_id, context)
    await event.bot.edit_message(data["message_id"], text, ATTACHMENTS.QUESTION)

    await context.set_state(States.STATE5)


@dp.message_callback(States.STATE5)
async def next_question(event: MessageCallback, context: MemoryContext):
    option = event.callback.payload
    await event.answer(notification=option)

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
            f"Результат: {data['points']} из 30",
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
        await event.message.answer(TEXT.STOP)

    await context.clear()


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    run(main())
