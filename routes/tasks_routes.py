from flask import Blueprint, jsonify, request

from auth.jwt_handler import require_auth
from storage import tasks_storage

tasks_bp = Blueprint(
    "tasks",
    __name__,
)


@tasks_bp.route("/tasks", methods=["GET"])
@require_auth
def list_tasks(user_id):
    tasks = tasks_storage.list_tasks(user_id)
    return jsonify({"code": 200, "message": "Success!", "data": tasks}), 200


@tasks_bp.route("/tasks/<int:id>", methods=["GET"])
@require_auth
def bring_unique_task(user_id, id):
    task = tasks_storage.get_task(user_id, id)
    if not task or not task.get("id"):
        return jsonify(
            {"code": 404, "message": "The task does not exist", "data": None}
        ), 404
    return jsonify({"code": 200, "message": "Success", "data": task}), 200


@tasks_bp.route("/tasks", methods=["POST"])
@require_auth
def create_task(user_id):
    req = request.get_json()
    if not req or not req.get("title"):
        return jsonify(
            {"code": 400, "message": "There are missing fields!", "data": None}
        ), 400
    new_task = tasks_storage.create_task(user_id, req["title"])
    return jsonify({"code": 201, "message": "Success", "data": new_task}), 201


@tasks_bp.route("/tasks/<int:id>", methods=["PUT"])
@require_auth
def edit_task(user_id, id):
    req = request.get_json()
    if not req or not req.get("title") or req.get("completed") is None:
        return jsonify(
            {"code": 400, "message": "There are missing fields!", "data": None}
        ), 400
    edited_task = tasks_storage.edit_task(user_id, id, req)
    if not edited_task:
        return jsonify(
            {"code": 404, "message": "The task does not exist", "data": None}
        ), 404
    return jsonify({"code": 200, "message": "Success!", "data": edited_task}), 200


@tasks_bp.route("/tasks/<int:id>", methods=["DELETE"])
@require_auth
def delete_task(user_id, id):
    confirm_delete = tasks_storage.delete_task(user_id, id)
    if not confirm_delete:
        return jsonify(
            {"code": 404, "message": "The task does not exist", "data": None}
        ), 404
    return "", 204
