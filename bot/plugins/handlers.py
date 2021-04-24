import datetime

from textblob import TextBlob
from pyrogram import filters, Client

from .chatsids import INSIDER_ID


async def filter_channel(_, __, query):
    hasnt_button = getattr(query, 'reply_markup', None) is None
    isnt_edited = getattr(query, 'edit_date', None) is None
    return query.chat.id in __.source_chats and hasnt_button and isnt_edited


@Client.on_message(filters.me & filters.command(['rects']))
def recalculate_target_source(client, message):
    client.source_chats = [chat[1] for chat in client.data_source.get_source_chats() if chat[3]]
    client.target_chats = [chat[1] for chat in client.data_source.get_target_chats() if chat[3]]
    

@Client.on_message(filters.channel & filters.create(filter_channel))
async def on_new_post(client, message):
    for chat_id in client.target_chats:
        await client.copy_message(chat_id, message['chat']['id'], message['message_id'])


@Client.on_message(filters.command('lastn') & filters.me)
async def get_new_post(client, message):
    messages = await client.get_history(INSIDER_ID, limit=10)
    print(messages)


