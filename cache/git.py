from base64 import b64decode
from pathlib import Path

from orjson import loads


def read_encoded_json(filename):
    file_path = Path(__file__).parent.parent.parent / filename
    with open(file_path, "r", encoding="utf-8") as file:
        encoded_data = file.read().strip()
    return loads(b64decode(encoded_data).decode("utf-8"))


def get_log():
    return read_encoded_json("log.json")


def get_student_data():
    return read_encoded_json("students.json")


def get_test_data():
    return read_encoded_json("tests.json")


login_data = {
    "students": get_student_data(),
    "tests": get_test_data(),
}
