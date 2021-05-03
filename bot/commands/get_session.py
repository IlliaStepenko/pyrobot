from pyrogram import Client

from bot.local_config import LocalConfig


with Client("my_account", LocalConfig.API_ID, LocalConfig.API_HASH) as app:
    session_string = app.export_session_string()
    config_strings = []
    with open('../local_config.py', 'r') as config_file:
        for line in config_file:
            if line.find('SESSION') > -1:
                config_strings.append(
                   f'    SESSION = "{session_string}" \n'
                )
            else:
                config_strings.append(line)

    with open('../local_config.py', 'w') as config_file:
        for item in config_strings:
            config_file.write(item)