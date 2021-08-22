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
        if items:
            message_items.add(items)
    else:
        message_items = items

    from_cache = duplicate_cache.get(chat_id, set())

    if message_items == from_cache:
        return True
    else:
        duplicate_cache.update({chat_id: message_items})
    return False


async def filter_channel(_, __, query):
    hasnt_button = getattr(query, 'reply_markup', None) is None
    isnt_edited = getattr(query, 'edit_date', None) is None
    return query.chat.id in __.source_chats and hasnt_button and isnt_edited


async def check_spam(chat_id, chat_username, message_text):
    if message_text.find('t.me/') != -1 or message_text.find('@') != -1:
        return not(message_text.find(chat_id) != -1 or message_text.find(chat_username) != -1)


@Client.on_message(filters.me & filters.command(['rects']))
def recalculate_target_source(client, message):
    client.source_chats = [chat[1] for chat in client.data_source.get_source_chats() if chat[3]]
    client.target_chats = [chat[1] for chat in client.data_source.get_target_chats() if chat[3]]
    

@Client.on_message(filters.channel & filters.create(filter_channel))
async def on_new_post(client, message):
    chat = getattr(message, 'chat')
    if chat:
        chat_id = str(getattr(chat, 'id', None))
        chat_username = str(getattr(chat, 'username', None))
    else:
        return None

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

                    if caption and await check_spam(chat_id, chat_username, caption):
                        return None

                    entities = getattr(message, 'entities', [])

                    if not entities:
                        entities = getattr(message, 'caption_entities', [])

                    if entities:
                        for entity in entities:
                            url = getattr(entity, 'url', None)

                            if url and await check_spam(chat_id, chat_username, url):
                                await client.send_message("me", f"block spam in url {url}")  # remove
                                return None

                    if media_obj:
                        media_group_to_send.append(
                            media_class(media_obj['file_id'], caption=caption)
                        )
            if await check_duplicate(chat_id, message_items):
                await client.send_message("me", f"block duplicate in message_items {str(message_items)}") # remove
                return None

            for chat_id in client.target_chats:
                await client.send_media_group(chat_id, media_group_to_send)
    else:

        message_text = getattr(message, 'text', None)
        if message_text and await check_spam(chat_id, chat_username, message_text):
            await client.send_message("me", f"block spam in message_text {message_text}") # remove
            return None

        if await check_duplicate(chat_id, message_items):
            await client.send_message("me", f"block duplicate in message_text {message_text}") # remove
            return None

        for chat_id in client.target_chats:
            await client.copy_message(chat_id, message['chat']['id'], message['message_id'])


@Client.on_message(filters.command('lastn') & filters.me)
async def get_new_post(client, message):
    messages = await client.get_history("insiderUKR", limit=2)



