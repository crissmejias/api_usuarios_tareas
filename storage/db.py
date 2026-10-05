import os
from psycopg2 import connect
from psycopg2.extras import RealDictCursor


def connect_to_db():
    conn = connect(
        database=os.getenv("DB_NAME"),
        user="postgres",
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port="5432",
    )
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cursor


def close_connection(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()
