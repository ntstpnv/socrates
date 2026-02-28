from collections import deque
from random import choice, sample
from time import time

from aiohttp import ClientSession
from maxapi.context import MemoryContext
from orjson import loads

from bot.cache import PERMUTATIONS, PROGRESS_BARS, catalog
from bot.settings import URL_RAW
from bot.types import Types


async def test_preparation(test_id: str, context: MemoryContext) -> str:
    url = f"{URL_RAW}tests/{test_id}.json"
    async with ClientSession() as session:
        async with session.get(url) as response:
            test_data: Types.TestData = loads(await response.text())

    numbers = sample(list(test_data), 30)
    options: Types.Options = deque()
    tasks: Types.Tasks = deque()

    for number, progress_bar in zip(numbers, PROGRESS_BARS):
        new_order: Types.NewOrder = choice(PERMUTATIONS)
        options.append(
            {
                "1": number + new_order[0],
                "2": number + new_order[1],
                "3": number + new_order[2],
                "4": number + new_order[3],
            }
        )
        task = test_data[number]
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
        test_name=catalog[test_id],
        tasks=tasks,
        options=options,
        points=0,
        mistakes=[],
        start_time=int(time()),
    )

    return text
