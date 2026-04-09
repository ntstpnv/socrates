from datetime import datetime

from sqlalchemy import Row

from bot.caches import STATEMENTS
from bot.settings import ASYNC_ENGINE


async def _get_rows(stmt: str, *args) -> list[Row]:
    async with ASYNC_ENGINE.connect() as conn:
        results = await conn.exec_driver_sql(stmt, args)
        rows = results.all()

    return rows


class RowBuilder:
    @staticmethod
    async def select_group_() -> list[Row]:
        return await _get_rows(STATEMENTS.ADMIN1)

    @staticmethod
    async def select_test_(group_id: int) -> list[Row]:
        return await _get_rows(STATEMENTS.ADMIN2, group_id)

    @staticmethod
    async def get_results(group_id: int, test_id: int) -> list[Row]:
        return await _get_rows(STATEMENTS.ADMIN3, group_id, test_id)

    @staticmethod
    async def select_group() -> list[Row]:
        return await _get_rows(STATEMENTS.STUDENT1)

    @staticmethod
    async def select_student(group_id: int) -> list[Row]:
        return await _get_rows(STATEMENTS.STUDENT2, group_id)

    @staticmethod
    async def select_test() -> list[Row]:
        return await _get_rows(STATEMENTS.STUDENT3)

    @staticmethod
    async def first_question(test_id: int) -> list[Row]:
        return await _get_rows(STATEMENTS.STUDENT5, test_id)

    @staticmethod
    async def add_result(
        user_id: int,
        full_name: str | None,
        group_id: int,
        student_id: int,
        test_id: int,
        started_at: datetime,
        finished_at: datetime,
        answers: str,
        points: int,
    ) -> None:
        async with ASYNC_ENGINE.begin() as conn:
            await conn.exec_driver_sql(
                STATEMENTS.STUDENT6,
                (
                    user_id,
                    full_name,
                    group_id,
                    student_id,
                    test_id,
                    started_at,
                    finished_at,
                    answers,
                    points,
                ),
            )
