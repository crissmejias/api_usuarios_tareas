# Proyecto 3: API de tareas con manejo de usuarios

Este proyecto tiene el objetivo de generar aprendizaje en el uso de Flask y la construcción de APIs REST en un ambiente de desarrollo un poco más profesional.

## Arrancar el contenedor en el puerto 5000 y linkear a la carpeta de desarrollo con Dockerfile

### Dockerfile
```
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python","app.py"]
```

### Comando en bash para crear la imagen y correr el contenedor

```bash
docker build -t "api_usuarios_tareas" . && docker run -it --name api_usuarios_tareas -p 5000:5000 -v .:/app -v /app/venv api_usuarios_tareas
```

## Integración con contenedor para base de datos postgresql usando docker-compose y script para crear la nueva base

### Docker-compose

```yml
services:
  db:
    image: postgres:16
    container_name: postgres_db_api_usuarios_tareas
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "5432:5432"
    volumes:
      - "datos_postgres:/var/lib/postgresql/data"
    env_file:
      - .env 
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 2s
      timeout: 5s
      retries: 5
      start_period: 5s
  api:
   build: .
   ports:
    - "5000:5000"
   environment:
    DB_HOST: db
   env_file:
    - .env
   depends_on:
    db:
      condition: service_healthy
      restart: true
   volumes:
    - .:/app
    - /app/venv
volumes:
  datos_postgres:

```
### Script para realizar la conexión de base de datos

```python
from psycopg2 import connect
import os
from dotenv import load_dotenv


def connect_to_db():
    load_dotenv()
    try:
        conn = connect(
            database=os.getenv("DB_NAME"),
            user="postgres",
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port="5432",
        )
        cursor = conn.cursor()
        return conn, cursor
```

## 1. Schema de users

Qué debe gestionar: identidad del usuario (username, email), credencial (password hasheado), rol para autorización futura (user/admin), y metadato de creación.

```python
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
```

## 2. Schema de tasks

Qué debe gestionar: los mismos datos que ya conoces del proyecto anterior (título, estado completado, fecha de creación), más la relación con su dueño — una foreign key hacia users.

```python
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
        PRIMARY KEY(id),
        CONSTRAINT unique_users_email UNIQUE(email),
        CONSTRAINT check_valid_email CHECK (email LIKE '_%@_%._%')
        );""")
        conn.commit()
    except errors.Error as error:
        return {"error": f"{error}"}
    finally:
        if conn:
            conn.close()
```

3. Relación entre ambas tablas

Antes de escribir el CREATE TABLE de tasks, pensar: ¿qué debería pasar con las tareas de un usuario si ese usuario se elimina? (esto define qué política de ON DELETE usar en la foreign key — es una decisión de diseño, no solo sintaxis).