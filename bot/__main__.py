import asyncio

from pyrogram.methods.utilities.idle import idle

from toolbot import ToolBot


async def main(bot=None):
    await bot.calculate_target_source()
    await bot.start()
    await idle()
    await bot.stop()

if __name__ == "__main__":
    bot = ToolBot()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(bot))

