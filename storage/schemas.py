from db import connect_to_db
from psycopg2 import errors


def createTasks():
    conn = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute("""DROP TABLE IF EXISTS tasks;""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        completed BOOLEAN NOT NULL DEFAULT false,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );""")
        conn.commit()
    except errors.Error as error:
        return {"error": f"{error}"}
    finally:
        if conn:
            conn.close()


def createUsers():
    conn = None
    try:
        conn, cursor = connect_to_db()
        cursor.execute("""DROP TABLE IF EXISTS users CASCADE;""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER NOT NULL GENERATED ALWAYS AS IDENTITY,
        name TEXT NOT NULL,
        email VARCHAR(100) NOT NULL,
        password VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        role VARCHAR(20) NOT NULL DEFAULT 'user',
        PRIMARY KEY(id),
        CONSTRAINT unique_users_email UNIQUE(email),
        CONSTRAINT check_valid_email CHECK (email LIKE '_%@_%._%'),
        CONSTRAINT check_valid_role CHECK (role in ('user','admin'))
        );""")
        conn.commit()
    except errors.Error as error:
        return {"error": f"{error}"}
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    createUsers()
    createTasks()
