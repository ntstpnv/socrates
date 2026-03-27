from asyncio import run

from sqlalchemy import select

from bot.db.models import Base, Group, Student, Test, Task
from bot.db.services.new_groups import new_groups
from bot.settings import ASYNC_ENGINE, ASYNC_SESSION


# async def reset_tables() -> None:
#     async with ASYNC_ENGINE.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)


async def add_groups():
    for new_group, new_students in new_groups.items():
        async with ASYNC_SESSION.begin() as session:
            stmt = select(Group).where(Group.name == new_group)
            group = await session.scalar(stmt)

            if not group:
                group = Group(name=new_group)
                session.add(group)

            for new_student in new_students:
                stmt = select(Student).where(Student.name == new_student, Student.group == group)
                student = await session.scalar(stmt)

                if not student:
                    student = Student(name=new_student, group=group)
                    session.add(student)


async def main() -> None:
    pass
    # await reset_tables()
    # await add_groups()


if __name__ == "__main__":
    run(main())
