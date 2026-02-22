from base64 import b64decode, b64encode
from time import time
from typing import Any

from aiohttp import ClientSession
from orjson import OPT_SORT_KEYS, dumps, loads

from bot.settings import HEADERS, URL_API


async def test_result(data: dict[str, Any]):
    timestamp = int(time())
    duration = timestamp - data["timestamp"]
    mistakes = " ".join(sorted(data["mistakes"]))

    url = f"{URL_API}log.json"
    async with ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            response_dict = loads(await response.read())
            log_str = b64decode(response_dict["content"]).decode()
            log_dict = loads(log_str) if log_str else {}
            (
                log_dict.setdefault(data["group"], {})
                .setdefault(data["name"], {})
                .setdefault(data["test_id"], [])
                .append(f"{timestamp}={duration}={data['points']}={mistakes}")
            )

        async with session.put(
            url,
            json={
                "message": "+=",
                "content": b64encode(dumps(log_dict, option=OPT_SORT_KEYS)).decode(),
                "sha": response_dict["sha"],
            },
            headers=HEADERS,
        ) as _:
            pass
