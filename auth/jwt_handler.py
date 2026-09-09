import os
from datetime import datetime, timedelta

import jwt
from dotenv import load_dotenv


def create_jwt(user):
    load_dotenv()
    secret = os.getenv("SECRET")
    payload = {"user_id": user["id"], "exp": datetime.now() + timedelta(minutes=15)}
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token
