import os
from io import BytesIO

import imgkit
import datetime
from pathlib import Path
from datetime import timedelta
from PIL import Image, ImageOps
from PIL import ImageFont
from pilmoji import Pilmoji
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
    MessageEntityType.TEXT_LINK: ['<a href="/">', '</a>'],
    MessageEntityType.MENTION: ['<span style="color:#2ea3d9">', '</span>'],
    MessageEntityType.BOT_COMMAND: ['<span style="color:#2ea3d9">', '</span>']
}


def convert_pyrogram_entities_to_rules(entities):
    return [[entity.offset, entity.offset + entity.length, entity.type] for entity in entities]


def format_text(string, format_vals=[], ):
    string = string.replace('\n', '<br>')
    result = ''
    prev_ind = 0
    for item in format_vals:
        insertion = string[item[0]: item[1]]
        rule = rules_list.get(item[2], None)
        if rule:
            insertion = rule[0] + insertion + rule[1]

        result += string[prev_ind: item[0]] + insertion
        prev_ind = item[1]

    result += string[prev_ind:]

    return result


async def create_html_repr_of_message(client, message, i, hide_name=False, show_avatar=False):
    base_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute().joinpath('assets')
    tmp_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute().joinpath('tmp')
    result = ''

    with open(base_path.joinpath('message_template.html'), 'r', encoding='utf-8') as template:
        result = template.read()
        if message.text or message.caption:
            message_text = ''

            if message.text is not None:
                message_text = message.text
            elif message.caption is not None:
                message_text = message.caption

            message_text = format_text(message_text,
                                       convert_pyrogram_entities_to_rules(message.entities if message.entities else []))

            result = result.replace('[display-message-text]', 'block').replace('[message-text]', message_text)
        else:
            result = result.replace('[display-message-text]', 'none')

        if message.sticker or message.photo:

            file_id = None
            if message.sticker:
                file_id = message.sticker.file_id
            elif message.photo:
                file_id = message.photo.file_id

            if file_id:
                file = await client.download_media(file_id, in_memory=True)
                inner_image = Image.open(file).convert('RGBA')
                path_d = tmp_path.joinpath(f'inner_sticker_msg_{i}.png')

                inner_image.save(path_d)
                result = result.replace('[message-image]',
                                        str(path_d)).replace(
                    '[display-message-image]', 'block')


        else:
            result = result.replace('[display-message-image]', 'none').replace('[message-image]', '')

        r_text = 'Фотография'

        if message.reply_to_message and message.reply_to_message.from_user:
            reply_to_name = ''
            if message.reply_to_message.from_user.first_name:
                reply_to_name += message.reply_to_message.from_user.first_name

            if message.reply_to_message.from_user.last_name:
                reply_to_name += message.reply_to_message.from_user.last_name

            result = result.replace('[reply-name]', reply_to_name)

            if message.reply_to_message.photo or message.reply_to_message.sticker:

                file_id = ''
                if message.reply_to_message.photo is not None:

                    if hasattr(message.reply_to_message.photo, 'small_file_id'):
                        file_id = message.reply_to_message.photo.small_file_id

                    if hasattr(message.reply_to_message.photo, 'file_id'):
                        file_id = message.reply_to_message.photo.file_id

                elif message.reply_to_message.sticker is not None:
                    file_id = message.reply_to_message.sticker.file_id

                reply_min_img = await client.download_media(file_id, in_memory=True)
                if reply_min_img:
                    reply_img = Image.open(reply_min_img).convert('RGBA')
                    path = tmp_path.joinpath(f'reply_{i}.png')
                    reply_img.save(path)
                    result = result.replace('[reply-image]', str(path))
                    result = result.replace('[display-reply-image]', 'block')
                    if message.reply_to_message.caption is None:
                        result = result.replace('[reply-text]', r_text)


            else:
                result = result.replace('[display-reply-image]', 'none').replace('[reply-image]', '')

            if message.reply_to_message.text or message.reply_to_message.caption:
                r_text = message.reply_to_message.text or message.reply_to_message.caption
                r_text = r_text.replace('\n', ' ')[:25]
                r_text = r_text if len(r_text) < 25 else r_text + '...'
                result = result.replace('[reply-text]', r_text)
                result = result.replace('[display-reply-image]', 'block')

            else:
                result = result.replace('[reply-text]', '')

        else:
            result = result.replace('[display-reply-image]', 'none').replace('[reply-image]', '').replace(
                '[display-reply]', 'none')

        username = ''
        if not hide_name:
            if message.from_user and message.from_user.first_name:
                username += message.from_user.first_name

            if message.from_user and message.from_user.last_name:
                username += ' ' + message.from_user.last_name

        if not show_avatar:
            result = result.replace('comment_bubble', 'comment_bubble-without-before').replace('[avatar-img]', '')

        else:
            user_avatar_photo = message.from_user.photo

            user_avatar = None
            if user_avatar_photo:
                user_avatar = await client.download_media(message.from_user.photo.small_file_id,
                                                          in_memory=True)

            if user_avatar:
                avatar_img = Image.open(user_avatar).convert('RGBA')

            else:
                avatar_img = Image.new('RGBA', (50, 50), color="#36c91c")
                font = ImageFont.truetype(str(base_path.joinpath('microsoftsansserif.ttf')), 24, encoding="unic")

                gl = ''

                if message.from_user.first_name is not None:
                    gl += message.from_user.first_name[0]

                if message.from_user.last_name is not None:
                    gl += message.from_user.last_name[0]

                with Pilmoji(avatar_img) as pilmoji:
                    pilmoji.text((12, 12), gl, 'white', font=font)
            mask = Image.open(base_path.joinpath('rounded.png')).convert('L')
            output = ImageOps.fit(avatar_img, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            output = output.resize((50, 50), Image.Resampling.LANCZOS)
            output.save(tmp_path.joinpath(f'avatar_tmp_{i}.png'))
            result = result.replace('[avatar-img]', str(tmp_path.joinpath(f'avatar_tmp_{i}.png')))

        result = result.replace('[name_text]', username)
        result = result.replace('[time-text]', (message.date + timedelta(hours=2)).strftime("%H:%M"))

    return result


async def create_sticker_from_messages(client, messages):
    base_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute().joinpath('assets')
    tmp_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute().joinpath('tmp')

    with open(base_path.joinpath('root_template.html'), 'r', encoding='utf-8') as template:
        base_template = template.read()
        result = ''
        for i, message in enumerate(messages):
            r = await create_html_repr_of_message(client, message, i, i != 0, len(messages) == i + 1)
            result += '\n' + r

        result = base_template.replace('[sticker-body]', result)

        with open(tmp_path.joinpath('out.html'), 'w+', encoding='utf-8') as out:
            out.write(result)

        imgkit.from_file(str(tmp_path.joinpath('out.html')), str(tmp_path.joinpath('out.png')), options=kitoptions)
        img = Image.open(tmp_path.joinpath('out.png'))

        if img.width > img.height:
            new_size = (512, int(img.height * (512 / img.width)))
        else:
            new_size = (int(img.width * (512 / img.height)), 512)
        img = img.resize(new_size, Image.Resampling.LANCZOS)

        image_content = BytesIO()
        img.seek(0)
        img.save(image_content, format='PNG')
        image_content.seek(0)
        image_content.name = 'sticker'
        return image_content

    return '', []


async def not_me_filter(_, __, m):
    return m.chat.id in (-1002140296565,) and not bool(
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
