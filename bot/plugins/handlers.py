import datetime

from textblob import TextBlob
from pyrogram import filters, Client

from .chatsids import SOURCE_CHATS, TARGET_CHATS, INSIDER_ID


async def filter_channel(_, __, query):

    hasnt_button = getattr(query, 'reply_markup', None) is None
    isnt_edited = getattr(query, 'edit_date', None) is None

    return query.chat.id == SOURCE_CHATS and hasnt_button and isnt_edited


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


@Client.on_message(filters.command(['en', 'ru']) & filters.me)
async def translate_message(client, message):
    if len(message['command']) > 1:

        lang = message['command'][0]

        to_translate = " ".join(message['command'][1:])

        translated = "translating_error"
        try:
            translator = TextBlob(to_translate)
            translated = translator.translate(to=lang)
        except:
            pass

        await client.edit_message_text(
            message['chat']['id'], message['message_id'], translated)


@Client.on_message(filters.channel & filters.create(filter_channel))
async def on_new_post(client, message):
    async for chat_id in TARGET_CHATS:
        await client.forward_messages(chat_id, INSIDER_ID, message['message_id'])


@Client.on_message(filters.command('lastn') & filters.me)
async def get_new_post(client, message):
    messages = await client.get_history(INSIDER_ID, limit=1)
    for chat_id in TARGET_CHATS:
        await client.forward_messages(chat_id, INSIDER_ID, messages[0]['message_id'])
