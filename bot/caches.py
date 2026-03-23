from collections import namedtuple

from requests import Session

from bot.builders.attachments import (
    get_question_attachments,
    get_state1_attachments,
    get_state3_attachments,
    get_state4_attachments,
)
from bot.builders.texts import get_state3_text
from bot.preloads import get_groups, get_students, get_tests


with Session() as session:
    GROUPS = get_groups(session)
    STUDENTS = get_students(session)
    TESTS = get_tests(session)


TEXTS = namedtuple(
    "Texts",
    ["STATE1", "STATE2", "STATE3", "STATE4", "STOP"],
)(
    "<code>Шаг 1:\n\nВыберите вашу группу</code>",
    "<code>Шаг 2:\n\nВыберите себя из списка</code>",
    get_state3_text("Шаг 3:\nВыберите необходимый тест\n", TESTS),
    "Шаг 4:\nПодтвердите правильность данных\n\nГрупа: {}\nСтудент: {}\nТест: {}",
    "<code>Выполнение теста прервано</code>",
)


ATTACHMENTS = namedtuple(
    "Attachments",
    ["STATE1", "STATE3", "STATE4", "QUESTION"],
)(
    get_state1_attachments(GROUPS),
    get_state3_attachments(TESTS),
    get_state4_attachments(("Начать тест", "Прервать тест")),
    get_question_attachments(("1", "2", "3", "4")),
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
