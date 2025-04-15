import os
from typing import Any

import psycopg2
from dotenv import load_dotenv

from LOGGING_SETTINGS.settings import database_logger

load_dotenv()


class Database:
    def __init__(self, host: str, port: str|int, db_name: str, user: str, password: str):
        self.cursor = None
        try:
            self.connect = psycopg2.connect(host=host,
                                            port=port,
                                            database=db_name,
                                            user=user,
                                            password=password,
                                            options="-c client_encoding=UTF8")
            # self.cursor = self.connect.cursor()
            database_logger.debug(f'DataBase - *{db_name}* connection...')
            with self.connect.cursor() as cursor:
                cursor.execute(
                    "SELECT version();"
                )
                database_logger.debug(f'Server version: {cursor.fetchone()[0]}')
        except Exception as _ex:
            database_logger.critical(f'Can`t establish connection to DataBase with error: {_ex}')

    def open(self):
        self.cursor = self.connect.cursor()

    def close(self):
        self.cursor.close()

    msg = f'The sql query failed with an error' # Default error query message, when DEBUG -> False

    def query(self, query: str, values: tuple = None, execute_many = False, fetch: str = None, size: int = None, log_level: int = 40,
              msg: str = msg, debug: bool = False) -> Any:
        """
        :param query: takes sql query, for example: "SELECT * FROM table"
        :param values: takes tuple of values
        :param execute_many: if True - change cursor *execute* to *execute_many*
        :param fetch: choose of one upper this list
        :param size: count of fetching info from database. Default 10, JUST FOR fetchmany
        :param log_level: choose of logging level if needed. Default 40[ERROR]
        :param msg: message for logger
        :param debug: make Exception error message

        - fetch:
            1. fetchone
            2. fetchall
            3. fetchmany - size required(default 10)
            4. None - using for UPDATE, DELETE etc.

        - log_level:
            1. 10 (Debug) - the lowest logging level, intended for debugging messages, for displaying diagnostic information about the application.
            2. 20 (Info) - this level is intended for displaying data about code fragments that work as expected.
            3. 30 (Warning) - this logging level provides for the display of warnings, it is used to record information about events that a programmer usually pays attention to. Such events may well lead to problems during the operation of the application. If you do not explicitly set the logging level, the warning is used by default.
            4. 40 (Error)(default) - this logging level provides for the display of information about errors - that part of the application does not work as expected, that the program could not execute correctly.
            5. 50 (Critical) - this level is used to display information about very serious errors, the presence of which threatens the normal functioning of the entire application. If you do not fix such an error, this may lead to the application ceasing to work.
        """
        try:
            self.open()
            self.cursor.execute('SAVEPOINT point1')
            if fetch == 'fetchone':
                with self.connect.cursor() as cursor:
                    if values is None:
                        cursor.execute(query)
                        return cursor.fetchone()
                    else:
                        cursor.execute(query, values)
                        return cursor.fetchone()
            elif fetch == 'fetchall':
                with self.connect.cursor() as cursor:
                    if values is None:
                        cursor.execute(query)
                        return cursor.fetchall()
                    else:
                        cursor.execute(query, values)
                        return cursor.fetchall()
            elif fetch == 'fetchmany':
                with self.connect.cursor() as cursor:
                    if values is None:
                        cursor.execute(query)
                        return cursor.fetchmany(size=size)
                    else:
                        cursor.execute(query, values)
                        return cursor.fetchmany(size=size)
            else:
                with self.connect.cursor() as cursor:
                    if values is None:
                        cursor.execute(query)
                    else:
                        if execute_many:
                            cursor.executemany(query, values)
                        else:
                            cursor.execute(query, values)
            self.cursor.execute('RELEASE point1')
            self.connect.commit()
            self.close()
            return 'Success'
        except Exception as _ex:
            if debug:
                database_logger.log(msg=_ex, level=log_level)
                self.cursor.execute('ROLLBACK TO point1')
                return 'Error'
            else:
                database_logger.log(msg=msg, level=log_level)
                self.cursor.execute('ROLLBACK TO point1')
                return 'Error'


db = Database(host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), db_name=os.getenv("DB_NAME"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"))

create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    user_id NUMERIC(50) UNIQUE NOT NULL,
    user_name TEXT CHECK (char_length(user_name) <= 500),
    username TEXT CHECK (char_length(username) <= 500),
    user_surname TEXT CHECK (char_length(user_surname) <= 500),
    id SERIAL PRIMARY KEY
);
"""

create_tokens_table = """
CREATE TABLE IF NOT EXISTS tokens (
    id SERIAL PRIMARY KEY,
    yandex_token TEXT NULL,
    yandex_refresh_token TEXT NULL,
    avito_token TEXT NULL,
    avito_refresh_token TEXT NULL,
    vk_token TEXT NULL,
    vk_refresh_token TEXT NULL,
    vk_device_id TEXT NULL
)
"""


db.query(query=create_users_table)
db.query(query=create_tokens_table)