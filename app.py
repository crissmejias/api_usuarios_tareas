from flask import Flask

# Routes imports
from routes.auth_routes import auth_bp
from routes.tasks_routes import tasks_bp
from routes.users_routes import users_bp

# Error handler import
from utils.handlers import register_error_handlers

app = Flask(__name__)
app.json.ensure_ascii = False

# Adding Error Handlers
register_error_handlers(app)


# Registering blueprints
app.register_blueprint(tasks_bp)
app.register_blueprint(users_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
