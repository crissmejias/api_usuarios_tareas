import bcrypt

from storage.db import close_connection, connect_to_db


def auth_user(req):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(
            "SELECT id, name, email, password FROM users WHERE email = %s",
            [req["email"]],
        )
        user = cursor.fetchone()
        if not user:
            return None
        if not bcrypt.checkpw(
            req["password"].encode("utf-8"), user["password"].encode("utf-8")
        ):
            return None
        del user["password"]
        return user
    finally:
        close_connection(conn, cursor)
