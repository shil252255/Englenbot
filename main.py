from config import *
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
import random
from psql_modul import select_from_db, insert_to_db, command_for_db, count_from_db
from datetime import datetime
from typing import Final


bot = Bot(TG_API_KEY)
dispatcher = Dispatcher(bot)
training_now = {}
ENG_WORDS: Final = select_from_db('eng_words')


async def add_word_question(user_id: int):  # этот подход к добавлению слов мне не нравиться егополностью переделать
    all_user_learning_words_ids = select_from_db('users_progress', 'word_id', where=f'user_id = {user_id}')
    word_info = None
    for word_info in ENG_WORDS:
        if word_info[0] not in all_user_learning_words_ids:
            break
    inline_btn_add_wd = InlineKeyboardButton(messages_dict["add word"], callback_data=f'add_wd_st_0_id_{word_info[0]}')
    inline_btn_i_know = InlineKeyboardButton(messages_dict["i know"], callback_data=f'add_wd_st_10_id_{word_info[0]}')
    inline_kb_add_word = InlineKeyboardMarkup().add(inline_btn_add_wd, inline_btn_i_know)
    await bot.send_message(user_id, f"{word_info[1]} - {word_info[2]}", reply_markup=inline_kb_add_word)


async def training_word_question(user_id: int, main_word: list, variants):
    answer_kb = ReplyKeyboardMarkup(one_time_keyboard=True)
    for word in variants:
        answer_kb.add(KeyboardButton(word[1]))
    await bot.send_message(user_id, main_word[2], reply_markup=answer_kb)
    training_now[user_id] = main_word


def count_learning_words(user_id: int | str) -> int:
    return count_from_db(USERS_PROGRESS_TABLE, f'user_id = {user_id}AND status < 10')


def count_training_words(user_id: int | str) -> int:
    return count_from_db(USERS_PROGRESS_TABLE, f'user_id = {user_id}AND next_training < NOW()')


def add_word_into_bd(user_id: int | str, word_id: int | str, status: int | str) -> None:
    all_learning_words = command_for_db(f'SELECT word_id FROM users_progress WHERE user_id = {user_id}')
    if int(word_id) not in all_learning_words:
        command_for_db(f"INSERT INTO users_progress(user_id, word_id, status, next_training)"
                     f"VALUES({user_id}, {word_id}, {status}, now() + interval '{2**int(status)} minutes');")


async def training_word(user_id: str | int):
    training_pull = command_for_db(f"SELECT word_id, last_result, eng_words.word, "
                                 f"eng_words.short_rus_translation, status, next_training "
                                 f"FROM users_progress "
                                 f"LEFT JOIN eng_words ON users_progress.word_id = eng_words.id "
                                 f"WHERE user_id = {user_id}"
                                 f"ORDER BY next_training, status, word_id;")
    if not training_pull or training_pull[0][5] > datetime.now().astimezone():
        await bot.send_message(user_id, "You didn't have words to training now")
        training_now.pop(user_id, None)
        return
    main_word = training_pull.pop(0)
    variants = [[main_word[0], main_word[3]]]
    if main_word[1]:
        variants.append([int(main_word[1].split('_')[0]), main_word[1].split('_')[1]])
    if len(training_pull) < COUNT_OF_VARIANTS:
        training_pull.append(command_for_db(f"SELECT id, null, word, short_rus_translation FROM eng_words "))
    while len(variants) < COUNT_OF_VARIANTS:
        variant = random.choice(training_pull)
        if variant not in variants:
            variants.append([variant[0], variant[3]])
    random.shuffle(variants)
    await training_word_question(user_id, main_word, variants)


@dispatcher.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer(messages_dict['say_hello'])
    insert_to_db(USERS_TABLE, dict(message.from_user) | {"reg_date": message.date})


@dispatcher.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.answer(messages_dict['help'])


@dispatcher.message_handler(commands=['start_training'])
async def process_start_training_command(message: types.Message):
    await message.answer(messages_dict['start_training'])
    clw = count_learning_words(message.from_user.id)
    ctw = count_training_words(message.from_user.id)
    await message.answer(f'{messages_dict["all learning words count"]} {clw}\nFor training: {ctw}')
    if clw < LEARNING_PULL:
        await message.answer(messages_dict["let's add more"])
        await add_word_question(message.from_user.id)
    else:
        await training_word(message.from_user.id)


@dispatcher.message_handler(lambda message: message.from_user.id in training_now and "/" not in message.text)
async def process_training_answers(message: types.Message):
    if message.text == training_now[message.from_user.id][3]:
        await message.answer(random.choice(messages_dict["right answer"]))
        status = training_now[message.from_user.id][4] + 1
    else:
        await message.answer(random.choice(messages_dict["wrong answer"]))
        status = 0
    command_for_db(f"UPDATE users_progress SET status = {status}, "
                   f"next_training = now() + interval '{2**int(status)} minutes'"
                   f"WHERE user_id = {message.from_user.id} AND word_id = {training_now[message.from_user.id][0]};")
    await training_word(message.from_user.id)


@dispatcher.callback_query_handler(lambda c: "add_wd_" in c.data)
async def process_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    add_word_into_bd(callback_query.from_user.id, callback_query.data[15:], callback_query.data[10])
    if count_learning_words(callback_query.from_user.id) < LEARNING_PULL:
        await add_word_question(callback_query.from_user.id)


if __name__ == '__main__':
    executor.start_polling(dispatcher)

    """
    Всего 11 функций.
    причесаны 3/11
    """
