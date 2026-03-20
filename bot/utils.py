from base64 import b64decode, b64encode
from collections import deque
from random import choice, sample
from time import time
from typing import Any

from aiohttp import ClientSession
from maxapi.context import MemoryContext
from orjson import OPT_SORT_KEYS, dumps, loads

from bot.caches import PERMUTATIONS, PROGRESS_BARS
from bot.settings import HEADERS, URL_API, URL_RAW


async def test_preparation(context: MemoryContext) -> str:
    data = await context.get_data()

    url = f"{URL_RAW}db/tasks/{data['test_id']}.json"
    async with ClientSession() as session:
        async with session.get(url) as response:
            test = loads(await response.text())

    numbers = sample(list(test), 30)
    options, tasks = deque(), deque()

    for number, progress_bar in zip(numbers, PROGRESS_BARS):
        new_order = choice(PERMUTATIONS)
        options.append(
            {
                "1": number + new_order[0],
                "2": number + new_order[1],
                "3": number + new_order[2],
                "4": number + new_order[3],
            }
        )
        task = test[number]
        tasks.append(
            f"<code>{progress_bar}{task['0']}\n\n"
            f"(1) {task[new_order[0]]}\n"
            f"(2) {task[new_order[1]]}\n"
            f"(3) {task[new_order[2]]}\n"
            f"(4) {task[new_order[3]]}</code>"
        )

    text = tasks.popleft()

    await context.update_data(
        tasks=tasks,
        options=options,
        points=0,
        mistakes=[],
        started_at=int(time()),
    )

    return text


async def test_result(data: dict[str, Any]) -> None:
    finished_at = int(time())
    duration = finished_at - data["started_at"]
    mistakes = " ".join(sorted(data["mistakes"]))

    url = f"{URL_API}db/results.json"
    async with ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            response_dict = loads(await response.read())
            res_str = b64decode(response_dict["content"]).decode()
            res_dict = loads(res_str) if res_str else {}
            (
                res_dict.setdefault(data["group_id"], {})
                .setdefault(f"{data['student_id']} {data['user_id']}", {})
                .setdefault(data["test_id"], [])
                .append(f"{finished_at}={duration}={data['points']}={mistakes}")
            )

        async with session.put(
            url,
            json={
                "message": "+=",
                "content": b64encode(dumps(res_dict, option=OPT_SORT_KEYS)).decode(),
                "sha": response_dict["sha"],
            },
            headers=HEADERS,
        ) as _:
            pass
