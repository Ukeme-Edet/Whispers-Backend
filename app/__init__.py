#!/usr/bin/env python3
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    from config import Config
    from flask import Flask

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.routes import api

    # Register the API blueprint with the app disabling strict slashes
    app.register_blueprint(api, url_prefix="/api")

    with app.app_context():
        db.metadata.create_all(db.engine)

    app.url_map.strict_slashes = False
    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User

    return User.query.get(user_id)
