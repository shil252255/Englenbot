import psycopg2


class Database:
    def __init__(self, **kwargs):
        self.CONNECTION_PARAMETERS = kwargs
        self.name = CONNECTION_PARAMETERS['database']
        self.connection = psycopg2.connect(**self.CONNECTION_PARAMETERS)
        self.__tables = {tb_name: Table(tb_name, self) for tb_name in self.select('INFORMATION_SCHEMA.TABLES',
                                                                                  'TABLE_NAME',
                                                                                  "table_schema = 'public'")}
        # Специально не отлавливаю здесь psycopg2.Error так как если что-то пойдет не
        # по плану на этом этапе лучше если все упадет и выдаст ошивку само,
        # хотя наверное лучше чтобы оно просто завершало работу выдавая соответственное сообщение в консоль

    def __str__(self):
        copy_parameters = self.CONNECTION_PARAMETERS
        copy_parameters['password'] = '***'
        connection_information = '\n'.join([f'{param}: {values}' for param, values in copy_parameters.items()])
        return connection_information

    def _is_connect(self):
        print(self.connection)

    def __request(self, command: str, is_return: bool = True) -> list:
        try:
            with self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute(command)
                    result = cursor.fetchall() if is_return else []
        except Exception as _ex:
            print("Error while working with PostgreSQL", _ex)  # Вот это вот в лог бы писать.
            cursor.close()
            return []
        if result and len(result[0]) == 1:
            result = [r[0] for r in result]
        return result

    def select(self, table: str,
               columns: list[str] | str = '*',
               where: str | None = None,
               join: str | None = None,
               order_by: str | None = None):
        columns = ', '.join(columns) if type(columns) == list else columns
        where = ' WHERE ' + where if where else ''
        join = f' LEFT JOIN {join} ' if join else ''
        order_by = f' ORDER BY {order_by} ' if order_by else ''
        return self.__request(f'SELECT {columns} FROM {table}{join}{where}{order_by};')

    def insert(self, table: str, data: dict, on_conflict_do_nothing: str | bool = True):
        columns = list(data.keys())
        values = ', '.join([f"'{data[col]}'" for col in columns])
        columns = ', '.join(columns)
        on_conflict = 'ON CONFLICT DO NOTHING' if on_conflict_do_nothing else ''
        return self.__request(f'INSERT INTO {table}({columns}) VALUES({values}) {on_conflict};', False)

    def count(self, table: str, where: str | None = None) -> int:
        where = ' WHERE ' + where if where else ''
        return int(self.__request(f'SELECT count(*) FROM {table}{where};')[0])

    def update(self, table: str, columns: list[str] | str = '*', values: list | dict = None,
               where: str | None = None):
        pass

    @property
    def tables_name(self):
        return list(self.__tables.keys())

    @property
    def tables(self):
        return list(self.__tables.values())

    def table(self, name):
        if name in self.__tables.keys():
            return self.__tables[name]
        else:
            raise KeyError(f'Database {self.name} dose not contain table withe name "{name}"')


class Table:
    def __init__(self, name, database: Database):
        self.name = name
        self.database = database
        self.__columns = {col_name: Column(col_name, self) for col_name in
                          self.database.select('INFORMATION_SCHEMA.COLUMNS', 'column_name',
                                               f"TABLE_NAME='{self.name}'")}

    def select(self, **kwargs):
        return self.database.select(self.name, **kwargs)

    def insert(self, **kwargs):
        return self.database.insert(self.name, **kwargs)

    def count(self, **kwargs):
        return self.database.count(self.name, **kwargs)

    def update(self, **kwargs):
        return self.database.update(self.name, **kwargs)

    @property
    def columns_names(self):
        return list(self.__columns.keys())

    @property
    def columns(self):
        return list(self.__columns.values())


class Column:
    def __init__(self, name: str, table: Table, primary_key: bool = False):
        self.name = name
        self.table = table
        self.primary_key = primary_key

    def select(self, **kwargs):
        return self.table.select(columns=self.name, **kwargs)

    def insert(self, **kwargs):
        return self.table.insert(columns=self.name, **kwargs)

    def count(self, **kwargs):
        return self.table.count(columns=self.name, **kwargs)

    def update(self, **kwargs):
        return self.table.update(columns=self.name, **kwargs)


if __name__ == '__main__':
    from config import CONNECTION_PARAMETERS

    db = Database(**CONNECTION_PARAMETERS)
    print(db)
    for table in db.tables:
        print(f'{table.name}:')
        for column in table.columns:
            print(f'\t-{column.name}')
    print(True) if ' ' else print(False)
