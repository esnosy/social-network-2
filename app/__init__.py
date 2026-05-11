import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv(".env.local")

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DB_URI"]

    db.init_app(app)

    from . import models  # noqa

    with app.app_context():
        db.create_all()

    from .auth import auth_bp

    app.register_blueprint(auth_bp)

    from .main import main_bp

    app.register_blueprint(main_bp)

    return app
