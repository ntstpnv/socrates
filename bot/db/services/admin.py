from asyncio import run, to_thread
from json import dumps
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bot.db.models import Group, Student, Test
from bot.settings import ASYNC_SESSION


async def add_groups(new_groups: dict[str, list[str]]) -> None:
    async with ASYNC_SESSION.begin() as session:
        for new_group, new_students in new_groups.items():
            stmt = select(Group).where(Group.name == new_group)
            result = await session.execute(stmt)
            group = result.scalar_one_or_none()

            if not group:
                group = Group(name=new_group)
                session.add(group)

            for new_student in new_students:
                stmt = select(Student).where(Student.name == new_student, Student.group == group)
                result = await session.execute(stmt)
                student = result.scalar_one_or_none()

                if not student:
                    student = Student(name=new_student, group=group)
                    session.add(student)


def _create(name: str, data: dict[int, dict[str, str]]) -> None:
    with open(f"to_json/{name}.json", "w", encoding="utf-8") as file:
        file.write(dumps(data, ensure_ascii=False, indent=2))


async def to_json() -> None:
    Path("to_json").mkdir(exist_ok=True)

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
                for task in test.questions
            }

            await to_thread(_create, test.name, data)


async def main() -> None:
    pass
    # await add_groups()
    # await to_json()


if __name__ == "__main__":
    run(main())
