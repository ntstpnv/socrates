from requests import Session


def url_raw(path: str) -> str:
    return f"https://raw.githubusercontent.com/ntstpnv/socrates/refs/heads/main/{path}"


def get_log() -> dict:
    with Session() as session:
        return session.get(url_raw("log.json")).json()


def get_login_data() -> dict:
    with Session() as session:
        return {
            "students": session.get(url_raw("students.json")).json(),
            "tests": session.get(url_raw("tests.json")).json(),
        }


login_data = get_login_data()
