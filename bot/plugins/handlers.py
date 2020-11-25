import datetime

from pyrogram import filters, Client


@Client.on_message(filters.command('check') & filters.me & filters.chat("me"))
async def check(client, message):
    await message.reply("Helloooooo")


@Client.on_message(filters.command('tukan') )
async def det_tukan(client, message):
    tukan_id = 303701321
    tukan = await client.get_users(tukan_id)
    await message.reply('@'+tukan['username'])


@Client.on_message(filters.command('dall') & filters.me & ~filters.chat("me"))
async def delete_all_message(client, message):
    chat_id = message['chat']['id']

    await message.delete()

    chat_messages = [message['message_id'] async for message in client.search_messages(chat_id=chat_id, from_user="me") ]

    await client.delete_messages(chat_id=chat_id, message_ids=chat_messages)

    result_string = f"Удаление ВСЕХ сообщений из чата {chat_id} в {datetime.datetime.now()}"

    await client.send_message("me", result_string)


@Client.on_message(filters.user(303701321))
async def down_answer(client, message):
    down_id = 77003216
    tuk_test = 303701321
    message.reply_text("asdad)
                   
