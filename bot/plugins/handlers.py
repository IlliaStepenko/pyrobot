import random
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
    message_items = set()
    if not issubclass(items.__class__, Iterable):
        if items:
            message_items.add(items)
    else:
        message_items = items

    from_cache = duplicate_cache.get(chat_id, set())

    if from_cache == set() and message_items == set():
        return False
    elif message_items == from_cache:
        return True
    else:
        duplicate_cache.update({chat_id: message_items})

    return False


async def filter_channel(_, __, query):
    hasnt_button = getattr(query, 'reply_markup', None) is None
    isnt_edited = getattr(query, 'edit_date', None) is None
    return query.chat.id in __.source_chats and hasnt_button and isnt_edited


async def filter_channel_2(_, __, query):
    hasnt_button = getattr(query, 'reply_markup', None) is None
    isnt_edited = getattr(query, 'edit_date', None) is None
    return query.chat.id in (
        -1001220606936, -1001247449131, -1001098515055, -1001523454586) and hasnt_button and isnt_edited


async def check_spam(chat_id, chat_username, message_text, whitelist=None):
    if whitelist is None:
        whitelist = []

    if message_text.find('t.me/') != -1 or message_text.find('@') != -1:
        for item in whitelist:
            if message_text.find(item) != -1:
                return False

        return not (message_text.find(chat_id) != -1 or message_text.find(chat_username) != -1)


@Client.on_message(filters.me & filters.command(['rects']))
async def recalculate_target_source(client, message):
    config = await client.data_source.get_config()
    config = config[0]
    client.abuser_on = config['abuser_on']
    client.autotranslate = config['autotranslate_lang'] if config['autotranslate'] else None
    client.ask_openai = config['ask_open_ai']
    client.lang_codes = config['used_languages'].replace(' ', '').split(',')
    client.source_chats = [chat[1] for chat in await client.data_source.get_source_chats() if chat[3]]
    client.target_chats = [chat[1] for chat in await client.data_source.get_target_chats() if chat[3]]
    client.whitelist = [item[1].strip() for item in await client.data_source.get_white_list()]
    await message.reply("recalculated")


@Client.on_message(filters.channel & filters.create(filter_channel))
async def on_new_post(client, message):
    if client.send_news:
        chat = getattr(message, 'chat')
        if chat:
            chat_id = str(getattr(chat, 'id', None))
            chat_username = str(getattr(chat, 'username', None))
        else:
            return None

        media_group_id = getattr(message, 'media_group_id', None)
        message_items = set()

        if media_group_id:
            if media_group_id != client.last_media_group:
                client.last_media_group = media_group_id
                media_group_to_send = []
                media_group_messages = await client.get_media_group(chat_id, message.id)

                for message in media_group_messages:

                    for item, media_class in media_types.items():
                        media_obj = getattr(message, item, None)
                        caption = getattr(message, 'caption', None)
                        if caption is not None:
                            message_items.add(caption)

                        if caption and await check_spam(chat_id, chat_username, caption, client.whitelist):
                            return None

                        entities = getattr(message, 'entities', [])

                        if not entities:
                            entities = getattr(message, 'caption_entities', [])

                        if entities:
                            for entity in entities:
                                url = getattr(entity, 'url', None)

                                if url and await check_spam(chat_id, chat_username, url, client.whitelist):
                                    await client.send_message("me", f"block spam in url {url}")  # remove
                                    return None

                        if media_obj:
                            media_group_to_send.append(
                                media_class(media_obj.file_id, caption=caption)
                            )
                if await check_duplicate(chat_id, message_items):
                    await client.send_message("me", f"block duplicate in message_items {str(message_items)}")  # remove
                    return None

                for chat_id in client.target_chats:
                    await client.send_media_group(chat_id, media_group_to_send)
        else:
            message_text = getattr(message, 'text', None)

            caption = getattr(message, 'caption', None)

            if message_text is not None:
                message_items.add(message_text)

            if caption is not None:
                message_items.add(caption)

            caption_entities = getattr(message, 'caption_entities', None)
            if caption_entities is not None:
                for item in caption_entities:
                    caption_url = getattr(item, 'url', None)
                    if caption_url and await check_spam(chat_id, chat_username, caption_url, client.whitelist):
                        await client.send_message("me", f"block spam in caption_entity {caption_url}")  # remove
                        return None

            message_entities = getattr(message, 'entities', None)
            if message_entities is not None:
                for item in message_entities:
                    message_url = getattr(item, 'url', None)
                    if message_url and await check_spam(chat_id, chat_username, message_url, client.whitelist):
                        await client.send_message("me", f"block spam in message entity {message_url}")  # remove
                        return None

            if message_text is not None and await check_spam(chat_id, chat_username, message_text, client.whitelist):
                await client.send_message("me", f"block spam in message_text {message_text}")  # remove
                return None

            if caption is not None and await check_spam(chat_id, chat_username, caption, client.whitelist):
                await client.send_message("me", f"block spam in caption {caption}")  # remove
                return None

            if await check_duplicate(chat_id, message_items):
                await client.send_message("me", f"block duplicate in message_text {message_text}")  # remove
                return None

            for chat_id in client.target_chats:
                await client.copy_message(chat_id, message.chat.id, message.id)


@Client.on_message(filters.channel & filters.create(filter_channel_2))
async def on_new_post_two(client, message):
    await client.forward_messages(-1001140635421, from_chat_id=message.chat.id, message_ids=message.id)
