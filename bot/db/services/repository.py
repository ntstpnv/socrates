from datetime import datetime, timedelta

from sqlalchemy import Row

from bot.caches import STATEMENTS
from bot.settings import ASYNC_ENGINE


async def get_rows(statement: str, *args) -> list[Row]:
    async with ASYNC_ENGINE.connect() as async_connection:
        results = await async_connection.exec_driver_sql(statement, args)
        rows = results.all()

    return rows


async def add_result(
    user_id: int,
    full_name: str | None,
    group_id: int,
    student_id: int,
    test_id: int,
    finished_at: datetime,
    duration: timedelta,
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
                finished_at,
                duration,
                answers,
                points,
            ),
        )
