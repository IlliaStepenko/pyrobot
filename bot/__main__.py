import asyncio
import os
import subprocess

import openai
from pyrogram.methods.utilities.idle import idle

from toolbot import ToolBot


async def main(bot=None):
    try:
        from local_config import LocalConfig
        openai.api_key = LocalConfig.OPEN_AI_KEY
    except:
        openai.api_key = os.environ.get('OPENAI', None)

    await bot.calculate_target_source()
    await bot.start()
    await idle()
    await bot.stop()


if __name__ == "__main__":
    if 'DYNO' in os.environ:
        print('loading wkhtmltopdf path on heroku')
        WKHTMLTOPDF_CMD = subprocess.Popen(
            ['which', os.environ.get('WKHTMLTOPDF_BINARY', 'wkhtmltopdf-pack')],
            # Note we default to 'wkhtmltopdf' as the binary name
            stdout=subprocess.PIPE).communicate()[0].strip()
    else:
        print('loading wkhtmltopdf path on localhost')
        MYDIR = os.path.dirname(__file__)
        WKHTMLTOPDF_CMD = os.path.join(MYDIR + "/static/executables/bin/", "wkhtmltopdf.exe")
    bot = ToolBot()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(bot))
