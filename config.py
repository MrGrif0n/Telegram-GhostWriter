# here should be the greps from .env file
#BOT_TOKEN
# BOT_OWNER_ID


import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

BOT_OWNER_ID = os.getenv("BOT_OWNER_ID")