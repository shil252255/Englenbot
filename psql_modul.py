import psycopg2
from config import *

CONNECTION_PARAMETERS = {'host': PSQL_HOST,
                         'user': PSQL_USER_NAME,
                         'password': PSQL_USER_PASS,
                         'database': BD_NAME,
                         'port': PSQL_PORT
                         }


def command_for_db(command: str, is_return: bool = True) -> list:
    try:
        with psycopg2.connect(**CONNECTION_PARAMETERS) as connection_to_db:
            with connection_to_db.cursor() as cursor:
                cursor.execute(command)
                result = cursor.fetchall() if is_return else []
    except Exception as _ex:
        print("Error while working with PostgreSQL", _ex)  # Вот это вот в лог бы писать.
        cursor.close()
        connection_to_db.close()
        return []
    if result and len(result[0]) == 1:
        result = [r[0] for r in result]
    return result


def select_from_db(table: str,
                   columns: list[str] | str = '*',
                   where: str | None = None,
                   join: str | None = None,
                   order_by: str | None = None):
    columns = ', '.join(columns) if type(columns) == list else columns
    where = ' WHERE ' + where if where else ''
    join = f' LEFT JOIN {join} ' if join else ''
    order_by = f' ORDER BY {order_by} ' if order_by else ''
    return command_for_db(f'SELECT {columns} FROM {table}{join}{where}{order_by};')


def insert_to_db(table: str, data: dict, on_conflict_do_nothing: str | bool = True):
    columns = list(data.keys())
    values = ', '.join([f"'{data[col]}'" for col in columns])
    columns = ', '.join(columns)
    on_conflict = 'ON CONFLICT DO NOTHING' if on_conflict_do_nothing else ''
    return command_for_db(f'INSERT INTO {table}({columns}) VALUES({values}) {on_conflict};', False)


def count_from_db(table: str, where: str | None = None) -> int:
    where = ' WHERE ' + where if where else ''
    return int(command_for_db(f'SELECT count(*) FROM {table}{where};')[0])


def update_db(table: str, columns: list[str] | str = '*', values: list | dict = None, where: str | None = None):
    pass


def easy_tests():
    command0 = "insert into eng_words (word) values ('nnn');"
    command1 = 'select count(*) from eng_words'
    command2 = 'select * from eng_words'
    command3 = "select word from eng_words where word = 'ca,,,t'"
    for command in [command1, command2, command3]:
        print(command)
        with psycopg2.connect(**CONNECTION_PARAMETERS) as con:
            with con.cursor() as cur:
                cur.execute(command)
                res = cur.fetchall()
        if res and len(res[0]) == 1:
            res = [r[0] for r in res]
        print(res)
        print('-' * 50, '\n' * 3)


if __name__ == '__main__':
    # print(select_from_db('eng_words', where='id = 1275'))
    print(command_for_db("SELECT id FROM elb_users"))
    print(select_from_db('elb_users', 'id'))

    command_for_db(f"INSERT INTO elb_users(id, is_bot, first_name, last_name, username, language_code, reg_date)"
                   f"VALUES ("
                   f'244605875, '
                   f'FALSE, '
                   f"'Илья', "
                   f"'Шилов', "
                   f"'Il252255', "
                   f"'ru', "
                   f"'2023-03-09 20:01:54+03'"
                   f') ON CONFLICT DO NOTHING;', is_return=False)
