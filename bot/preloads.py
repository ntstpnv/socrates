from collections import namedtuple

from requests import Session

from bot.settings import URL_RAW


Student = namedtuple("Student", ["name", "group_id"])


def _loader(session: Session, path: str) -> dict[str, str | int]:
    return session.get(f"{URL_RAW}{path}").json()


def _cleaner(data: dict[str, str | int]) -> dict[str, str]:
    return {k: v for k, v in data.items() if isinstance(v, str)}


def _sorter(data: dict[str, str | int]) -> dict[str, str]:
    return dict(sorted(data.items(), key=lambda tpl: tpl[1]))


def _splitter(data: dict[str, str], tpl: type[namedtuple]) -> dict[str, type[namedtuple]]:
    return {k: tpl(*v.split("=")) for k, v in data.items()}


def get_groups(session: Session, path: str) -> dict[str, str]:
    return _sorter(_cleaner(_loader(session, path)))


def get_students(session: Session, path: str) -> dict[str, Student]:
    return _splitter(_sorter(_cleaner(_loader(session, path))), Student)


def get_tests(session: Session, path: str) -> dict[str, str]:
    return _sorter(_cleaner(_loader(session, path)))
