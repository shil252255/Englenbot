from dotenv import load_dotenv
from os import environ

LANG = 'RU'
load_dotenv()

TG_API_KEY = environ['ENGLENBOT_APIKEY']
PSQL_USER_NAME = environ['PSQL_USER_NAME']
PSQL_USER_PASS = environ['PSQL_USER_PASS']
BD_NAME = 'elb_bd'
PSQL_HOST = '127.0.0.1'
PSQL_PORT = 5432
LEARNING_PULL = 20
