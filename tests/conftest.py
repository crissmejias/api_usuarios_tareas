import os
import re
from itertools import count

import pytest
from dotenv import load_dotenv
from psycopg2 import connect, sql
from psycopg2.extras import RealDictCursor

load_dotenv()

BASE_DB_NAME = os.getenv("DB_NAME", "api_users_tasks")
TEST_DB_NAME = os.getenv("DB_NAME_TEST", f"{BASE_DB_NAME}_test")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")

os.environ.setdefault("SECRET", "test-secret-key-with-at-least-32-bytes")
os.environ.setdefault("ADMIN_EMAIL", "admin@test.local")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")


def _connect(database):
    return connect(
        database=database,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def _ensure_test_database():
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", TEST_DB_NAME):
        raise ValueError(f"Invalid test database name: {TEST_DB_NAME}")

    conn = _connect("postgres")
    conn.autocommit = True
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", [TEST_DB_NAME]
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(TEST_DB_NAME))
                )
    finally:
        conn.close()


def _reset_schema():
    from storage import schemas

    for result in (schemas.createUsers(), schemas.createTasks()):
        if result:
            raise RuntimeError(result["error"])


@pytest.fixture(scope="session", autouse=True)
def test_database():
    previous_db_name = os.environ.get("DB_NAME")

    _ensure_test_database()
    os.environ["DB_NAME"] = TEST_DB_NAME
    _reset_schema()

    yield TEST_DB_NAME

    if previous_db_name is None:
        os.environ.pop("DB_NAME", None)
    else:
        os.environ["DB_NAME"] = previous_db_name


@pytest.fixture(autouse=True)
def clean_database(test_database):
    conn = _connect(test_database)
    try:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE tasks, users RESTART IDENTITY CASCADE")
        conn.commit()
    finally:
        conn.close()

    yield


@pytest.fixture
def client():
    from app import app

    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def user_factory():
    counter = count(1)

    def create(name=None, email=None, role="user"):
        number = next(counter)
        name = name or f"User {number}"
        email = email or f"user{number}@example.com"

        conn = _connect(TEST_DB_NAME)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (name, email, password, role)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, name, email, role
                    """,
                    [name, email, "not-used-in-tests", role],
                )
                created_user = dict(cursor.fetchone())
            conn.commit()
            return created_user
        finally:
            conn.close()

    return create


def _auth_headers_for(user):
    from auth.jwt_handler import create_jwt

    return {"Authorization": f"Bearer {create_jwt(user)}"}


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def other_user(user_factory):
    return user_factory()


@pytest.fixture
def auth_headers(user):
    return _auth_headers_for(user)


@pytest.fixture
def other_auth_headers(other_user):
    return _auth_headers_for(other_user)


@pytest.fixture
def task_factory():
    def create(user_id, title="Default task", completed=False):
        conn = _connect(TEST_DB_NAME)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks (user_id, title, completed)
                    VALUES (%s, %s, %s)
                    RETURNING id, title, completed
                    """,
                    [user_id, title, completed],
                )
                created_task = dict(cursor.fetchone())
            conn.commit()
            return created_task
        finally:
            conn.close()

    return create
