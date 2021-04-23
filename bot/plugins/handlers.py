import datetime

from textblob import TextBlob
from pyrogram import filters, Client

from .chatsids import SOURCE_CHATS, TARGET_CHATS, INSIDER_ID


async def filter_channel(_, __, query):

    hasnt_button = getattr(query, 'reply_markup', None) is None
    isnt_edited = getattr(query, 'edit_date', None) is None
    print(__.source_chats)
    return query.chat.id in __.source_chats and hasnt_button and isnt_edited


@Client.on_message(filters.me & filters.command(['stopfromsource']))
async def stop_send_from_chat(client, message):
    if len(message['command']) > 1:
        chat_id = int(message['command'][1])
        if chat_id in client.source_chats:
            client.source_chats.remove(chat_id)


@Client.on_message(filters.me & filters.command(['addsource']))
async def start_send_from_chat(client, message):
    if len(message['command']) > 1:
        chat_id = int(message['command'][1])
        if chat_id in client.source_chats:
            client.source_chats.append(chat_id)


@Client.on_message(filters.channel & filters.create(filter_channel))
async def on_new_post(client, message):
    for chat_id in client.target_chats:
        await client.forward_messages(chat_id, message['chat']['id'], message['message_id'])


@Client.on_message(filters.command('lastn') & filters.me)
async def get_new_post(client, message):
    messages = await client.get_history(INSIDER_ID, limit=1)
    for chat_id in client.target_chats:
        await client.forward_messages(chat_id, INSIDER_ID, messages[0]['message_id'])
