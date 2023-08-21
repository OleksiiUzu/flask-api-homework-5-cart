import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLiteDB:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connect = sqlite3.connect(self.db_name)
        self.connect.row_factory = dict_factory
        self.cursor = self.connect.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connect.commit()
        self.connect.close()

    def sql_query(self, query, all_data=True):
        answer = self.cursor.execute(query)
        if all_data:
            return answer.fetchall()
        else:
            return answer.fetchone()

    def insert_into(self, table_name, params):
        print('params: ', params)
        # у values перевіряється чи всі символи в значенні є числами, якщо ні то значення буде в лапках
        values = ','.join([str(f"'{i}'") if isinstance(i, str) and not all(num.isdigit() for num in i) else str(i) for i in params.values()])
        columns = ','.join([str(i) for i in params.keys()])
        print(values)
        print(columns)
        return self.cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")

    def select_from(self, table_name, columns: list, param=None, all_data=True):
        columns = ','.join(columns)
        query = f"SELECT {columns} FROM {table_name}"
        if param:
            param = ' and '.join([f"{key}='{value}'" for key, value in param.items()])
            query += f" WHERE {param}"
        if all_data:
            return self.sql_query(query)
        else:
            return self.sql_query(query, all_data=False)

    def update(self, table_name, columns: dict, param: dict):
        # знаю що DRY, потім щось придумаю))
        columns = ','.join([f"{key}='{value}'" for key, value in columns.items()])
        if len(param) > 1:
            param = ' AND '.join([f"{key}='{value}'" for key, value in param.items()])
            query = f"UPDATE {table_name} SET {columns} WHERE {param}"
            return self.sql_query(query)
        else:
            param = ','.join([f"{key}='{value}'" for key, value in param.items()])
            query = f"UPDATE {table_name} SET {columns} WHERE {param}"
            return self.sql_query(query)

    def ordered_by(self, table_name, columns: list, param=None, asc_desc=None):
        columns = ','.join(columns)
        query = f"SELECT {columns} FROM {table_name} ORDER BY {param} {asc_desc}"
        return self.sql_query(query)

    def delete_dish(self, table_name, columns: dict, param=False):

        if param:
            columns = ' AND '.join([f'{key}={value}' for key, value in columns.items()])
            query = f"DELETE FROM {table_name} WHERE {columns}"
            print(query)
        else:
            columns = ','.join([f'{key}={value}' for key, value in columns.items()])
            query = f"DELETE FROM {table_name} WHERE {columns}"
            print(query)
        return self.sql_query(query)


"""
Додати join запит до класу
SELECT * FROM Ordered_dishes join Dishes on Ordered_dishes.dish = Dishes.ID where Ordered_dishes.order_id = 123
"""