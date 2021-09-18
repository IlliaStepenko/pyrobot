import datetime
import os
import io
import sys
from textblob import TextBlob
from pyrogram import filters, Client

command_last_used = None

LANGUAGE_CODES = ['ru', 'en']


@Client.on_message(filters.command('check') & filters.me & filters.chat("me"))
async def check(client, message):
    await message.reply("Helloooooo")


@Client.on_message(filters.command('tukan') )
async def det_tukan(client, message):
    tukan_id = 303701321
    tukan = await client.get_users(tukan_id)
    await message.reply('@'+tukan['username'])


@Client.on_message(filters.command('dall') & filters.me & ~filters.chat("me"))
async def delete_all_message(client, message):
    LIMIT = 50

    offset = 0

    has_messages = True

    chat_id = message['chat']['id']

    await message.delete()

    while has_messages:

        chat_messages = []

        async for message in client.search_messages(chat_id=chat_id, from_user='me', offset=offset, limit=LIMIT):
            chat_messages.append(message['message_id'])

        await client.delete_messages(chat_id=chat_id, message_ids=chat_messages)

        offset += 50

        has_messages = bool(chat_messages)

    result_string = f"Удаление ВСЕХ сообщений из чата {chat_id} в {datetime.datetime.now()}"

    await client.send_message("me", result_string)


@Client.on_message(filters.command('py') & filters.me)
async def run_python(client, message):

    python_text = message['text'].replace('/py', '')

    old_buffer = sys.stdout
    try:
        sys.stdout = new_buffer = io.StringIO()
        print(f"code: \n{python_text}\n")
        print("\nresult\n")
        exec(python_text, globals())
        sys.stdout = old_buffer
        await client.edit_message_text( message['chat']['id'], message['message_id'], new_buffer.getvalue())
    except Exception as e:
        sys.stdout = old_buffer
        await client.edit_message_text(message['chat']['id'], message['message_id'], str(e))


@Client.on_message(filters.command(LANGUAGE_CODES) & filters.me)
async def translate_message(client, message):
    lang = message['command'][0]
    if len(message['command']) > 1:

        to_translate = " ".join(message['command'][1:])
        translated = "translating_error"
        try:
            translator = TextBlob(to_translate)
            translated = translator.translate(to=lang)
        except Exception as e:
            translated = str(e)

        await client.edit_message_text(
            message['chat']['id'], message['message_id'], translated)

    elif getattr(message, 'reply_to_message', None):
        reply = message['reply_to_message']
        message_text = getattr(reply, 'text', None)
        if message_text:
            translated = "translating_error"
            try:
                translator = TextBlob(message_text)
                translated = translator.translate(to=lang)
            except Exception as e:
                translated = str(e)

            await client.edit_message_text(
                message['chat']['id'], message['message_id'], translated)


@Client.on_message(filters.command('vanvirgin'))
async def get_ivans_virginity(client, message):

    global command_last_used

    if command_last_used is None \
            or bool((datetime.datetime.now() - command_last_used).seconds > 60) \
            or bool(message.from_user and message.from_user.is_self):


        today = datetime.datetime.today().date()
        vanya_brth = datetime.date(today.year - 29, 4, 2)
        msg_text = f"Ваня без секса {(today - vanya_brth).days} дней"

        if bool(message.from_user and message.from_user.is_self):
            await client.edit_message_text(
                message['chat']['id'], message['message_id'], msg_text)
        else:
            command_last_used = datetime.datetime.now()
            await message.reply(msg_text)