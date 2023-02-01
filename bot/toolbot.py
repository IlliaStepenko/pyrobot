import os

from pyrogram import Client, filters
import datetime

from database.main import DataSource, AsyncDataSource


class ToolBot(Client):

    def __init__(self):

        try:
            from local_config import LocalConfig as bot_config
        except:
            from config import Config as bot_config

        self.data_source = AsyncDataSource()
        self.last_media_group = None

        self.abuser_on = False

        self.source_chats = []
        self.target_chats = []
        self.whitelist = []

        super().__init__(
            session_string=bot_config.SESSION,
            name="toolbot",
            api_id=bot_config.API_ID,
            api_hash=bot_config.API_HASH,
            plugins=dict(
                root="plugins",
                include=['handlers','personal']
            )
        )

    async def calculate_target_source(self):
        self.source_chats = [chat[1] for chat in await self.data_source.get_source_chats() if chat[3]]
        self.target_chats = [chat[1] for chat in await self.data_source.get_target_chats() if chat[3]]
        self.whitelist = [item[1].strip() for item in await self.data_source.get_white_list()]

