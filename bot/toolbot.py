import os

import openai
from pyrogram import Client
from googletrans import Translator

from database.main import AsyncDataSource


class ToolBot(Client):
    DEFAULT_LANG_CODES = ["en", "ru", "pl", "uk", "de", "it"]

    def __init__(self):

        try:
            from local_config import LocalConfig as bot_config
        except:
            from config import Config as bot_config

        self.data_source = AsyncDataSource()
        self.translator = Translator()

        self.last_media_group = None

        self.abuser_on = True
        self.counter = 0
        self.source_chats = []
        self.target_chats = []
        self.whitelist = []
        self.my_messages = dict()

        self.autotranslate = None
        self.ask_openai = False
        self.ai = openai.Completion

        self.lang_codes = self.DEFAULT_LANG_CODES.copy()
        self.nn_model = "text-davinci-003",
        self.temperature = float(0.5),
        self.max_tokens = int(1000),
        self.top_p = float(1.0),
        self.frequency_penalty = float(0.5),
        self.presence_penalty = float(0.5)


        super().__init__(
            session_string=bot_config.SESSION,
            name="toolbot",
            api_id=bot_config.API_ID,
            api_hash=bot_config.API_HASH,
            plugins=dict(
                root="plugins",
                include=['handlers', 'personal']
            )
        )

    async def calculate_target_source(self):
        config = await self.data_source.get_config()
        config = config[0]
        self.abuser_on = config['abuser_on']
        self.autotranslate = config['autotranslate_lang'] if config['autotranslate'] else None
        self.ask_openai = config['ask_open_ai']
        self.lang_codes = config['used_languages'].replace(' ', '').split(',')
        self.source_chats = [chat[1] for chat in await self.data_source.get_source_chats() if chat[3]]
        self.target_chats = [chat[1] for chat in await self.data_source.get_target_chats() if chat[3]]
        self.whitelist = [item[1].strip() for item in await self.data_source.get_white_list()]
