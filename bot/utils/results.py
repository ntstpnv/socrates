from datetime import datetime, timedelta

from bot.caches import user_statements
from bot.settings import ASYNC_ENGINE


async def add_result(
    user_id: int,
    full_name: str | None,
    group_id: int,
    student_id: int,
    test_id: int,
    answers: str,
    points: int,
    finished_at: datetime,
    duration: timedelta,
) -> None:
    async with ASYNC_ENGINE.begin() as async_connection:
        await async_connection.exec_driver_sql(
            user_statements.ADD_RESULT,
            (
                user_id,
                full_name,
                group_id,
                student_id,
                test_id,
                answers,
                points,
                finished_at,
                duration,
            ),
        )
