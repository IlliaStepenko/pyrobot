from pyrogram import Client, filters
import datetime
from config import Config



config = Config


class ToolBot(Client):

    def __init__(self):
        super().__init__(
            session_name=config.SESSION,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            plugins=dict(
                root="plugins",
                include=['handlers',]
            )
        )


