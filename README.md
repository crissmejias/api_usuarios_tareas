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

## 2. Schema de tasks

Qué debe gestionar: título, estado completado y fecha de creación, más la relación con su dueño — una foreign key hacia `users`.

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

### Relación entre ambas tablas

Se decidió `ON DELETE CASCADE` en la foreign key `user_id`: si un usuario se elimina, sus tareas se eliminan automáticamente junto con él, evitando tareas huérfanas sin dueño.

## 3. API de usuarios (`users_bp`)

CRUD completo sobre el recurso `users`, con validación de campos y respuestas JSON consistentes (`{code, message, data}`).

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/users` | Crea un usuario. Valida `name`, `email`, `password`. Hashea el password con `bcrypt` antes de guardarlo. |
| PUT | `/users/<id>` | Actualiza `name` y `email` (reemplazo completo). 404 si el id no existe. |
| DELETE | `/users/<id>` | Elimina un usuario. 404 si el id no existe. |

## 4. Autenticación (`auth_bp`)

Autenticación basada en JWT (JSON Web Tokens), sin manejo de sesiones/estado en el servidor.

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/login` | Recibe `email` y `password`. Verifica contra el hash guardado con `bcrypt.checkpw`. Devuelve un JWT firmado (`HS256`, expira en 15 min) junto con los datos del usuario (sin el password). |

**Detalles de la implementación:**

- El password nunca se compara en SQL — se trae el hash por `email` y se compara en Python con `bcrypt.checkpw`.
- Ante credenciales inválidas (email inexistente o password incorrecto), la respuesta es siempre la misma (`401`, mensaje genérico) para evitar enumeración de usuarios.
- El secret de firma vive en `.env` (variable `SECRET`), generado con `secrets.token_hex(32)` para cumplir la longitud mínima recomendada por RFC 7518 para HS256.
- El payload del JWT contiene únicamente `user_id` y `exp` (expiración) — nunca datos sensibles, ya que el payload de un JWT no está encriptado, solo firmado.

### Decorator `@require_auth`

Protege rutas exigiendo un header `Authorization: Bearer <token>`. Decodifica el token, valida la firma y expiración, e inyecta el `user_id` autenticado como primer argumento de la función de la ruta — el `user_id` **nunca** se toma de la URL ni del body, para evitar vulnerabilidades tipo IDOR (que un usuario acceda o modifique datos de otro).

Las excepciones de PyJWT (`ExpiredSignatureError`, `InvalidTokenError`) no se capturan localmente en el decorator: se propagan y son manejadas por los error handlers globales de la app, devolviendo `401` con un mensaje específico según el caso.

## 5. API de tareas (`tasks_bp`)

CRUD completo sobre el recurso `tasks`, protegido en su totalidad con `@require_auth`. Cada tarea pertenece a un usuario (`user_id`), y todas las operaciones de lectura, edición y borrado están filtradas por el usuario autenticado — un usuario no puede ver, editar ni borrar tareas de otro.

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/tasks` | Lista las tareas del usuario autenticado. |
| GET | `/tasks/<id>` | Trae una tarea puntual, solo si pertenece al usuario autenticado. 404 si no existe o no le pertenece. |
| POST | `/tasks` | Crea una tarea. Valida `title`. |
| PUT | `/tasks/<id>` | Actualiza `title` y `completed` (reemplazo completo). Valida presencia de ambos campos — `completed` se chequea con `is None` para no confundir `false` con "campo ausente". 404 si no existe o no pertenece al usuario. |
| DELETE | `/tasks/<id>` | Elimina una tarea, solo si pertenece al usuario autenticado. 404 si no existe o no le pertenece. |

## Pendientes

- **Cambio de rol**: la tabla `users` no incluye actualmente una columna de rol (`user`/`admin`). Falta definir el schema (columna `role`, valores permitidos) y la lógica de autorización asociada — quién puede cambiar el rol de otro usuario, y qué endpoints quedarían restringidos a `admin`.
- **JWT refresh**: El JWT expira a los 15 minutos. Falta implementar un proceso para que se refresque automáticamente sin volver a hacer login.
- **Testing**: por ahora todo el CRUD (`users`, `tasks`, `auth`) fue probado manualmente con Posting. Falta una rama dedicada para introducir `pytest`, fixtures, y una base de datos de test separada (contenedor Docker sin volumen, para partir de un estado limpio en cada corrida).
- **Robustez del header `Authorization`**: el parseo del header (`split(" ")`) no valida el formato antes de hacer el unpacking — un header malformado (sin espacio, vacío) podría lanzar un error no controlado. Pendiente blindarlo.