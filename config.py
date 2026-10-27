import os
from dotenv import load_dotenv

load_dotenv()

CHATBOT_API_KEY = os.getenv("CHATBOT_API_KEY")
CHATBOT_BASE_URL = os.getenv("CHATBOT_BASE_URL")
CHATBOT_MODEL = os.getenv("CHATBOT_MODEL")

def get_config():
    return {
        "api_key": CHATBOT_API_KEY,
        "base_url": CHATBOT_BASE_URL,
        "model": CHATBOT_MODEL
    }
