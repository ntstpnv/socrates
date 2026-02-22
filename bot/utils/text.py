from typing import Iterable


def text_builder(start: str, data: Iterable[str]) -> str:
    text = [start]
    for i, element in enumerate(data, 1):
        text.append(f"{i} {element}")

    return "\n".join(text)
