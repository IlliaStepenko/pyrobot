import os


class Config:
    API_ID = int(os.environ.get("APP_ID", 12345))
    API_HASH = os.environ.get("API_HASH", None)
    SESSION = os.environ.get("SESSION", None)