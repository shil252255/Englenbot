from config import TG_API_KEY, LANG, PSQL_HOST, PSQL_USER_PASS, PSQL_USER_NAME, PSQL_PORT, BD_NAME
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import json
import psycopg2
from psycopg2 import ProgrammingError


bot = Bot(TG_API_KEY)
dispatcher = Dispatcher(bot)

with open(f'{LANG}.json', 'r', encoding='utf-8') as file:
    messages_dict = json.load(file, )


def psql_command(command):
    connection = None
    result = None
    try:
        connection = psycopg2.connect(
            host=PSQL_HOST,
            user=PSQL_USER_NAME,
            password=PSQL_USER_PASS,
            database=BD_NAME,
            port=PSQL_PORT
        )
        with connection.cursor() as cursor:
            cursor.execute(command)
            try:
                result = cursor.fetchall()
            except (ProgrammingError, IndexError):
                result = None

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.commit()
            connection.close()
        return result


@dispatcher.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(messages_dict['say_hello'])
    all_users_tg_id = psql_command("SELECT tg_id FROM elb_users")
    if all_users_tg_id is None:
        all_users_tg_id = []
    else:
        for n, user_tg_id in enumerate(all_users_tg_id):
            all_users_tg_id[n] = user_tg_id[0]
    if message["from"]["id"] not in all_users_tg_id:
        psql_command(f"INSERT INTO elb_users(tg_id, chat_id, name, surname, reg_date)"
                     f"VALUES ("
                     f'{message["from"]["id"]}, '
                     f'{message["chat"]["id"]}, '
                     f"'{message['from']['first_name']}', "
                     f"'{message['from']['last_name']}', "
                     f"'{message['date']}'"
                     f')')


@dispatcher.message_handler(commands=['help'])
async def process_start_command(message: types.Message):
    await message.reply(messages_dict['help'])


if __name__ == '__main__':
    executor.start_polling(dispatcher)
