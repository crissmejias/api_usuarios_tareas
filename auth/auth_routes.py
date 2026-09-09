from flask import Blueprint, jsonify, request

from .auth_storage import auth_user
from .jwt_handler import create_jwt

auth_bp = Blueprint(
    "auth",
    __name__,
)


@auth_bp.route("/login", methods=["POST"])
def auth():
    req = request.get_json()
    if not req or not req.get("email") or not req.get("password"):
        return jsonify(
            {"code": 400, "message": "There are missing fields!", "data": None}
        ), 400
    user = auth_user(req)
    if not user:
        return jsonify(
            {"code": 401, "message": "Invalid credentials!", "data": None}
        ), 401
    token = create_jwt(user)
    return jsonify(
        {"code": 200, "token": token, "data": user, "message": "Success!"}
    ), 200
