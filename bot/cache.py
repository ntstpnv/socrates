from collections import namedtuple

from requests import Session

from bot.settings import URL_RAW
from bot.types import Types
from bot.utils.builders import attachments_builder, text_builder


with Session() as session:
    groups: Types.Groups = session.get(f"{URL_RAW}groups.json").json()
    catalog: Types.Catalog = session.get(f"{URL_RAW}catalog.json").json()


TEXT = namedtuple(
    "Text",
    ["STATE1", "STATE2", "STATE3", "STOP"],
)(
    "Шаг 1:\n\nВыберите вашу группу",
    "Шаг 2:\n\nВыберите себя из списка",
    text_builder("Шаг 3:\nВыберите необходимый тест\n", catalog.values()),
    "Прохождение теста прервано",
)


ATTACHMENTS = namedtuple(
    "Attachments",
    ["STATE1", "STATE3", "QUESTION"],
)(
    attachments_builder(groups),
    attachments_builder(catalog, False),
    attachments_builder(("1", "2", "3", "4")),
)


PERMUTATIONS = (
    ("1", "2", "3", "4"),
    ("1", "2", "4", "3"),
    ("1", "3", "2", "4"),
    ("1", "3", "4", "2"),
    ("1", "4", "2", "3"),
    ("1", "4", "3", "2"),
    ("2", "1", "3", "4"),
    ("2", "1", "4", "3"),
    ("2", "3", "1", "4"),
    ("2", "3", "4", "1"),
    ("2", "4", "1", "3"),
    ("2", "4", "3", "1"),
    ("3", "1", "2", "4"),
    ("3", "1", "4", "2"),
    ("3", "2", "1", "4"),
    ("3", "2", "4", "1"),
    ("3", "4", "1", "2"),
    ("3", "4", "2", "1"),
    ("4", "1", "2", "3"),
    ("4", "1", "3", "2"),
    ("4", "2", "1", "3"),
    ("4", "2", "3", "1"),
    ("4", "3", "1", "2"),
    ("4", "3", "2", "1"),
)


PROGRESS_BARS = (
    "Вопрос 1 из 30:\n",
    "Вопрос 2 из 30:\n",
    "Вопрос 3 из 30:\n",
    "Вопрос 4 из 30:\n",
    "Вопрос 5 из 30:\n",
    "Вопрос 6 из 30:\n",
    "Вопрос 7 из 30:\n",
    "Вопрос 8 из 30:\n",
    "Вопрос 9 из 30:\n",
    "Вопрос 10 из 30:\n",
    "Вопрос 11 из 30:\n",
    "Вопрос 12 из 30:\n",
    "Вопрос 13 из 30:\n",
    "Вопрос 14 из 30:\n",
    "Вопрос 15 из 30:\n",
    "Вопрос 16 из 30:\n",
    "Вопрос 17 из 30:\n",
    "Вопрос 18 из 30:\n",
    "Вопрос 19 из 30:\n",
    "Вопрос 20 из 30:\n",
    "Вопрос 21 из 30:\n",
    "Вопрос 22 из 30:\n",
    "Вопрос 23 из 30:\n",
    "Вопрос 24 из 30:\n",
    "Вопрос 25 из 30:\n",
    "Вопрос 26 из 30:\n",
    "Вопрос 27 из 30:\n",
    "Вопрос 28 из 30:\n",
    "Вопрос 29 из 30:\n",
    "Вопрос 30 из 30:\n",
)
