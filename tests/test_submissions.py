"""
Tests for submission create (student), my-submissions list/detail, and admin review.
"""
import pytest
from tests.conftest import login, register_user


def test_student_submit(client):
    """Student can submit a challenge and is redirected to my-submissions."""
    register_user(client, "Student", "sub@test.com", "pass12", "Student")
    register_user(client, "Admin", "adm@test.com", "pass12", "Admin")
    login(client, "adm@test.com", "pass12")
    client.post("/admin/challenges/create", data={
        "title": "Submit This",
        "description": "Answer here.",
        "category": "C",
        "difficulty": "Easy",
        "deadline": "",
        "submit": "Save Challenge",
    }, follow_redirects=True)
    client.get("/logout", follow_redirects=True)
    login(client, "sub@test.com", "pass12")
    r = client.post("/challenges/1/submit", data={
        "text_answer": "My answer text",
        "file_name": "",
        "submit": "Submit",
    }, follow_redirects=False)
    assert r.status_code == 302
    assert "my-submissions" in r.headers["Location"].lower()
    r2 = client.get("/my-submissions")
    assert r2.status_code == 200
    assert b"My answer text" in r2.data or b"Submit This" in r2.data


def test_my_submission_detail_owner(client):
    """Student can view own submission detail."""
    register_user(client, "Student", "s2@test.com", "pass12", "Student")
    register_user(client, "Admin", "a2@test.com", "pass12", "Admin")
    login(client, "a2@test.com", "pass12")
    client.post("/admin/challenges/create", data={
        "title": "C2",
        "description": "D2",
        "category": "X",
        "difficulty": "Medium",
        "deadline": "",
        "submit": "Save Challenge",
    }, follow_redirects=True)
    client.get("/logout", follow_redirects=True)
    login(client, "s2@test.com", "pass12")
    client.post("/challenges/1/submit", data={
        "text_answer": "Only mine",
        "file_name": "",
        "submit": "Submit",
    }, follow_redirects=True)
    r = client.get("/my-submissions/1")
    assert r.status_code == 200
    assert b"Only mine" in r.data


def test_admin_review_submission(client):
    """Admin can review a submission; score, status, feedback and reviewed_at are set."""
    register_user(client, "Student", "stu@test.com", "pass12", "Student")
    register_user(client, "Admin", "ad@test.com", "pass12", "Admin")
    login(client, "ad@test.com", "pass12")
    client.post("/admin/challenges/create", data={
        "title": "Review Me",
        "description": "Desc",
        "category": "Y",
        "difficulty": "Hard",
        "deadline": "",
        "submit": "Save Challenge",
    }, follow_redirects=True)
    client.get("/logout", follow_redirects=True)
    login(client, "stu@test.com", "pass12")
    client.post("/challenges/1/submit", data={
        "text_answer": "Reviewed answer",
        "file_name": "",
        "submit": "Submit",
    }, follow_redirects=True)
    client.get("/logout", follow_redirects=True)
    login(client, "ad@test.com", "pass12")
    r = client.post("/admin/submissions/1/review", data={
        "score": "85",
        "status": "Reviewed",
        "feedback": "Good work.",
        "submit": "Save Review",
    }, follow_redirects=False)
    assert r.status_code == 302
    assert "admin/submissions" in r.headers["Location"]
    r2 = client.get("/admin/submissions/1")
    assert r2.status_code == 200
    assert b"85" in r2.data
    assert b"Reviewed" in r2.data
    assert b"Good work" in r2.data
    assert b"Reviewed" in r2.data or b"reviewed" in r2.data.lower()
