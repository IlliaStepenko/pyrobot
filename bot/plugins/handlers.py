import datetime

from pyrogram.types import InputMediaDocument, InputMediaAudio, InputMediaPhoto, InputMediaVideo
from textblob import TextBlob
from pyrogram import filters, Client

media_types = {
    "document": InputMediaDocument,
    "audio": InputMediaAudio,
    "photo": InputMediaPhoto,
    "video": InputMediaVideo
}


async def filter_channel(_, __, query):
    hasnt_button = getattr(query, 'reply_markup', None) is None
    isnt_edited = getattr(query, 'edit_date', None) is None
    return query.chat.id in __.source_chats and hasnt_button and isnt_edited


async def check_spam(message):

    chat = getattr(message, 'chat')
    if chat:
        chat_id = chat.get('id')
        chat_username = chat.get('username')

    message_text = getattr(message, 'text')
    if message_text:
        if message_text.find('t.me/') != -1 and message_text.find('@') != -1:

            if message_text.find(chat_id) or message_text.find(chat_username):
               return False

            if message_text.find('https://t.me/joinchat/AAAAAFCg99bpFf62A_f3yA') != -1:
                return False
            return True

    caption = getattr(message, 'caption', None)
    if caption:
        if caption.find('t.me/') != -1 and caption.find('@') != -1:

            if caption.find(chat_id) or caption.find(chat_username):
               return False

            if caption.find('https://t.me/joinchat/AAAAAFCg99bpFf62A_f3yA') != -1:
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
            elif url and url.find('t.me/') != -1 and url.find('@') != -1:

                if url.find(chat_id) or url.find(chat_username):
                    return False

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

    chat_id = message['chat']['id']
    media_group_id = getattr(message, 'media_group_id', None)

    if media_group_id:
        if media_group_id != client.last_media_group:
            client.last_media_group = media_group_id
            media_group_to_send = []
            media_group_messages = await client.get_media_group(chat_id, message['message_id'])

            for message in media_group_messages:
                for item, media_class in media_types.items():
                    media_obj = getattr(message, item, None)
                    caption = getattr(message, 'caption', None)

                    if caption and await check_spam(message):
                        return None

                    if media_obj:
                        media_group_to_send.append(
                            media_class(media_obj['file_id'], caption=caption)
                        )

            for chat_id in client.target_chats:
                await client.send_media_group(chat_id, media_group_to_send)
    else:
        if not await check_spam(message):
            for chat_id in client.target_chats:
                await client.copy_message(chat_id, message['chat']['id'], message['message_id'])


@Client.on_message(filters.command('lastn') & filters.me)
async def get_new_post(client, message):
    messages = await client.get_history("insiderUKR", limit=2)
    print(messages[1])


