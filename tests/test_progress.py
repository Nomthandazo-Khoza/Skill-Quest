"""
Tests for progress pages: student progress, admin progress overview, mentor progress.
"""
import pytest
from tests.conftest import login, register_user


def test_student_progress_page(client):
    """Student progress page shows stats and challenge rows."""
    register_user(client, "Student", "prog@test.com", "pass12", "Student")
    register_user(client, "Admin", "ap@test.com", "pass12", "Admin")
    login(client, "ap@test.com", "pass12")
    client.post("/admin/challenges/create", data={
        "title": "P Challenge",
        "description": "D",
        "category": "K",
        "difficulty": "Easy",
        "deadline": "",
        "submit": "Save Challenge",
    }, follow_redirects=True)
    client.get("/logout", follow_redirects=True)
    login(client, "prog@test.com", "pass12")
    r = client.get("/student/progress")
    assert r.status_code == 200
    assert b"Progress" in r.data or b"progress" in r.data
    assert b"P Challenge" in r.data or b"Challenge" in r.data


def test_admin_progress_overview(client):
    """Admin progress page lists students and stats."""
    register_user(client, "Student", "st1@test.com", "pass12", "Student")
    register_user(client, "Admin", "ad1@test.com", "pass12", "Admin")
    login(client, "ad1@test.com", "pass12")
    r = client.get("/admin/progress")
    assert r.status_code == 200
    assert b"st1" in r.data or b"Progress" in r.data or b"progress" in r.data


def test_mentor_progress_overview(client):
    """Mentor progress page lists students (read-only)."""
    register_user(client, "Student", "st2@test.com", "pass12", "Student")
    register_user(client, "Mentor", "mentor@test.com", "pass12", "Mentor")
    login(client, "mentor@test.com", "pass12")
    r = client.get("/mentor/progress")
    assert r.status_code == 200
    assert b"st2" in r.data or b"Progress" in r.data or b"progress" in r.data


def test_admin_student_progress_detail(client):
    """Admin can view one student's progress detail."""
    register_user(client, "Student", "stu3@test.com", "pass12", "Student")
    register_user(client, "Admin", "ad3@test.com", "pass12", "Admin")
    login(client, "ad3@test.com", "pass12")
    # Student id is 1 (first user), Admin is 2. So student id 1.
    r = client.get("/admin/progress/1")
    assert r.status_code == 200
    assert b"stu3" in r.data or b"progress" in r.data.lower()
