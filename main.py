from config import TG_API_KEY, LANG, PSQL_HOST, PSQL_USER_PASS, PSQL_USER_NAME, PSQL_PORT, BD_NAME, LEARNING_PULL
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
import json
import psycopg2
from psycopg2 import ProgrammingError

bot = Bot(TG_API_KEY)
dispatcher = Dispatcher(bot)

with open(f'{LANG}.json', 'r', encoding='utf-8') as file:
    messages_dict = json.load(file, )


async def add_word_question(user_id: int):
    all_dict = psql_command(f'SELECT * FROM eng_words')
    all_learning_words = psql_command(f'SELECT word_id FROM users_progress WHERE user_id = {user_id}')
    all_learning_words = [a[0] for a in all_learning_words]
    for word_info in all_dict:
        if word_info[0] not in all_learning_words:
            word_id, word, word_translation = word_info[:3]
            break
    inline_btn_add_word = InlineKeyboardButton(messages_dict["add word"], callback_data=f'add_wd_st_0_id_{word_id}')
    inline_btn_i_know = InlineKeyboardButton(messages_dict["i know"], callback_data=f'add_wd_st_5_id_{word_id}')
    inline_kb_add_word = InlineKeyboardMarkup().add(inline_btn_add_word, inline_btn_i_know)
    await bot.send_message(user_id, f"{word} - {word_translation}", reply_markup=inline_kb_add_word)


def count_learning_words(user_id: int) -> int:
    return int(psql_command(f'SELECT count(*) FROM users_progress WHERE user_id = {user_id}AND status < 5')[0][0])


def add_word_into_bd(user_id: int | str, word_id: int | str, status: int | str) -> None:
    all_learning_words = psql_command(
        f'SELECT word_id FROM users_progress WHERE user_id = {user_id}')
    all_learning_words = [a[0] for a in all_learning_words]
    if int(word_id) not in all_learning_words:
        psql_command(f"INSERT INTO users_progress(user_id, word_id, status)"
                     f"VALUES({user_id}, {word_id}, {status});")


def psql_command(command: str) -> list:
    connection = None
    result = []
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
                result = []

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.commit()
            connection.close()
        return result


@dispatcher.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(messages_dict['say_hello'])
    all_users_tg_id = psql_command("SELECT id FROM elb_users")
    all_users_tg_id = [user_tg_id[0] for user_tg_id in all_users_tg_id]
    if message["from"]["id"] not in all_users_tg_id:
        psql_command(f"INSERT INTO elb_users(id, is_bot, first_name, last_name, username, language_code, reg_date)"
                     f"VALUES ("
                     f'{message["from"]["id"]}, '
                     f'{message["from"]["is_bot"]}, '
                     f"'{message['from']['first_name']}', "
                     f"'{message['from']['last_name']}', "
                     f"'{message['from']['username']}', "
                     f"'{message['from']['language_code']}', "
                     f"'{message['date']}'"
                     f')')


@dispatcher.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.answer(messages_dict['help'])


@dispatcher.message_handler(commands=['start_training'])
async def process_start_training_command(message: types.Message):
    await message.answer(messages_dict['start_training'])
    clw = count_learning_words(message.from_user.id)
    await message.answer(f'{messages_dict["all learning words count"]} {clw}')
    if clw < LEARNING_PULL:
        await message.answer(messages_dict["let's add more"])
        await add_word_question(message.from_user.id)
    else:
        pass


@dispatcher.callback_query_handler(lambda c: "add_wd_" in c.data)
async def process_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    add_word_into_bd(callback_query.from_user.id, callback_query.data[15:], callback_query.data[10])
    if count_learning_words(callback_query.from_user.id) < LEARNING_PULL:
        await add_word_question(callback_query.from_user.id)


if __name__ == '__main__':
    executor.start_polling(dispatcher)
