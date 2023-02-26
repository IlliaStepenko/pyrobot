import os
from io import BytesIO

import imgkit
import datetime
from pathlib import Path

from PIL import Image
from pyrogram.enums import MessageEntityType

kitoptions = {
    "enable-local-file-access": None,
    'width': 410,
    'disable-smart-width': '',
    'encoding': 'utf-8'
}

rules_list = {
    MessageEntityType.BOLD: ['<b>', '</b>'],
    MessageEntityType.ITALIC: ['<i>', '</i>'],
    MessageEntityType.UNDERLINE: ['<u>', '</u>'],
    MessageEntityType.STRIKETHROUGH: ['<s>', '</s>'],
    MessageEntityType.TEXT_LINK: ['<a href="/">', '</a>']
}


def convert_pyrogram_entities_to_rules(entities):
    return [[entity.offset, entity.offset + entity.length, entity.type] for entity in entities]


def format_text(string, format_vals=[], ):
    string = string.replace('\n', '<br>')

    for item in format_vals:
        insertion = string[item[0]: item[1]]
        rule = rules_list.get(item[2], None)
        if rule:
            insertion = rule[0] + insertion + rule[1]
            string = string[:item[0]] + insertion + string[item[1]:]

    return string


def create_sticker_from_message(name, name_color, text, time, reply, entities):
    params = {
        '[name_color]': name_color,
        '[name_text]': name,
        '[message_text]': text,
        '[time_text]': time,
        '[display-reply]': 'block' if reply else 'none',
        '[reply-text]': reply['text'] if reply else None,
        '[reply-name]': reply['name'] if reply else None

    }

    rules = convert_pyrogram_entities_to_rules(entities)

    base_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute().joinpath('assets')

    with open(base_path.joinpath('tmp.html'), 'w+', encoding='utf-8') as tmp:
        with open(base_path.joinpath('index.html'), 'r', encoding='utf-8') as template:
            template_as_string = template.read()

            for k, v in params.items():
                ss = format_text(v, rules) if k == '[message_text]' else v
                if ss:
                    template_as_string = template_as_string.replace(k, ss)

            tmp.write(template_as_string)

    imgkit.from_file(str(base_path.joinpath('tmp.html')), str(base_path.joinpath('out.png')), options=kitoptions)

    os.remove(base_path.joinpath('tmp.html'))

    img = Image.open(base_path.joinpath('out.png'))

    if img.width > img.height:
        new_size = (512, int(img.height * (512 / img.width)))
    else:
        new_size = (int(img.width * (512 / img.height)), 512)
    img = img.resize(new_size, Image.Resampling.LANCZOS)

    image_content = BytesIO()
    img.seek(0)
    img.save(image_content, format='PNG')
    image_content.seek(0)
    return image_content


async def not_me_filter(_, __, m):
    return m.chat.id in (-1001162926553, -1001520738007) and not bool(
        m.from_user and m.from_user.is_self or getattr(m, "outgoing", False))


def make_readable_list(l):
    return ", \n".join(['\t\t\t\t' + str(i) for i in l])


def extract_value(val):
    return val[0] if isinstance(val, tuple) else val


def add_to_my_messages(client, message):
    chat_id = message.chat.id
    if not client.my_messages.get(chat_id, []):
        client.my_messages.update({chat_id: []})
    client.my_messages[chat_id].append(message.id)


async def delete_all(client, message, mode='cch'):
    LIMIT = 50
    offset = 0
    has_messages = True
    chat_id = message.chat.id
    await message.delete()

    if mode == 'srv':
        while has_messages:
            chat_messages = []
            async for message in client.search_messages(chat_id=chat_id, from_user='me', offset=offset, limit=LIMIT):
                chat_messages.append(message.id)
            await client.delete_messages(chat_id=chat_id, message_ids=chat_messages)
            offset += 50
            has_messages = bool(chat_messages)
    else:
        cached_ids = client.my_messages.get(chat_id, [])
        if cached_ids:
            await client.delete_messages(chat_id=chat_id, message_ids=cached_ids)
            if len(client.my_messages.get(chat_id, [])) > 50:
                cached_ids.clear()
        else:
            while has_messages:
                chat_messages = []
                async for message in client.search_messages(chat_id=chat_id, from_user='me', offset=offset,
                                                            limit=LIMIT):
                    chat_messages.append(message.id)
                await client.delete_messages(chat_id=chat_id, message_ids=chat_messages)
                offset += 50
                has_messages = bool(chat_messages)

    result_string = f"Удаление ВСЕХ сообщений из чата {chat_id} в {datetime.datetime.now()}"

    await client.send_message("me", result_string)
