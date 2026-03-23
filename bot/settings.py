from os import getenv

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
PAT_TOKEN = getenv("PAT_TOKEN")

HEADERS = {"Authorization": f"Bearer {PAT_TOKEN}"}

URL_API = "https://api.github.com/repos/ntstpnv/socrates-db/contents/db/results.json"
URL_RAW = "https://raw.githubusercontent.com/ntstpnv/socrates-db/main/db/"
