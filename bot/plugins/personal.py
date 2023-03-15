import io
import os
import random
import shutil
import sys
import json
import asyncio
from datetime import timedelta
from pathlib import Path

from emoji import unicode_codes
from gtts import gTTS
from io import BytesIO

from pilmoji import Pilmoji
from pyrogram import filters, Client
from pyrogram import enums
from pyrogram.enums import MessageEntityType
from PIL import Image, ImageOps, ImageFont
from pyrogram.raw.functions.messages import SendMedia
from pyrogram.raw.types import InputMediaGeoLive, InputGeoPoint, MessageMediaGeoLive

from .utils import add_to_my_messages, delete_all, extract_value, make_readable_list, not_me_filter, \
    create_html_repr_of_message, create_sticker_from_messages

not_me = filters.create(not_me_filter)


@Client.on_message(filters.me)
async def catch_message_id(client, message):
    add_to_my_messages(client, message)
    is_command = any([m.type == MessageEntityType.BOT_COMMAND for m in message.entities]) if hasattr(message,
                                                                                                     'entities') and message.entities else False
    if not is_command and client.autotranslate and client.autotranslate in client.lang_codes:
        try:
            translation = client.translator.translate(message.text, src='ru', dest=client.autotranslate).text
            await client.edit_message_text(message.chat.id, message.id, translation)
        except:
            pass
        message.stop_propagation()

    message.continue_propagation()


@Client.on_message(filters.command('check') & filters.me & filters.chat("me"))
async def check(client, message):
    await message.reply("Helloooooo")


@Client.on_message(filters.command('dall') & filters.me)
async def delete_all_message(client, message):
    message_commands = message.command
    if len(message_commands) > 1 and message_commands[1] == 'srv':
        mode = 'srv'
    else:
        mode = 'cch'

    await delete_all(client, message, mode)


@Client.on_message(filters.command('py') & filters.me)
async def run_py(client, message):
    python_text = message.text.replace('/py', '')

    old_buffer = sys.stdout
    try:
        sys.stdout = new_buffer = io.StringIO()
        print(f"code: \n ```{python_text}```\n")
        print("\nresult\n")
        exec(python_text, globals())
        sys.stdout = old_buffer
        await client.edit_message_text(
            message.chat.id, message.id, new_buffer.getvalue(), parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        sys.stdout = old_buffer
        await client.edit_message_text(message.chat.id, message.id, str(e))


@Client.on_message(filters.command('abuser') & filters.me)
async def abuser(client, message):
    client.abuser_on = not client.abuser_on
    await message.reply(f"abuser {'disabled' if not client.abuser_on else 'enabled'}")


@Client.on_message(not_me)
async def answer(client, message):
    if client.ask_openai and message.text and message.reply_to_message and message.reply_to_message.from_user.id == 654009330:
        answer = client.ai.create(
            model="text-davinci-003",
            prompt=message.text,
            temperature=0.5,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.5
        )

        await message.reply(answer['choices'][0]['text'])


@Client.on_message(filters.command('ai') & filters.me)
async def ai(client, message):
    answer = client.ai.create(
        model=extract_value(client.nn_model),
        prompt=message.text,
        temperature=extract_value(client.temperature),
        max_tokens=extract_value(client.max_tokens),
        top_p=extract_value(client.top_p),
        frequency_penalty=extract_value(client.frequency_penalty),
        presence_penalty=extract_value(client.presence_penalty)
    )

    await message.reply(answer['choices'][0]['text'])


@Client.on_message(filters.command('sv') & filters.me)
async def send_voice(client, message):
    await message.delete()
    await client.send_chat_action(message.chat.id, enums.ChatAction.RECORD_AUDIO)
    await asyncio.sleep(3)
    to_speech = message.text.replace('/sv', '')
    if not to_speech:
        to_speech = 'Мне нечего сказать'

    mp3_fp = BytesIO()
    tts = gTTS(to_speech, lang='ru')
    tts.write_to_fp(mp3_fp)
    setattr(mp3_fp, 'name', 'vvoice')
    await client.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)
    if message.reply_to_message:
        msg = await client.send_voice(message.chat.id, mp3_fp, reply_to_message_id=message.reply_to_message.id)
    else:
        msg = await client.send_voice(message.chat.id, mp3_fp)

    if msg:
        add_to_my_messages(client, msg)


