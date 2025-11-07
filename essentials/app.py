import logging
from datetime import timedelta

from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from database import db  # your SQLAlchemy() instance

# Import blueprints (exported from routes/*.py)
from routes.admin import bp as admin_bp
from routes.user import bp as users_bp
from routes.game import bp as games_bp
from routes.session import bp as sessions_bp
logging.basicConfig(level=logging.INFO)

def create_app(config_override: dict | None = None) -> Flask:
    app = Flask("FlaskWeb")

    # Base config
    app.config.update(
        SECRET_KEY="mysecretkey123",
        SQLALCHEMY_DATABASE_URI="sqlite:///VR3.db",
        REMEMBER_COOKIE_DURATION=timedelta(minutes=30),
        JSON_AS_ASCII=False,  # keep Chinese messages readable
    )
    if config_override:
        app.config.update(config_override)

    # Init extensions
    CORS(app, supports_credentials=True)
    db.init_app(app)
    Migrate(app, db)

    # Register blueprints (prefixes live in each blueprint or set them here)
    app.register_blueprint(admin_bp)  # e.g. url_prefix in routes.admin: "/api/admin"
    app.register_blueprint(users_bp)  # e.g. "/api"
    app.register_blueprint(games_bp)  # e.g. "/api"
    app.register_blueprint(sessions_bp)  # e.g. "/api"

    return app

