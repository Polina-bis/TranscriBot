import datetime
import time

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
    record_id BIGSERIAL PRIMARY KEY,
    user_id BIGSERIAL REFERENCES users(user_id),
    date DATE,
    operation_type CHAR(8) REFERENCES codes(code_name),
    source_type CHAR(8) REFERENCES codes(code_name),
    source_link TEXT
    );""",
    """INSERT INTO codes (code_name, code_type, rus_equivalent)
    SELECT 'summ', 'operation_type', 'Суммаризация'
    WHERE NOT EXISTS (SELECT 1 FROM codes);""",
    """
    INSERT INTO codes (code_name, code_type, rus_equivalent)
    SELECT 'tran', 'operation_type', 'Транскрибация'
    WHERE NOT EXISTS (SELECT 1 FROM codes);""",
    """
    INSERT INTO codes (code_name, code_type, rus_equivalent)
    SELECT 'yt', 'source_type', 'YouTube'
    WHERE NOT EXISTS (SELECT 1 FROM codes);""",
    """
    INSERT INTO codes (code_name, code_type, rus_equivalent)
    SELECT 'vm', 'source_type', 'Голосовое'
    WHERE NOT EXISTS (SELECT 1 FROM codes);""",
    """
    INSERT INTO codes (code_name, code_type, rus_equivalent)
    SELECT 'cr', 'source_type', 'Кружочек'
    WHERE NOT EXISTS (SELECT 1 FROM codes);""",
    """
    INSERT INTO codes (code_name, code_type, rus_equivalent)
    SELECT 'rus', 'transcription_language', 'Русский язык'
    WHERE NOT EXISTS (SELECT 1 FROM codes);""",
    """
    INSERT INTO codes (code_name, code_type, rus_equivalent)
    SELECT 'eng', 'transcription_language', 'Английский язык'
    WHERE NOT EXISTS (SELECT 1 FROM codes);""",
    """
    INSERT INTO codes (code_name, code_type, rus_equivalent)
    SELECT 'text', 'result format', 'Текст'
    WHERE NOT EXISTS (SELECT 1 FROM codes);""",
    """
    INSERT INTO codes (code_name, code_type, rus_equivalent)
    SELECT 'doc', 'result format', 'Документ'
    WHERE NOT EXISTS (SELECT 1 FROM codes);
    """,
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
        try:
            request = f"""INSERT INTO "{table_name}" 
                            ({', '.join([f'"{key}"' for key in params])}) 
                            VALUES ({', '.join(['%s'] * len(params))})"""

            self.cursor.execute(request, tuple(params.values()))
            self.connection.commit()
        except psycopg2.errors.UniqueViolation:
            pass

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

    def get_printable_user_history(self, user_id: int) -> list[tuple]:
        request = """select uh.date, c.rus_equivalent as operation_type, c2.rus_equivalent as source_type, uh.source_link 
                        from user_history uh 
                        join codes c on uh.operation_type = c.code_name
                        join codes c2 on uh.source_type = c2.code_name
                        where uh.user_id = {};""".format(user_id)

        self.cursor.execute(request)
        return self.cursor.fetchall()

    def __close(self):
        self.cursor.close()
        self.connection.close()


if __name__ == '__main__':
    db_helper = DbHelper()
    db_helper.insert_row('test', {'column': 2, 'value': 'two'})

