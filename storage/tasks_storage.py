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


def create_task(user_id, title):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(
            """INSERT INTO tasks (user_id,title)
        VALUES (%s, %s)
        RETURNING id, title, completed
        """,
            [user_id, title],
        )
        conn.commit()
        new_task = cursor.fetchone()
        return new_task
    finally:
        close_connection(conn, cursor)


def edit_task(user_id, id, req):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(
            """
        UPDATE tasks SET title =%s, completed=%s
        WHERE id = %s AND user_id = %s
        RETURNING id, title, completed""",
            [req["title"], req["completed"], id, user_id],
        )
        if cursor.rowcount == 0:
            return None
        edited_task = cursor.fetchone()
        conn.commit()
        return edited_task
    finally:
        close_connection(conn, cursor)


def delete_task(user_id, id):
    conn = cursor = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute(
            """
        DELETE FROM tasks
        WHERE user_id = %s AND id = %s
        """,
            [user_id, id],
        )
        if cursor.rowcount == 0:
            return None
        conn.commit()
        return True
    finally:
        close_connection(conn, cursor)
