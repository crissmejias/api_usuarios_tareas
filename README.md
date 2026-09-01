# Proyecto 3: API de tareas con manejo de usuarios

Este proyecto tiene el objetivo de generar aprendizaje en el uso de Flask y la construcción de APIs REST en un ambiente de desarrollo un poco más profesional.

## Arrancar el contenedor en el puerto 5000 y linkear a la carpeta de desarrollo

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