@Client.on_message(filters.command('tr') & filters.me)
async def translate_message(client, message):
    command_len = len(message.command)
    from_lang = message.command[1]

    if from_lang not in client.lang_codes:
        message.reply(f"language {from_lang} not recognized")

    try:
        translation = ''
        if command_len > 3:
            to_lang = message.command[2]
            if to_lang not in client.lang_codes:
                message.reply(f"language {to_lang} not recognized")

            text = message.text.replace('/', '').replace(from_lang, '').replace(to_lang, '').replace('tr', '')
            translation = client.translator.translate(text, src=from_lang, dest=to_lang).text
        elif message.reply_to_message and command_len == 3:
            to_lang = message.command[2]
            translation = client.translator.translate(message.reply_to_message.text, src=from_lang, dest=to_lang).text

        await client.edit_message_text(message.chat.id, message.id, translation)

    except Exception as e:
        pass


@Client.on_message(filters.command('autotranslate') & filters.me)
async def autotranslate(client, message):
    if len(message.command) > 1:
        lang = message.command[1]
        if message.command[1] in client.lang_codes:
            client.autotranslate = lang
            msg = await message.reply(f"translation to {lang} enabled")
        else:
            msg = await message.reply(f"lang {lang} not supported")
    else:
        client.autotranslate = None
        msg = await message.reply("translation disabled")

    add_to_my_messages(client, msg)


@Client.on_message(filters.command('info') & filters.me)
async def send_info(client, message):
    info_msg = str(message)

    cnt = len(info_msg) // 4000
    await client.send_message("me", info_msg[0:4000])

    for i in range(1, cnt - 1):
        await client.send_message("me", info_msg[i * 4000:(i + 1) * 4000])

    await client.send_message("me", info_msg[cnt * 4000:])


@Client.on_message(filters.command('openai') & filters.me)
async def ask_openai(client, message):
    client.ask_openai = not client.ask_openai
    msg = await message.reply(f"OpenAI {'enabled' if client.ask_openai else 'disabled'}")
    add_to_my_messages(client, msg)


async def get_config(client, message):
    result = 'ConfigList:\n\n'
    result += f"\t\t\t\tabuser_on: {extract_value(client.abuser_on)}\n"
    result += f"\t\t\t\tautotranslate: {extract_value(client.autotranslate)}\n"
    result += f"\t\t\t\task_openai: {extract_value(client.ask_openai)}\n"
    result += f"\t\t\t\ttarget_stickerpack: {extract_value(client.target_stickerpack)}\n"
    result += f"\t\t\t\tlang_codes: {', '.join(client.lang_codes)}\n"

    result += f"\t\t\t\tnn_model: {extract_value(client.nn_model)}\n"
    result += f"\t\t\t\ttemperature: {extract_value(client.temperature)}\n"
    result += f"\t\t\t\tmax_tokens: {extract_value(client.max_tokens)}\n"
    result += f"\t\t\t\ttop_p: {extract_value(client.top_p)}\n"
    result += f"\t\t\t\tfrequency_penalty: {extract_value(client.frequency_penalty)}\n"
    result += f"\t\t\t\tpresence_penalty: {extract_value(client.presence_penalty)}\n"

    result += "\n\n"
    result += f'Source chats: [\n{make_readable_list(client.source_chats)}\n]'
    result += "\n\n"
    result += f'Target chats: [\n{make_readable_list(client.target_chats)}\n]'
    result += "\n\n"
    result += f'White list: [\n{make_readable_list(client.whitelist)}\n]'
    msg = await message.reply(result, disable_web_page_preview=True)
    add_to_my_messages(client, msg)


@Client.on_message(filters.command('get_config') & filters.me)
async def get_config_c(client, message):
    await get_config(client, message)


@Client.on_message(filters.command('set_ai_config') & filters.me)
async def set_config(client, message):
    text = "{" + message.text.replace('/set_ai_config', '') + "}"
    try:
        dct = json.loads(text)
    except Exception as e:
        await message.reply(str(e))

    for k, v in dct.items():
        if hasattr(client, k):
            setattr(client, k, v)

    await get_config(client, message)


