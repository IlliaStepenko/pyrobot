from pyrogram.enums import MessageEntityType
from gtts import gTTS
from io import BytesIO
import asyncio
import datetime
import io
import sys
from pyrogram import filters, Client
from pyrogram import enums


def add_to_my_messages(client, message):
    chat_id = message.chat.id
    if not client.my_messages.get(chat_id, []):
        client.my_messages.update({chat_id: []})
    client.my_messages[chat_id].append(message.id)


async def not_me_filter(_, __, m):
    return m.chat.id in (-1001162926553, -1001520738007) and not bool(
        m.from_user and m.from_user.is_self or getattr(m, "outgoing", False))


not_me = filters.create(not_me_filter)


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
        print(f"code: \n{python_text}\n")
        print("\nresult\n")
        exec(python_text, globals())
        sys.stdout = old_buffer
        await client.edit_message_text(message.chat.id, message.id, new_buffer.getvalue())
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
        model="text-davinci-003",
        prompt=message.text,
        temperature=0.5,
        max_tokens=1000,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.5
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


def make_readable_list(l):
    return ", \n".join(['\t\t\t\t' + str(i) for i in l])


@Client.on_message(filters.command('get_config') & filters.me)
async def get_config(client, message):
    result = 'ConfigList:\n\n'
    result += f"\t\t\t\tabuser_on: {client.abuser_on}\n"
    result += f"\t\t\t\tautotranslate: {client.autotranslate}\n"
    result += f"\t\t\t\task_openai: {client.ask_openai}\n"
    result += f"\t\t\t\tlang_codes: {', '.join(client.lang_codes)}"
    result += "\n\n"
    result += f'Source chats: [\n{make_readable_list(client.source_chats)}\n]'
    result += "\n\n"
    result += f'Target chats: [\n{make_readable_list(client.target_chats)}\n]'
    result += "\n\n"
    result += f'White list: [\n{make_readable_list(client.whitelist)}\n]'
    msg = await message.reply(result, disable_web_page_preview=True)
    add_to_my_messages(client, msg)
