from flask import Blueprint, jsonify, request
from auth.jwt_handler import require_admin, require_auth 
from storage import users_storage

users_bp = Blueprint(
    "users",
    __name__,
)


@users_bp.route("/users", methods=["GET"])
@require_auth
@require_admin
def get_users(user_id):
    users = users_storage.list_users()
    return jsonify({"code": 200, "message": "success", "data": users}), 200


@users_bp.route("/users/<int:id>", methods=["GET"])
@require_auth
@require_admin
def get_single_user(user_id, id):
    single_user = users_storage.list_user(id)
    if not single_user:
        return jsonify(
            {"code": 404, "message": "The user does not exist", "data": None}
        ), 404
    return jsonify({"code": 200, "message": "success", "data": single_user}), 200


@users_bp.route("/users", methods=["POST"])
@require_auth
@require_admin
def create_user(user_id):
    req = request.get_json()
    if (
        not req
        or not req.get("name")
        or not req.get("email")
        or not req.get("password")
    ):
        return jsonify(
            {"code": 400, "message": "There are missing fields!", "data": None}
        ), 400
    response = users_storage.create_user(req)
    return jsonify({"code": 201, "message": "success", "data": response}), 201


@users_bp.route("/users/<int:id>", methods=["PUT"])
@require_auth
@require_admin
def edit_user(user_id, id):
    req = request.get_json()
    if not req or not req.get("name") or not req.get("email"):
        return jsonify(
            {"code": 400, "message": "There are missing fields!", "data": None}
        ), 400
    response = users_storage.edit_user(req, id)
    if response:
        return jsonify({"code": 200, "message": "success", "data": response}), 200
    return jsonify({"code": 404, "message": "The ID does not exist", "data": None}), 404


@users_bp.route("/users/<int:id>", methods=["DELETE"])
@require_auth
@require_admin
def delete_user(user_id, id):
    valid_deletion = users_storage.delete_user(id)
    if valid_deletion:
        return "", 204
    return jsonify({"code": 404, "message": "The ID does not exist", "data": None}), 404
