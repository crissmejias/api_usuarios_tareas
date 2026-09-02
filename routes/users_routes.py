from flask import Blueprint, jsonify

users_bp = Blueprint(
    "users",
    __name__,
)


@users_bp.route("/users", methods=["GET"])
def users():
    return jsonify({"message": "Hi from the users routes"}), 200
