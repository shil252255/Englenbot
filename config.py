from dotenv import load_dotenv
from os import environ
import json

LANG = 'RU'
load_dotenv()

TG_API_KEY = environ['ENGLENBOT_APIKEY']
PSQL_USER_NAME = environ['PSQL_USER_NAME']
PSQL_USER_PASS = environ['PSQL_USER_PASS']
BD_NAME = 'elb_bd'
MAIN_DICT = 'eng_words'
PSQL_HOST = '127.0.0.1'
PSQL_PORT = 5432
LEARNING_PULL = 20
COUNT_OF_VARIANTS = 5
USERS_TABLE = 'elb_users'
USERS_PROGRESS_TABLE = 'users_progress'

with open(f'{LANG}.json', 'r', encoding='utf-8') as file:
    # неверный метод который загружает один язык для всех пользователей.
    messages_dict = json.load(file)
