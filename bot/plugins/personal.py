import datetime
import os
import io
import sys
from textblob import TextBlob
from pyrogram import filters, Client

command_last_used = None

LANGUAGE_CODES = ['ru', 'en', 'pl']


@Client.on_message(filters.command('check') & filters.me & filters.chat("me"))
async def check(client, message):
    await message.reply("Helloooooo")


@Client.on_message(filters.command('tukan') )
async def det_tukan(client, message):
    tukan_id = 303701321
    tukan = await client.get_users(tukan_id)
    await message.reply('@'+tukan['username'])


@Client.on_message(filters.command('dall') & filters.me)
async def delete_all_message(client, message):
    LIMIT = 50

    offset = 0

    has_messages = True

    chat_id = message.chat.id

    await message.delete()

    while has_messages:

        chat_messages = []

        async for message in client.search_messages(chat_id=chat_id, from_user='me', offset=offset, limit=LIMIT):
            chat_messages.append(message.id)

        await client.delete_messages(chat_id=chat_id, message_ids=chat_messages)

        offset += 50

        has_messages = bool(chat_messages)

    result_string = f"Удаление ВСЕХ сообщений из чата {chat_id} в {datetime.datetime.now()}"

    await client.send_message("me", result_string)


@Client.on_message(filters.command('py') & filters.me)
async def run_python(client, message):

    python_text = message.text.replace('/py', '')

    old_buffer = sys.stdout
    try:
        sys.stdout = new_buffer = io.StringIO()
        print(f"code: \n{python_text}\n")
        print("\nresult\n")
        exec(python_text, globals())
        sys.stdout = old_buffer
        await client.edit_message_text(message.chat.id, message.id, new_buffer.getvalue())
    except Exception as e:
        sys.stdout = old_buffer
        await client.edit_message_text(message.chat.id, message.id, str(e))


@Client.on_message(filters.command(LANGUAGE_CODES) & filters.me)
async def translate_message(client, message):

    from_lang = message.command[0]
    to_lang = message.command[1]


    if len(message.command) > 2:

        to_translate = " ".join(message.command[2:])
        translated = "translating_error"
        try:
            translator = TextBlob(to_translate)
            translated = translator.translate(from_lang=from_lang, to=to_lang)
        except Exception as e:
            translated = str(e)

        await client.edit_message_text(
            message.chat.id, message.id, translated)

    elif getattr(message, 'reply_to_message', None):
        reply = message.reply_to_message
        message_text = getattr(reply, 'text', None)
        if message_text:
            translated = "translating_error"
            try:
                translator = TextBlob(message_text)
                translated = translator.translate(from_lang=from_lang, to=to_lang)
            except Exception as e:
                translated = str(e)

            await client.edit_message_text(
                message.chat.id, message.id, translated)
