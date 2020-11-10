from pyrogram import Client, filters

from config import Config


class ToolBot(Client):

    def __init__(self):
        super().__init__(
            session_name=Config.SESSION,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root="plugins")
        )

        @self.on_message(filters.command('check') & filters.me & filters.chat("me"))
        async def check(client, message):
            await message.reply("Helloooooo")