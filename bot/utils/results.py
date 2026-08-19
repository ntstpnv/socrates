from datetime import datetime, timedelta
from time import perf_counter

from bot.logger import logger
from bot.caches import UserStatement
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
    t0_connection = perf_counter()
    async with ASYNC_ENGINE.begin() as async_connection:
        t_connection = perf_counter() - t0_connection

        logger.info("%s | ADD_RESULT | t_connection=%.3fs", user_id, t_connection)

        t0_results = perf_counter()
        await async_connection.exec_driver_sql(
            UserStatement.ADD_RESULT.value,
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
        t_results = perf_counter() - t0_results

        logger.info("%s | ADD_RESULT | t_results=%.3fs", user_id, t_results)
