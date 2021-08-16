from collections import Iterable

from pyrogram.types import InputMediaDocument, InputMediaAudio, InputMediaPhoto, InputMediaVideo
from pyrogram import filters, Client

media_types = {
    "document": InputMediaDocument,
    "audio": InputMediaAudio,
    "photo": InputMediaPhoto,
    "video": InputMediaVideo
}

duplicate_cache = dict()


async def check_duplicate(chat_id, items):

    if not issubclass(items.__class__, Iterable):
        message_items = set()
        message_items.add(items)
    else:
        message_items = items

    from_cache = duplicate_cache.get(chat_id, set())

    if from_cache and message_items == from_cache:
        return True
    else:
        duplicate_cache.update({chat_id: message_items})
        return False



# async def check_duplicate(chat_id, message):
#     message_text = getattr(message, 'text')
#     from_cache = duplicate_cache.get(chat_id, None)
#     if from_cache and from_cache == message_text:
#         return True
#     else:
#         if from_cache is None:
#             duplicate_cache.update({chat_id: message_text})
#         else:
#             duplicate_cache[chat_id] = message_text
#         return False


async def filter_channel(_, __, query):
    hasnt_button = getattr(query, 'reply_markup', None) is None
    isnt_edited = getattr(query, 'edit_date', None) is None
    return query.chat.id in __.source_chats and hasnt_button and isnt_edited


async def check_spam(message):

    chat = getattr(message, 'chat')

    if chat:
        chat_id = str(getattr(chat, 'id', None))
        chat_username = str(getattr(chat, 'username', None))

    message_text = getattr(message, 'text')
    if message_text:

        if message_text.find('t.me/') != -1 or message_text.find('@') != -1:

            if message_text.find(chat_id) != -1 or message_text.find(chat_username) != -1:
               return False

            if message_text.find('https://t.me/joinchat/AAAAAFCg99bpFf62A_f3yA') != -1:
                return False
            return True

    caption = getattr(message, 'caption', None)
    if caption:
        if caption.find('t.me/') != -1 or caption.find('@') != -1:

            if caption.find(chat_id) != -1 or caption.find(chat_username) != -1:
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
            elif url and (url.find('t.me/') != -1 or url.find('@') != -1):

                if url.find(chat_id) != -1 or url.find(chat_username) != -1:
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
    message_items = set()
    message_items.add(getattr(message, 'text', None))

    if media_group_id:
        if media_group_id != client.last_media_group:
            client.last_media_group = media_group_id
            media_group_to_send = []
            media_group_messages = await client.get_media_group(chat_id, message['message_id'])

            for message in media_group_messages:

                for item, media_class in media_types.items():
                    media_obj = getattr(message, item, None)
                    caption = getattr(message, 'caption', None)
                    message_items.add(caption)

                    if caption and await check_spam(message):
                        return None

                    if media_obj:
                        media_group_to_send.append(
                            media_class(media_obj['file_id'], caption=caption)
                        )

            if await check_duplicate(chat_id, message_items):
                return None

            for chat_id in client.target_chats:
                await client.send_media_group(chat_id, media_group_to_send)
    else:

        if await check_spam(message):
            return None

        if await check_duplicate(chat_id, message_items):
            return None

        for chat_id in client.target_chats:
            await client.copy_message(chat_id, message['chat']['id'], message['message_id'])


@Client.on_message(filters.command('lastn') & filters.me)
async def get_new_post(client, message):
    messages = await client.get_history("insiderUKR", limit=2)



