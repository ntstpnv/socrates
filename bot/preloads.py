from base64 import b64decode
from collections import namedtuple

from orjson import loads
from requests import Session

from bot.settings import HEADERS, URL_API, URL_RAW


Student = namedtuple("Student", ["name", "group_id"])


def _loader(session: Session, url: str, headers: dict | None = None) -> dict:
    return loads(session.get(url, headers=headers).content)


def _cleaner(data: dict[str, str | int]) -> dict[str, str]:
    return {k: v for k, v in data.items() if isinstance(v, str)}


def _sorter(data: dict[str, str]) -> dict[str, str]:
    return dict(sorted(data.items(), key=lambda tpl: tpl[1]))


def _splitter(data: dict[str, str], tpl: type[namedtuple]) -> dict[str, type[namedtuple]]:
    return {k: tpl(*v.split("=")) for k, v in data.items()}


def _deserializer(response: dict) -> dict:
    return loads(b64decode(response["content"]).decode())


def get_groups(session: Session) -> dict[str, str]:
    return _sorter(_cleaner(_loader(session, f"{URL_RAW}groups.json")))


def get_students(session: Session) -> dict[str, Student]:
    return _splitter(_sorter(_cleaner(_loader(session, f"{URL_RAW}students.json"))), Student)


def get_tests(session: Session) -> dict[str, str]:
    return _sorter(_cleaner(_loader(session, f"{URL_RAW}tests.json")))


def get_results(session: Session) -> dict:
    return _deserializer(_loader(session, URL_API, HEADERS))
