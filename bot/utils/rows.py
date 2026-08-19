from enum import Enum
from time import perf_counter

from sqlalchemy import Row

from bot.logger import logger
from bot.settings import ASYNC_ENGINE


async def get_rows(user_id: int, stmt: Enum, *args) -> list[Row]:
    t0_connection = perf_counter()
    async with ASYNC_ENGINE.connect() as async_connection:
        t_connection = perf_counter() - t0_connection

        logger.info("%s | %s | t_connection=%.3fs", user_id, stmt.name, t_connection)

        t0_results = perf_counter()
        results = await async_connection.exec_driver_sql(stmt.value, args)
        t_results = perf_counter() - t0_results

        logger.info("%s | %s | t_results=%.3fs", user_id, stmt.name, t_results)

        t0_rows = perf_counter()
        rows = results.all()
        t_rows = perf_counter() - t0_rows

        logger.info("%s | %s | t_rows=%.3fs", user_id, stmt.name, t_rows)

    return rows
