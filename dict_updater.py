import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
from config import PSQL_HOST, PSQL_USER_PASS, PSQL_USER_NAME, BD_NAME, PSQL_PORT


def add_df_to_bd(data: pd.DataFrame, table_name: str) -> None:
    conn_string = f'postgresql://{PSQL_USER_NAME}:{PSQL_USER_PASS}@{PSQL_HOST}:{PSQL_PORT}/{BD_NAME}'
    db = create_engine(conn_string)
    conn = db.connect()
    data.to_sql(table_name, con=conn, if_exists='replace', index=False)


def get_words_from_englishdom() -> pd.DataFrame:
    url = 'https://www.englishdom.com/blog/1000-samyx-vazhnyx-slov-v-anglijskom-yazyke/'
    page = requests.request('GET', url)
    soup = BeautifulSoup(page.text, 'lxml')
    table = soup.find('table')
    df_table = pd.DataFrame(columns=['word', 'translation'])
    for line in table.find_all('tr')[1:]:
        df_table.loc[len(df_table)] = [cell.text for cell in line.find_all('td')][1:]
    return df_table


def main() -> None:
    df_table = get_words_from_englishdom()
    table_name = 'top_1000_words'
    df_table.to_csv('covid_data.csv', index=False)
    add_df_to_bd(df_table, table_name)


if __name__ == '__main__':
    main()
