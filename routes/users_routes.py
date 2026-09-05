from flask import Blueprint, jsonify, request

from storage import users_storage

users_bp = Blueprint(
    "users",
    __name__,
)


@users_bp.route("/users", methods=["GET"])
def get_users():
    users = users_storage.list_users()
    return jsonify({"code": 200, "message": "success", "data": users}), 200


@users_bp.route("/users/<int:id>", methods=["GET"])
def get_single_user(id):
    single_user = users_storage.list_user(id)
    if not single_user:
        return jsonify(
            {"code": 404, "message": "The user does not exist", "data": None}
        ), 404
    return jsonify({"code": 200, "message": "success", "data": single_user}), 200


@users_bp.route("/users", methods=["POST"])
def create_user():
    req = request.get_json()
    if (
        not req or
        not req.get("name") or
        not req.get("email") or
        not req.get("password")
    ):
        return jsonify(
            {"code": 400, "message": "There are missing fields!", "data": None}
        ), 400
    response = users_storage.create_user(req)
    return jsonify({"code": 201, "message": "success", "data": response}), 201
