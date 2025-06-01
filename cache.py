from requests import Session


def url_raw(path: str) -> str:
    return f"https://raw.githubusercontent.com/ntstpnv/socrates/refs/heads/main/{path}"


def get_log() -> dict:
    with Session() as session:
        return session.get(url_raw("log.json")).json()


def get_test_catalog() -> dict[str, str]:
    with Session() as session:
        return session.get(url_raw("test_catalog.json")).json()


test_catalog = get_test_catalog()
