import psycopg2


_create_table_queries = [
    """CREATE TABLE if not exists codes (
    code_name CHAR(8) PRIMARY KEY NOT NULL,
    code_type CHAR(25),
    rus_equivalent TEXT
    );""",
    """CREATE TABLE if not exists users (
    user_id BIGSERIAL PRIMARY KEY NOT NULL,
    tokens_amount INT,
    notifications_status DECIMAL(1),
    transcription_language CHAR(3) REFERENCES codes(code_name), 
    result_format CHAR(8) REFERENCES codes(code_name)
    );""",
    """CREATE TABLE if not exists user_history (
    record_id BIGINT PRIMARY KEY,
    user_id BIGSERIAL REFERENCES users(user_id),
    date DATE,
    operation_type CHAR(8) REFERENCES codes(code_name),
    source_type CHAR(8) REFERENCES codes(code_name),
    source_link TEXT
    );""",
    """CREATE TABLE if not exists youtube_cash (
    youtube_link TEXT PRIMARY KEY NOT NULL,
    date DATE,
    transcription_path TEXT
    );"""
]


class DbHelper:

    def __init__(self):
        self.connection = psycopg2.connect(
            host="localhost",
            database="transcribot",
            user='user',
            password='12345'
        )

        self.cursor = self.connection.cursor()
        self.__create_tables()

    def __create_tables(self):

        for create_table_query in _create_table_queries:
            self.cursor.execute(create_table_query)
            self.connection.commit()

    def insert_row(self, table_name: str, params: dict) -> None:
        request = f"""INSERT INTO "{table_name}" 
                        ({', '.join([f'"{key}"' for key in params])}) 
                        VALUES ({', '.join(['%s'] * len(params))})"""

        self.cursor.execute(request, tuple(params.values()))
        self.connection.commit()

    def update_row(self, table_name: str, key_params: dict, new_params: dict) -> None:
        request = f"""UPDATE "{table_name}" SET
                            {', '.join([f'"{key}" = %s' for key in new_params])}
                            WHERE {' AND '.join([f'"{key}" = %s' for key in key_params])}
                            """

        self.cursor.execute(request, tuple(new_params.values()) + tuple(key_params.values()))
        self.connection.commit()

    def select_rows(self, table_name: str, find_params: list, by_params: dict) -> list[tuple]:
        request = f"""SELECT {', '.join([f'"{key}"' for key in find_params])}
                        FROM "{table_name}"
                        WHERE {' AND '.join([f'"{key}" = %s' for key in by_params])}"""

        self.cursor.execute(request, tuple(by_params.values()))
        return self.cursor.fetchall()

    def delete_rows(self, table_name: str, params: dict) -> None:
        request = f"""DELETE FROM {table_name}
                        WHERE {' AND '.join([f'"{key}" = %s' for key in params])}"""

        self.cursor.execute(request, tuple(params.values()))
        self.connection.commit()

    def get_user_history(self, user_id: int) -> list:
        pass

    def __close(self):
        self.cursor.close()
        self.connection.close()


if __name__ == '__main__':
    db_helper = DbHelper()
    db_helper.insert_row('test', {'column': 1, 'value': 'abc'})
    db_helper.update_row('test', {'column': 2}, {'value': 'h'})
    row = db_helper.select_rows('test', ['value'], {'column': 1})
    print(row)
    db_helper.delete_rows('test', {'value': 'h'})
