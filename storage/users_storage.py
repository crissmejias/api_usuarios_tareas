import bcrypt
from db import connect_to_db, close_connection
from psycopg2 import errors

def list_users():
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute("""SELECT id,name,email,created_at FROM users;""")
        response = cursor.fetchall()
        return response
    finally:
       close_connection(conn,cursor)


def list_user(id):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute("SELECT id,name,email,created_at FROM users WHERE id = %s", [id])
        response = cursor.fetchone()
        return response
    finally:
       close_connection(conn,cursor)
        

def create_user(req):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        encoded_password = req["password"].encode('utf-8')
        salt = bcrypt.gensalt()
        encrypted_password = bcrypt.hashpw(encoded_password, salt)
        cursor.execute(
            """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        RETURNING id, name, email, role
        """,
            [req["name"], req["email"], encrypted_password],
        )
        conn.commit()
        new_user = cursor.fetchone()
        return new_user
    finally:
       close_connection(conn,cursor)


def edit_user(req, id):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(
            """
        UPDATE users SET name = %s, email=%s
        WHERE id = %s
        RETURNING id, name, email, role
        """,
            [req["name"], req["email"], id],
        )
        conn.commit()
        edited_user = cursor.fetchone()
        return edited_user
    finally:
       close_connection(conn,cursor)


def delete_user(id):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute("DELETE FROM users WHERE id = %s", [id])
        conn.commit()
    finally:
       close_connection(conn,cursor)
