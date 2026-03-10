---
name: SkillQuest gaps and next steps
overview: "Address the main gaps from the detailed status: quick UX/config fixes, automatic Late status and deadline validation, and add a test suite so the project can be extended safely."
todos: []
isProject: false
---

# SkillQuest – Plan: Gaps and Next Steps

This plan addresses the **missing or inconsistent** items from your detailed status so you can proceed from the current state. It is split into three parts: quick fixes, submission/deadline behavior, and tests. User management, file upload, and submission delete are left as optional follow-ups.

---

## Part 1: Quick fixes (UX and copy)

**1.1 Nav links for Admin and Mentor**

- **File:** [app/templates/base.html](app/templates/base.html)
- **Change:** In the `{% if current_user.is_authenticated %}` block, add role-specific nav items (after the existing Student-only block):
  - **Admin:** show links to "Challenges" (admin list), "Submissions", "Progress" (e.g. `url_for('main.admin_challenges_list')`, `admin_submissions_list`, `admin_progress`).
  - **Mentor:** show links to "Submissions" and "Progress" (e.g. `url_for('main.mentor_submissions_list')`, `main.mentor_progress`).
- Keep a single "Dashboard" link for each role as well, so behavior stays consistent.

**1.2 Mentor dashboard copy**

- **File:** [app/templates/mentor_dashboard.html](app/templates/mentor_dashboard.html)
- **Change:** Replace the footer card text "Grading & feedback (coming later)" and the short description with something like: "You can view all submissions and student progress. Only admins can score and give feedback." so it’s clear mentors are read-only.

**1.3 Optional: deadline validation in form**

- **File:** [app/forms.py](app/forms.py)
- **Change:** Add an optional validator for `ChallengeForm.deadline` (e.g. a custom validator or use a pattern/regex for `YYYY-MM-DD`) so invalid dates are caught at form level. Keep the existing try/except parsing in [app/routes.py](app/routes.py) as fallback and flash a message if parsing fails despite validation (e.g. edge cases).

---

## Part 2: Automatic "Late" status and deadline handling

**2.1 Set "Late" when submitting after deadline**

- **File:** [app/routes.py](app/routes.py)
- **Where:** In `submit_challenge` (POST branch, when creating the `Submission`).
- **Logic:** After building the submission object, if `challenge.deadline` is set and `datetime.utcnow() > challenge.deadline`, set `submission.status = "Late"` instead of `"Pending"`. Optionally flash a message like "Submitted after the deadline; marked as Late."

**2.2 Optional: show deadline in submission/review**

- **Files:** [app/templates/submission_detail.html](app/templates/submission_detail.html), [app/templates/review_submission.html](app/templates/review_submission.html) (if you show challenge info there).
- **Change:** Ensure the challenge’s deadline is displayed where the submission is shown so admins/mentors can see why a submission might be Late. No model changes required.

---

## Part 3: Tests

**3.1 Setup**

- Add `pytest`, `pytest-cov` (optional), and `flask-testing` or use plain Flask `app.test_client()` to `requirements.txt` or a `requirements-dev.txt`.
- Create a test config (e.g. in `config.py` or inside `create_app`) that uses an in-memory SQLite DB (`sqlite:///:memory:`) and a fixed `SECRET_KEY` so tests don’t touch `instance/skillquest.db`.

**3.2 Application factory for tests**

- **File:** [app/**init**.py](app/__init__.py) or a small `conftest.py` in a `tests/` package.
- **Idea:** `create_app(config={'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', ...})` so each test run gets a clean DB. Ensure `db.create_all()` and `_seed_roles()` run in that context (they already do when the app is created).

**3.3 Test modules (high level)**

- **tests/test_auth.py:** Registration (success, duplicate email), login (success, wrong password), logout, and role-based redirect after login (Student → student dashboard, etc.). Use `client.post('/register', data=...)`, `client.post('/login', data=...)`, then `client.get('/student/dashboard')` and assert redirect or 200 as appropriate.
- **tests/test_challenges.py:** List challenges (public), challenge detail; admin create/edit/delete (create challenge, then GET edit form, POST update, POST delete) with an admin user logged in (create user with Admin role in setUp).
- **tests/test_submissions.py:** Student submit (POST to `/challenges/<id>/submit`), list my-submissions, view own submission; admin list submissions, open review form, POST review (score, status, feedback) and assert `reviewed_at` and status/score in DB or on next GET.
- **tests/test_progress.py:** Create a student, a challenge, and a submission; GET student progress page and admin/mentor progress pages; assert key stats (e.g. total_submissions, reviewed_count) appear in response or in a structured way you can parse.

**3.4 Running tests**

- Document in README: e.g. `pytest tests/ -v` and optionally `pytest --cov=app tests/`.

---

## Optional follow-ups (not in this plan)

- **User management:** Admin edit/delete (or deactivate) users — new routes, forms, and templates; decide whether to soft-delete or hard-delete.
- **Submission delete:** Single route e.g. `POST /admin/submissions/<id>/delete` with CSRF and role check; link from admin submission detail.
- **File upload:** Use `FileField` in `SubmissionForm`, configure upload folder and `Submission.file_name` (or a new field) to store filename; serve files via a safe route (no path traversal).

---

## Order of implementation

1. Part 1 (quick fixes) — nav, mentor copy, optional deadline validator.
2. Part 2 (Late + deadline) — set Late on submit, optional deadline display in templates.
3. Part 3 (tests) — config, then auth, challenges, submissions, progress.

After this, the app will have consistent nav for all roles, correct mentor messaging, optional form-level deadline validation, automatic Late status, and a test suite to protect future changes.