from asyncio import run, to_thread
from json import dumps

from bot.db.models import Test
from bot.settings import ASYNC_SESSION, BACKUP_DIR
from sqlalchemy import select
from sqlalchemy.orm import selectinload


def _create(name: str, data: dict[int, dict[str, str]]) -> None:
    with open(BACKUP_DIR / name, "w", encoding="utf-8") as file:
        file.write(dumps(data, ensure_ascii=False, indent=2))


async def get_tests() -> None:
    async with ASYNC_SESSION() as session:
        stmt = select(Test).options(selectinload(Test.questions)).order_by(Test.name)
        tests = await session.scalars(stmt)

        for test in tests:
            data = {
                task.id: {
                    "0": task.question,
                    "1": task.option1,
                    "2": task.option2,
                    "3": task.option3,
                    "4": task.option4,
                }
                for task in sorted(test.questions, key=lambda t: t.id)
            }

            await to_thread(_create, f"{test.name}.json", data)


if __name__ == "__main__":
    run(get_tests())
