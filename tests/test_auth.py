"""
Tests for registration, login, logout, and role-based redirects.
"""
import pytest
from tests.conftest import login, register_user


def test_register_success(client):
    """Registration with valid data redirects to login."""
    r = register_user(client, "Test Student", "student@test.com", "password123", "Student")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/login")
    # Login with new user (follow_redirects=False to assert redirect)
    r2 = login(client, "student@test.com", "password123", follow_redirects=False)
    assert r2.status_code == 302
    assert "/student" in r2.headers["Location"] or "dashboard" in r2.headers["Location"]


def test_register_duplicate_email(client):
    """Duplicate email shows error and does not redirect."""
    register_user(client, "First", "same@test.com", "pass123", "Student")
    r = register_user(client, "Second", "same@test.com", "other456", "Student")
    assert r.status_code == 200
    assert b"already registered" in r.data or b"already" in r.data.lower()


def test_login_success_student(client):
    """Student can log in and is redirected to student dashboard."""
    register_user(client, "Student User", "s@test.com", "secret", "Student")
    r = login(client, "s@test.com", "secret", follow_redirects=False)
    assert r.status_code == 302
    assert "student" in r.headers["Location"].lower()


def test_login_success_admin(client):
    """Admin can log in and is redirected to admin dashboard."""
    register_user(client, "Admin User", "admin@test.com", "secret", "Admin")
    r = login(client, "admin@test.com", "secret", follow_redirects=False)
    assert r.status_code == 302
    assert "admin" in r.headers["Location"].lower()


def test_login_wrong_password(client):
    """Wrong password does not log in."""
    register_user(client, "User", "u@test.com", "correct", "Student")
    r = login(client, "u@test.com", "wrong")
    assert r.status_code == 200
    assert b"Invalid" in r.data or b"invalid" in r.data.lower()


def test_logout(client):
    """After logout, protected page redirects to login."""
    register_user(client, "U", "logout@test.com", "pass12", "Student")
    login(client, "logout@test.com", "pass12")
    r = client.get("/logout", follow_redirects=False)
    assert r.status_code in (302, 200)
    r2 = client.get("/student/dashboard", follow_redirects=False)
    assert r2.status_code == 302
    assert "login" in r2.headers["Location"].lower()


def test_role_redirect_mentor(client):
    """Mentor is redirected to mentor dashboard after login."""
    register_user(client, "Mentor User", "mentor@test.com", "pass12", "Mentor")
    r = login(client, "mentor@test.com", "pass12", follow_redirects=False)
    assert r.status_code == 302, f"expected redirect, got {r.status_code}"
    assert "mentor" in r.headers.get("Location", "").lower()
