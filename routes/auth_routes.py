from flask import Blueprint, jsonify

auth_bp = Blueprint(
    "auth",
    __name__,
)


@auth_bp.route("/auth", methods=["GET"])
def auth():
    return jsonify({"message": "Hi from the auth route"})
