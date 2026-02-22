from collections import deque
from random import choice, sample
from time import time

from aiohttp import ClientSession
from maxapi.context import MemoryContext
from orjson import loads

from bot.cache import PERMUTATIONS, PROGRESS_BARS
from bot.settings import URL_RAW


async def test_preparation(test_id: str, context: MemoryContext) -> str:
    url = f"{URL_RAW}tests/{test_id}.json"
    async with ClientSession() as session:
        async with session.get(url) as response:
            data: dict[str, dict[str, str]] = loads(await response.text())

    numbers = sample(list(data), 30)
    options: deque[dict[str, str]] = deque()
    tasks: deque[str] = deque()

    for number, progress_bar in zip(numbers, PROGRESS_BARS):
        new_order: tuple[str, str, str, str] = choice(PERMUTATIONS)
        options.append(
            {
                "1": number + new_order[0],
                "2": number + new_order[1],
                "3": number + new_order[2],
                "4": number + new_order[3],
            }
        )
        task = data[number]
        tasks.append(
            f"{progress_bar}{task['0']}\n\n"
            f"1 {task[new_order[0]]}\n"
            f"2 {task[new_order[1]]}\n"
            f"3 {task[new_order[2]]}\n"
            f"4 {task[new_order[3]]}"
        )

    text = tasks.popleft()

    await context.update_data(
        test_id=test_id,
        tasks=tasks,
        options=options,
        points=0,
        mistakes=[],
        timestamp=int(time()),
    )

    return text
