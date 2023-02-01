import datetime
import random
import io
import sys
from pyrogram import filters, Client

command_last_used = None

LANGUAGE_CODES = ['ru', 'en', 'pl']


@Client.on_message(filters.command('check') & filters.me & filters.chat("me"))
async def check(client, message):
    await message.reply("Helloooooo")


@Client.on_message(filters.command('dall') & filters.me)
async def delete_all_message(client, message):
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


@Client.on_message(filters.command('abuser_off') & filters.me)
async def stop_abuser(client, message):
    client.abuser_on = False


@Client.on_message(not filters.me)
async def my_handler(client, message):
    if getattr(client, 'abuser_on', False) and message.chat.id == -1001162926553:
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
        FILTERED_STRINGS = ('пон4чик', 'пончик', 'вадим', 'dailiastqq', 'поня ', '🍩', 'пон4ик', 'понchik', 'кончик')
        IDS = (77003216, 371004967, 5253922892, 334810090, 5277675033, 357893284)

        def filter_strings(message_text):
            for string in FILTERED_STRINGS:
                if string in message_text:
                    return True
            return False

        if message.text and filter_strings(message.text.lower()):
            await message.reply(phrases[random.randint(0, 9)])

        elif message.sticker and message.sticker.set_name in ('ponchik1488_by_fStikBot', 'gaydonbass'):
            await message.reply(phrases[random.randint(0, 9)])

        elif message.from_user and message.from_user.id in IDS and message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == 654009330:
            await message.reply(phrases[random.randint(0, 9)])


