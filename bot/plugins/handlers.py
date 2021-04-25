import datetime

from textblob import TextBlob
from pyrogram import filters, Client


async def filter_channel(_, __, query):
    hasnt_button = getattr(query, 'reply_markup', None) is None
    isnt_edited = getattr(query, 'edit_date', None) is None
    return query.chat.id in __.source_chats and hasnt_button and isnt_edited


async def check_spam(message):

    message_text = getattr(message, 'text')
    if message_text:
        if message_text.find('t.me/') != -1:
            if message_text.find('https://t.me/joinchat/AAAAAFCg99bpFf62A_f3yA') != -1:
                return False
            return True

    caption = getattr(message, 'caption', None)
    if caption:
        if caption.find('t.me/') != -1:
            if message_text.find('https://t.me/joinchat/AAAAAFCg99bpFf62A_f3yA') != -1:
                return False
            return True

    entities = getattr(message, 'entities', [])
    if not entities:
        entities = getattr(message, 'caption_entities', [])

    if entities:
        for item in entities:
            url = getattr(item, 'url', None)
            if url == 'https://t.me/joinchat/AAAAAFCg99bpFf62A_f3yA':
                continue
            elif url and url.find('t.me/') != -1:
                return True
        return False
    else:
        return False


@Client.on_message(filters.me & filters.command(['rects']))
def recalculate_target_source(client, message):
    client.source_chats = [chat[1] for chat in client.data_source.get_source_chats() if chat[3]]
    client.target_chats = [chat[1] for chat in client.data_source.get_target_chats() if chat[3]]
    

@Client.on_message(filters.channel & filters.create(filter_channel))
async def on_new_post(client, message):
    if not await check_spam(message):
        for chat_id in client.target_chats:
            await client.copy_message(chat_id, message['chat']['id'], message['message_id'])


@Client.on_message(filters.command('lastn') & filters.me)
async def get_new_post(client, message):
    messages = await client.get_history(-1001495650439, limit=2)
    print(messages[0])


