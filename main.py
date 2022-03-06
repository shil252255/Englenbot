from config import TG_API_KEY, LANG
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import json

bot = Bot(TG_API_KEY)
dispatcher = Dispatcher(bot)

with open(f'{LANG}.json', 'r', encoding='utf-8') as file:
    messages_dict = json.load(file, )


@dispatcher.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(messages_dict['say_hello'])


@dispatcher.message_handler(commands=['help'])
async def process_start_command(message: types.Message):
    await message.reply(messages_dict['help'])


if __name__ == '__main__':
    executor.start_polling(dispatcher)
