from flask import jsonify
from psycopg2 import errors


def register_error_handlers(app):
    @app.errorhandler(errors.UniqueViolation)
    def handle_duplicate_emails(error):
        return jsonify(
            {"code": 409, "message": "The email was already registered!", "data": None}
        ), 409

    @app.errorhandler(errors.Error)
    def handle_general_error(error):
        return jsonify(
            {"code": 500, "message": "Something went wrong!", "data": None}
        ), 500
