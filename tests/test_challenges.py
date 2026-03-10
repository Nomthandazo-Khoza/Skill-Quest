"""
Tests for challenge list, detail, and admin CRUD (create, edit, delete).
"""
import pytest
from tests.conftest import login, register_user


def test_challenges_list_public(client):
    """Anyone can view the challenges list."""
    r = client.get("/challenges")
    assert r.status_code == 200
    assert b"Challenge" in r.data or b"challenge" in r.data


def test_challenge_detail_public(client, app):
    """Challenge detail requires an existing challenge; 404 for missing."""
    r = client.get("/challenges/99999")
    assert r.status_code == 404


def test_admin_create_challenge(client):
    """Admin can create a challenge and is redirected to admin challenges list."""
    register_user(client, "Admin", "admin@test.com", "pass12", "Admin")
    login(client, "admin@test.com", "pass12")
    r = client.post("/admin/challenges/create", data={
        "title": "Test Challenge",
        "description": "Do something.",
        "category": "Testing",
        "difficulty": "Easy",
        "deadline": "",
        "submit": "Save Challenge",
    }, follow_redirects=False)
    assert r.status_code == 302
    assert "admin/challenges" in r.headers["Location"]
    r2 = client.get("/challenges")
    assert r2.status_code == 200
    assert b"Test Challenge" in r2.data


def test_admin_edit_challenge(client):
    """Admin can edit a challenge."""
    register_user(client, "Admin", "admin2@test.com", "pass12", "Admin")
    login(client, "admin2@test.com", "pass12")
    client.post("/admin/challenges/create", data={
        "title": "To Edit",
        "description": "Original",
        "category": "Cat",
        "difficulty": "Medium",
        "deadline": "",
        "submit": "Save Challenge",
    }, follow_redirects=True)
    r = client.get("/challenges")
    assert b"To Edit" in r.data
    # Get first challenge link - we assume id 1
    r_edit = client.post("/admin/challenges/1/edit", data={
        "title": "Edited Title",
        "description": "Updated description",
        "category": "Cat",
        "difficulty": "Hard",
        "deadline": "",
        "submit": "Save Challenge",
    }, follow_redirects=False)
    assert r_edit.status_code == 302
    r_check = client.get("/challenges/1")
    assert r_check.status_code == 200
    assert b"Edited Title" in r_check.data
    assert b"Updated description" in r_check.data


def test_admin_delete_challenge(client):
    """Admin can delete a challenge."""
    register_user(client, "Admin", "admin3@test.com", "pass12", "Admin")
    login(client, "admin3@test.com", "pass12")
    client.post("/admin/challenges/create", data={
        "title": "To Delete",
        "description": "Desc",
        "category": "X",
        "difficulty": "Easy",
        "deadline": "",
        "submit": "Save Challenge",
    }, follow_redirects=True)
    r = client.post("/admin/challenges/1/delete", follow_redirects=False)
    assert r.status_code == 302
    r2 = client.get("/challenges/1")
    assert r2.status_code == 404
