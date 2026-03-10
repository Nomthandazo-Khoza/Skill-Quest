"""
Pytest configuration and fixtures for SkillQuest.
Uses in-memory SQLite and disabled CSRF for testing.
"""
import pytest
from app import create_app
from app import db
from app.models import Role, User
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create application with test config (in-memory DB, no CSRF)."""
    app = create_app(config={
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    # When CSRF is disabled, csrf_token() is not in Jinja context; inject a no-op so templates don't break
    @app.context_processor
    def inject_csrf():
        return {"csrf_token": lambda: ""}
    return app


@pytest.fixture
def client(app):
    """Test client for making requests."""
    return app.test_client()


def login(client, email, password, follow_redirects=True):
    """Log in with email and password. Use follow_redirects=True so session cookie is established."""
    return client.post(
        "/login",
        data={"email": email, "password": password, "submit": "Log In"},
        follow_redirects=follow_redirects,
    )


def register_user(client, full_name, email, password, role_name="Student"):
    """Register a user with the given role. Role IDs from _seed_roles order: Student=1, Mentor=2, Admin=3. Password must be at least 6 chars."""
    role_id = {"Student": 1, "Mentor": 2, "Admin": 3}.get(role_name, 1)
    return client.post("/register", data={
        "full_name": full_name,
        "email": email,
        "password": password,
        "confirm_password": password,
        "role_id": str(role_id),
        "submit": "Register",
    }, follow_redirects=False)


def get_role_id(app, role_name):
    """Return role id by name (for use inside app context)."""
    with app.app_context():
        r = Role.query.filter_by(name=role_name).first()
        return r.id if r else None
