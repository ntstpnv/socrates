from asyncio import Lock
from os import getenv
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


BASE_DIR = Path(__file__).resolve().parent.parent

BACKUP_DIR = BASE_DIR / "backup"
BACKUP_DIR.mkdir(exist_ok=True)

SECRETS_DIR = Path(getenv("SECRETS_DIR", "")) or BASE_DIR / "secrets"


def read_secret(secret: str) -> str:
    with open(SECRETS_DIR / secret, encoding="utf-8") as file:
        return file.read().strip()


TOKEN = read_secret("bot_token")

ADMINS = {int(user_id) for user_id in read_secret("bot_admins").split(",")}

LOCKS: dict[int, Lock] = {}

DB_PASS = read_secret("db_password")
DB_HOST = getenv("DB_HOST", "localhost")

DSN = f"postgresql+asyncpg://postgres:{DB_PASS}@{DB_HOST}:5432/postgres"

ASYNC_ENGINE = create_async_engine(DSN)

ASYNC_SESSION = async_sessionmaker(ASYNC_ENGINE)
