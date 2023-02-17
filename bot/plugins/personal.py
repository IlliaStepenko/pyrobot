from pyrogram.enums import MessageEntityType
from gtts import gTTS
from io import BytesIO
import asyncio
import datetime
import random
import io
import sys
from pyrogram import filters, Client
from pyrogram import enums

command_last_used = None
LAN_CODES = ["en", "ru", "pl", "uk", "de", "it"]


def add_to_my_messages(client, message):
    chat_id = message.chat.id
    if not client.my_messages.get(chat_id, []):
        client.my_messages.update({chat_id: []})
    client.my_messages[chat_id].append(message.id)


async def not_me_filter(_, __, m):
    return m.chat.id == -1001162926553 and not bool(
        m.from_user and m.from_user.is_self or getattr(m, "outgoing", False))


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


@Client.on_message(filters.me)
async def catch_message_id(client, message):
    add_to_my_messages(client, message)
    is_command = any([m.type == MessageEntityType.BOT_COMMAND for m in message.entities]) if hasattr(message,
                                                                                                     'entities') and message.entities else False
    if not is_command and client.autotranslate and client.autotranslate in LAN_CODES:
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
        print(f"code: \n{python_text}\n")
        print("\nresult\n")
        exec(python_text, globals())
        sys.stdout = old_buffer
        await client.edit_message_text(message.chat.id, message.id, new_buffer.getvalue())
    except Exception as e:
        sys.stdout = old_buffer
        await client.edit_message_text(message.chat.id, message.id, str(e))


@Client.on_message(filters.command('abuser_on') & filters.me)
async def run_abuser(client, message):
    client.abuser_on = True
    await client.send_message("me", "abuser enabled")


@Client.on_message(filters.command('abuser_off') & filters.me)
async def stop_abuser(client, message):
    client.abuser_on = False
    await client.send_message("me", "abuser disabled")


@Client.on_message(filters.create(not_me_filter))
async def my_handler(client, message):
    if client.abuser_on:

        if client.counter > 5:
            await delete_all(client, message, 'cch')
            client.counter = 0

        phrases = [
            'хрю',
            'Вы всегда так глупы, или сегодня особый случай?',
            'Как аутсайдер, что вы думаете о человеческой расе?',
            'Я так не думаю, может у вас растяжение мозга!',
            'Да вы просто чудо комик. Если смешно, это чудо!',
            'Как ты сюда попал? Неужели кто-то оставил клетку открытой?',
            'Я думаю, вы бы не хотели, чувствовать себя так, как вы выглядите!',
            'Не пытайтесь ничего найти у себя в голове, она же пустая.',
            'Вы являетесь живым доказательством того, что человек может жить без мозгов!',
            'Почему ты здесь? Я думал, что зоопарк закрывается на ночь!',
            'Скоро на тебя наденут деревянный макинтош\nИ в твоём доме будет играть музыка\nНо ты её не услышишь!',
            '-'
        ]
        FILTERED_STRINGS = (
            'пон4чик', 'пончик', 'Ponchik', 'P0Nchik', 'Пончиk', 'вадим', 'dailiastqq', 'поня ', '🍩', 'пон4ик',
            'понchik', 'кончик')
        IDS = (77003216, 371004967, 5253922892, 334810090, 5277675033, 357893284)

        def filter_strings(message_text, FILTERED_STRINGS):
            for string in FILTERED_STRINGS:
                if string in message_text:
                    return True
            return False

        send_message = any([
            bool(message.text and filter_strings(message.text.lower(), FILTERED_STRINGS)),
            bool(message.sticker and message.sticker.set_name in ('ponchik1488_by_fStikBot', 'gaydonbass')),
            bool(
                message.from_user and message.from_user.id in IDS and message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == 654009330)
        ]
        )
        msg = None
        if send_message:
            client.counter += 1
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            await asyncio.sleep(4)
            msg = await message.reply(phrases[random.randint(0, 9)])
            await client.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)

        if msg:
            add_to_my_messages(client, msg)


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


@Client.on_message(filters.command(LAN_CODES) & filters.me)
async def translate_message(client, message):
    command_1 = message.command[0]
    command_2 = message.command[1]
    if len(message.command) > 2:
        command_3 = message.text.replace('/', '').replace(command_1, '').replace(command_2, '')
        try:
            translation = client.translator.translate(command_3, src=command_1, dest=command_2).text
        except Exception as e:
            translation = 'exception'
    elif message.reply_to_message:
        translation = client.translator.translate(message.reply_to_message.text, src=command_1, dest=command_2).text
    else:
        await message.delete()
        return
    await client.edit_message_text(message.chat.id, message.id, translation)


@Client.on_message(filters.command('autotranslate') & filters.me)
async def send_info(client, message):
    if len(message.command) > 1:
        lang = message.command[1]
        if message.command[1] in LAN_CODES:
            client.autotranslate = lang
            msg = await message.reply(f"translation to {lang} enabled")
        else:
            msg = await message.reply(f"lang {lang} not supported")
    else:
        client.autotranslate = None
        msg = await message.reply("translation disabled")

    add_to_my_messages(client, msg)


@Client.on_message(filters.command('info') & filters.me)
async def autotranslate(client, message):
    info_msg = str(message)

    print(len(info_msg))

    cnt = len(info_msg) // 4000
    await client.send_message("me", info_msg[0:4000])

    for i in range(1, cnt - 1):
        await client.send_message("me", info_msg[i * 4000:(i + 1) * 4000])

    await client.send_message("me", info_msg[cnt * 4000:])
