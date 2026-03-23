from typing import Iterable


def _builder(texts: Iterable[str]) -> str:
    return f"<code>{'\n'.join(texts)}</code>"


def _from_enumerate_dict(data: dict[str, str]) -> list[str]:
    return [f"({i}) {v}" for i, (_, v) in enumerate(data.items(), 1)]


def _from_template(template: str, *args) -> str:
    return f"<code>{template.format(*args)}</code>"


def get_state3_text(header: str, tests: dict[str, str]) -> str:
    return _builder([header] + _from_enumerate_dict(tests))


def get_state4_text(template: str, group: str, student: str, test: str) -> str:
    return _from_template(template, group, student, test)
