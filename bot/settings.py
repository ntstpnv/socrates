from os import getenv

from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
PAT_TOKEN = getenv("PAT_TOKEN")

HEADERS = {"Authorization": f"Bearer {PAT_TOKEN}"}

OWNER = getenv("OWNER")
REPO = getenv("REPO")
BRANCH = getenv("BRANCH")

URL_API = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/"
URL_RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/"
