import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import jsonify, request


def create_jwt(user):
    load_dotenv()
    secret = os.getenv("SECRET")
    payload = {
        "user_id": user["id"],
        "exp": datetime.now(tz=None) + timedelta(minutes=15),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        load_dotenv()
        secret = os.getenv("SECRET")
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify(
                {"code": 401, "message": "Invalid header!", "data": None}
            ), 401
        # TODO: validar formato del header (auth_header.split(" ")) antes del unpacking
        # para evitar ValueError si el header viene malformado (sin espacio, etc.)
        auth_type, token = auth_header.split(" ")
        if auth_type != "Bearer":
            return jsonify(
                {"code": 401, "message": "Invalid header!", "data": None}
            ), 401
        if not token:
            return jsonify(
                {"code": 401, "message": "No token found!", "data": None}
            ), 401
        data = jwt.decode(token, secret, algorithms=["HS256"])
        return f(data["user_id"], *args, **kwargs)

    return wrapper
