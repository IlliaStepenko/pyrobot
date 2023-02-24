import os
import textwrap
import datetime
import emoji
from io import BytesIO
from pathlib import Path
from PIL import ImageDraw, ImageFont, ImageOps, Image
from emoji import unicode_codes

from pilmoji import Pilmoji


def draw_time(image, text_time, font, offset_x=0, offset_y=0):
    draw = ImageDraw.Draw(image)
    draw.text((image.width - 110, image.height - 35), text_time, '#a0a3a1', font)


def draw_name(image, name, font, offset_x=0, offset_y=0):
    with Pilmoji(image) as pilmoji:
        pilmoji.text((35 + offset_x, 25 + offset_y), name, '#36c91c', font=font)


def draw_text(image, font, offset_x=0, offset_y=0, text=''):
    with Pilmoji(image) as pilmoji:
        for i, line in enumerate(text):
            pilmoji.text((offset_x + 35, 35 + 28 * (i + 1)), line, 'black', font=font, emoji_position_offset=(0, 0))


def prepare_text(text):
    d = []
    lines = text.split('\n')
    for line in lines:

        if line == '':
            d.append('\n')
        else:
            d.extend(textwrap.wrap(line, width=30))
    return d


def create_sticker(first_name, last_name, text, date, avatar=None):
    OFFSET_X = 55
    OFFSET_Y = 0

    str_date = date.strftime('%H:%M')

    username = ''
    username = username + first_name if first_name else username
    username = username + ' ' + last_name if last_name else username

    base_image_path = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute().joinpath('assets')
    background_filename = base_image_path.joinpath('background.png')
    footer_filename = base_image_path.joinpath('template_footer.png')
    header_filename = base_image_path.joinpath('template_head.png')
    body_filename = base_image_path.joinpath('template_body.png')
    rounded_filename = base_image_path.joinpath('rounded.png')
    font_path = base_image_path.joinpath('microsoftsansserif.ttf')
    font = ImageFont.truetype(str(font_path), 24, encoding="unic")
    time_font = ImageFont.truetype(str(font_path), 18, encoding="unic")

    message_text = prepare_text(text)
    img_hght = (len(message_text) + 1) * 26 if len(message_text) > 1 else 40

    header = Image.open(header_filename).convert("RGBA")
    footer = Image.open(footer_filename).convert("RGBA")
    background = Image.open(background_filename).convert("RGBA")
    body = Image.open(body_filename).convert("RGBA").resize((header.width + 2, img_hght), Image.Resampling.LANCZOS)
    mask = Image.open(rounded_filename).convert('L')

    if avatar:
        avatar_img = Image.open(avatar).convert('RGBA')

    else:
        avatar_img = Image.new('RGBA', (50, 50), color="#36c91c")
        with Pilmoji(avatar_img) as pilmoji:
            pilmoji.text((12, 14), first_name[0] + last_name[0], 'white', font=font)

    output = ImageOps.fit(avatar_img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    output = output.resize((50, 50), Image.Resampling.LANCZOS)

    result_img = Image.new('RGBA', (512, 90 + img_hght))
    result_img.paste(background)

    result_img.paste(header, (7 + OFFSET_X, 10), mask=header)
    result_img.paste(body, (6 + OFFSET_X, 40), mask=body)
    result_img.paste(footer, (0 + OFFSET_X, result_img.height - 75), mask=footer)

    draw_name(result_img, username, font=font, offset_x=OFFSET_X, offset_y=OFFSET_Y)
    draw_text(result_img, font=font, offset_x=OFFSET_X, text=message_text)
    draw_time(result_img, font=time_font, text_time=str_date)
    result_img.paste(output, (10, result_img.height - 65), mask=output)

    result_img.resize((512, 512), Image.Resampling.LANCZOS)

    image_content = BytesIO()
    result_img.seek(0)
    result_img.save(image_content, format='PNG')
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
