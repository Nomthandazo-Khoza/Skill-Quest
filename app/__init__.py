"""
SkillQuest - Flask application factory.
Creates and configures the Flask app, initializes extensions (SQLAlchemy, LoginManager),
and registers blueprints/routes.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config=None):
    """Application factory: create and configure the Flask app."""
    app = Flask(__name__, instance_relative_config=True)

    # Default configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    instance_path = os.path.join(app.root_path, "..", "instance")
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, "skillquest.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.abspath(db_path),
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to access this page."

    with app.app_context():
        from app import models  # noqa: F401 - register models for create_all
        from app import routes

        @login_manager.user_loader
        def load_user(user_id):
            return models.User.query.get(int(user_id))

        db.create_all()
        _seed_roles()
        _migrate_submission_phase4()
        app.register_blueprint(routes.bp)

    return app


def _seed_roles():
    """Create default roles if they do not exist."""
    if models.Role.query.first() is None:
        for name in ("Student", "Mentor", "Admin"):
            db.session.add(models.Role(name=name))
        db.session.commit()


def _migrate_submission_phase4():
    """Phase 4: add feedback and reviewed_at to submission if table exists and columns are missing."""
    from sqlalchemy import text
    for col_sql in (
        "ALTER TABLE submission ADD COLUMN feedback TEXT",
        "ALTER TABLE submission ADD COLUMN reviewed_at DATETIME",
    ):
        try:
            db.session.execute(text(col_sql))
            db.session.commit()
        except Exception:
            db.session.rollback()
