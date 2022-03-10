
import csv
from main import psql_command

with open('dict 1.csv', 'r', encoding='UTF8') as df:
    spamreader = csv.reader(df)
    for row in spamreader:
        print(', '.join(row))
        psql_command(f"INSERT INTO eng_words(word, short_rus_translation)"
                     f"VALUES("
                     f"'{row[0]}',"
                     f"'{row[2]}');")


if __name__ == '__main__':
    pass
