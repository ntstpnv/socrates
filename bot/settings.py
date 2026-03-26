from os import getenv

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


load_dotenv()

TOKEN = getenv("TOKEN")

ADMINS = {int(user_id) for user_id in getenv("ADMINS").split(",")}

DB_USER = getenv("DB_USER")
DB_PASS = getenv("DB_PASS")
DB_HOST = getenv("DB_HOST")
DB_PORT = getenv("DB_PORT")
DB_NAME = getenv("DB_NAME")

DSN = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

ASYNC_ENGINE = create_async_engine(DSN)

ASYNC_SESSION = async_sessionmaker(ASYNC_ENGINE)
