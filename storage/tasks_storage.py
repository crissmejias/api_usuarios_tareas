from .db import close_connection, connect_to_db


def list_tasks(user_id):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(
            """SELECT  id, title, completed FROM tasks WHERE user_id = %s""", [user_id]
        )
        tasks = cursor.fetchall()
        return tasks
    finally:
        close_connection(conn, cursor)


def get_task(user_id, id):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(
            """SELECT id, title, completed FROM tasks WHERE user_id = %s AND id = %s""",
            [user_id, id],
        )
        task = cursor.fetchone()
        return task
    finally:
        close_connection(conn, cursor)


def create_task(title, user_id):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(
            """INSERT INTO tasks (user_id,title)
        VALUES (%s, %s)
        RETURNING id, title, completed
        """,
            [title, user_id],
        )
        conn.commit()
        new_task = cursor.fetchone()
        return new_task
    finally:
        close_connection(conn, cursor)
