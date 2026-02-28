from collections import deque


class Types:
    Groups = dict[str, list[str]]
    Catalog = dict[str, str]
    TestData = dict[str, dict[str, str]]
    Options = deque[dict[str, str]]
    Tasks = deque[str]
    NewOrder = tuple[str, str, str, str]
