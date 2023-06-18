import os

from dotenv import load_dotenv


def load_env():
    load_dotenv()


def get_env(key):
    return os.getenv(key)
