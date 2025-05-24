from pathlib import Path
from orjson import loads

def read_json(filename):
    file_path = Path(__file__).parent / filename
    with open(file_path, "r") as file:  # 'rb' для orjson
        return loads(file.text())

def get_student_data():
    return read_json("students.json")

def get_test_data():
    return read_json("tests.json")

login_data = {
    "students": get_student_data(),
    "tests": get_test_data()
}
