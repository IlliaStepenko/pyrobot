import os

from pyrogram import Client, filters
import datetime


class ToolBot(Client):

    def __init__(self):

        try:
            from local_config import LocalConfig as bot_config
        except:
            from config import Config as bot_config


        super().__init__(
            session_name=bot_config.SESSION,
            api_id=bot_config.API_ID,
            api_hash=bot_config.API_HASH,
            plugins=dict(
                root="plugins",
                include=['handlers',]
            )
        )


