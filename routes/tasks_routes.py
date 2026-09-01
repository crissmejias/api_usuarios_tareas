from flask import Blueprint, jsonify

tasks_bp = Blueprint(
    "tasks",
    __name__,
)


@tasks_bp.route("/tasks", methods=["GET"])
def list_tasks():
    return jsonify({"message": "This is the tasks route"}), 200


@tasks_bp.route("/tasks/<int:id>", methods=["GET"])
def bring_unique_task(id):
    return jsonify({"message": f"This is a task with ID {id}"}), 200


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    return jsonify({"message": "A new task was created"}), 201


@tasks_bp.route("/tasks/<int:id>", methods=["PUT"])
def edit_task(id):
    return jsonify({"message": f"The task with ID {id} was modified"}), 200


@tasks_bp.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    return "", 204
