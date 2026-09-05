from psycopg2 import errors

def register_error_handlers(app):
    @app.errorhandler(errors.UniqueViolation)
    def handle_duplicate_emails(error):
        return {"error": f"{error}"},409
    @app.errorhandler(errors.Error)
    def handle_general_error(error):
        return {"error": f"{error}"},500