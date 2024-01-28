import mysql.connector
from decouple import config


def get_db_connection():
    dbHost = config('HOST')
    dbUser = config('USER')
    dbPassword = config('PASSWORD')
    dbDatabase = config('DATABASE')
    return mysql.connector.connect(
        host=dbHost,
        user=dbUser,
        password=dbPassword,
        database=dbDatabase
    )