@Client.on_message(filters.command('create_sticker') & filters.me)
async def cc_sticker(client, message):
    messages = []

    if '-l' in message.text:
        message_dict = {}
        messages_order = []
        message_text = message.text.replace('/create_sticker', '').replace('-l', '').strip().split('\n')

        for link in message_text:
            c_index = link.find('/c/')
            chat_message_ids = [int('-100' + entity_id) if i == 0 else int(entity_id) for i, entity_id in
                                enumerate(link[c_index + 3:].split('/'))]
            messages_order.append(chat_message_ids)

            tmp = message_dict.setdefault(chat_message_ids[0], [chat_message_ids[1]])

            if chat_message_ids[1] not in tmp:
                tmp.append(chat_message_ids[1])

        messages = []

        for chat_id, message_id_list in message_dict.items():
            messages.extend(await client.get_messages(chat_id, message_id_list))

        tmp = []

        for item in messages_order:
            for m in messages:
                if m.chat.id == item[0] and m.id == item[1]:
                    tmp.append(m)

        messages = tmp

    else:
        message_r = await client.get_messages(message.chat.id, message_ids=[message.reply_to_message.id])
        messages.extend(message_r)
    try:
        img = await create_sticker_from_messages(client, messages)
        await client.send_sticker(message.chat.id, img, reply_to_message_id=message.id)
    finally:
        folder = str(Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute().joinpath('tmp'))
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


@Client.on_message(filters.command('add_sticker') & filters.me)
async def add_sticker_to_me(client, message):
    if not message.reply_to_message:
        await message.reply("You must reply message for create sticker")
        return

    e = list(unicode_codes.get_emoji_unicode_dict('en').values())
    await client.send_message("Stickers", '/addsticker')
    await asyncio.sleep(0.3)
    await client.send_message("Stickers", client.target_stickerpack)
    await asyncio.sleep(0.3)
    if message.reply_to_message.text is None and (message.reply_to_message.photo or (
            message.reply_to_message.animation and message.reply_to_message.animation.thumbs)):
        file_id = message.reply_to_message.photo.file_id if message.reply_to_message.photo else \
            message.reply_to_message.animation.thumbs[0].file_id

        file = await client.download_media(file_id, in_memory=True)
        image = Image.open(file)
        image_content = BytesIO()

        if image.width > image.height:
            new_size = (512, int(image.height * (512 / image.width)))
        else:
            new_size = (int(image.width * (512 / image.height)), 512)
        image = image.resize(new_size, Image.Resampling.LANCZOS)

        image.seek(0)
        image.save(image_content, format='PNG')
        image_content.seek(0)
        image_content.name = 'test123'
        await client.send_sticker("Stickers", image_content)
    else:
        await client.forward_messages(chat_id="Stickers", from_chat_id=message.reply_to_message.chat.id,
                                      message_ids=[message.reply_to_message.id])
    await asyncio.sleep(0.3)
    await client.send_message("Stickers", e[random.randint(0, len(e))])

    await message.reply("Added")


@Client.on_message(filters.command('set_fake_geo') & filters.me)
async def set_fake_geo(client, message):
    lat, long = 0, 0
    if len(message.command) == 3:
        lat, long = float(message.command[1]), float(message.command[2])
    elif len(message.command) == 2 and message.command[1] == 'def':
        lat, long = client.my_def_lat, client.my_def_long

    client.my_lat = lat
    client.my_long = long
    await message.reply(f"your new cord ({lat},{long})")


@Client.on_message(filters.command('fake_geo') & filters.me)
async def send_geo(client, message):
    commands = message.command

    send_media_params = {}
    chat_id = -1001520738007
    if len(commands) == 2:
        chat_id = int(commands[1])
    elif len(commands) == 3:
        chat_id = int(commands[1])
        send_media_params.update({'reply_to_msg_id': int(commands[2])})

    gp = InputGeoPoint(lat=client.my_lat, long=client.my_long)
    d = InputMediaGeoLive(geo_point=gp, stopped=False, period=900)
    peer = await client.resolve_peer(chat_id)
    await client.invoke(
        SendMedia(
            peer=peer,
            message='',
            random_id=random.randint(1, 5000),
            media=d,
            **send_media_params
        )
    )
