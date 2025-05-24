from orjson import loads
from requests import Session


def get_log():
    with Session() as session:
        response = session.get("https://raw.githubusercontent.com/ntstpnv/socrates/refs/heads/main/log.json")
        content = loads(response.text)

    return content


login_data = {}


with Session() as session:
    students_response = session.get("https://raw.githubusercontent.com/ntstpnv/socrates/refs/heads/main/students.json")
    login_data["students"] = loads(students_response.text)

    tests_response = session.get("https://raw.githubusercontent.com/ntstpnv/socrates/refs/heads/main/tests.json")
    login_data["tests"] = loads(tests_response.text)
