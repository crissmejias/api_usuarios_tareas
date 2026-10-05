from flask import jsonify
from jwt import ExpiredSignatureError, InvalidTokenError
from psycopg2 import errors
from werkzeug import exceptions


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

    @app.errorhandler(InvalidTokenError)
    def handle_jwt_invalid_error(error):
        return jsonify({"code": 401, "message": "Invalid Token!", "data": None}), 401

    @app.errorhandler(ExpiredSignatureError)
    def handle_jwt_expired_token_error(error):
        return jsonify({"code": 401, "message": "Expired token!", "data": None}), 401
    @app.errorhandler(exceptions.HTTPException)
    def handle_http_exception(error):
        return jsonify({"code": int(error.code), "message": error.description , "data": None}), error.code
    @app.errorhandler(Exception)
    def handle_general_exception(error):
        return jsonify({"code": 500, "message": "Something went wrong!", "data": None}), 500
