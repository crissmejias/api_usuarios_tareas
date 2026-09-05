import os

from dotenv import load_dotenv
from psycopg2 import connect


def connect_to_db():
    load_dotenv()
    conn = connect(
        database=os.getenv("DB_NAME"),
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port="5432",
    )
    cursor = conn.cursor()
    return conn, cursor

def close_connection(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()