import psycopg2
from psycopg2 import ProgrammingError
from config import PSQL_HOST, PSQL_USER_PASS, PSQL_USER_NAME, PSQL_PORT, BD_NAME


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
                if len(result[0]) == 1:
                    result = [a[0] for a in result]
            except (ProgrammingError, IndexError):
                result = []

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.commit()
            connection.close()
        return result
