import asyncio
import datetime
import random
import io
import sys
from pyrogram import filters, Client
from pyrogram import enums

command_last_used = None


async def not_me_filter(_, __, m):
    return m.chat.id == -1001162926553 and not bool(m.from_user and m.from_user.is_self or getattr(m, "outgoing", False))


async def delete_all(client, message):
    LIMIT = 50
    offset = 0
    has_messages = True
    chat_id = message.chat.id
    await message.delete()
    while has_messages:
        chat_messages = []
        async for message in client.search_messages(chat_id=chat_id, from_user='me', offset=offset, limit=LIMIT):
            chat_messages.append(message.id)
        await client.delete_messages(chat_id=chat_id, message_ids=chat_messages)
        offset += 50
        has_messages = bool(chat_messages)

    result_string = f"Удаление ВСЕХ сообщений из чата {chat_id} в {datetime.datetime.now()}"

    await client.send_message("me", result_string)


@Client.on_message(filters.command('check') & filters.me & filters.chat("me"))
async def check(client, message):
    await message.reply("Helloooooo")


@Client.on_message(filters.command('dall') & filters.me)
async def delete_all_message(client, message):
   await delete_all(client, message)


@Client.on_message(filters.command('py') & filters.me)
async def run_python(client, message):
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

        if send_message:
            client.counter += 1
            await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
            await asyncio.sleep(4)
            await message.reply(phrases[random.randint(0, 9)])
            await client.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)

        if client.counter > 5:
            await delete_all(client, message)
            client.counter = 0
