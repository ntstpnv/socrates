from asyncio import run
from base64 import b64decode, b64encode

from aiohttp import ClientSession
from orjson import dumps, loads, OPT_SORT_KEYS, OPT_INDENT_2

from config import HEADERS, URL_API, URL_RAW


async def crud(session: ClientSession) -> None:
    url = f"{URL_API}.json"

    async with session.get(
        url,
        headers=HEADERS,
    ) as response:
        body = await response.read()

    response_data = loads(body)
    data_str = b64decode(response_data["content"]).decode()
    data_dict = loads(data_str)

    #

    # data_bytes = dumps(data_dict, option=OPT_SORT_KEYS)
    data_bytes = dumps(data_dict, option=OPT_INDENT_2 | OPT_SORT_KEYS)
    data_str = b64encode(data_bytes).decode()

    async with session.put(
        url,
        json={
            "message": "+=",
            "content": data_str,
            "sha": response_data["sha"],
            # "sha": None,
        },
        headers=HEADERS,
    ) as response:
        print(response)


async def main():
    async with ClientSession() as session:
        await crud(session)


if __name__ == "__main__":
    run(main())