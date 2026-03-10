# SkillQuest – Project Notes

This document explains what SkillQuest is, what’s in the project, and how to use it. It’s written so that anyone can understand the project without needing a technical background.

---

## What is SkillQuest?

**SkillQuest** is a web application for running a **student skill-building program**. The idea is:

- **Students** see a list of challenges (e.g. weekly tasks), submit their work, and see their scores and progress.
- **Mentors** can view all challenges, all submissions, and each student’s progress (read-only; they don’t grade).
- **Admins** create and edit challenges, review and score submissions, and see progress for all students.

So: students do the work, admins manage content and grading, and mentors can observe without changing anything.

---

## What Can Each Person Do?

### Students
- Register and log in.
- See all available challenges (title, description, category, difficulty, deadline).
- Submit an answer to a challenge (text and optional file name).
- See their own list of submissions and each submission’s status (e.g. Pending, Reviewed, Late).
- See their progress: how many challenges they’ve done, how many are reviewed, total and average score, completion rate.
- If they submit after the challenge deadline, that submission is automatically marked as **Late**.

### Mentors
- Log in (no registration of “mentor” by students; an admin or setup process would create mentor accounts).
- See all challenges.
- See all submissions (read-only).
- See progress for all students and for each student in detail.
- They **cannot** create challenges, edit challenges, or give scores/feedback.

### Admins
- Do everything mentors can, plus:
- Create new challenges (title, description, category, difficulty, optional deadline).
- Edit and delete existing challenges.
- Open any submission and **review** it: set a score (0–100), status (e.g. Reviewed, Late, Rejected), and written feedback.
- See all students and their progress in one place, and drill into any student’s detail.

---

## Main Parts of the Project (In Simple Terms)

### The Website (What You See)
- **Home page** – Short intro; if you’re logged in, you’re sent to your role’s dashboard.
- **Login / Register** – Sign in or create an account (you choose your role when registering).
- **Challenges** – A public list of all challenges; from here you can open one and (if you’re a student) submit.
- **Dashboards** – One per role (Student, Mentor, Admin) with links to the right sections.
- **My Submissions / My Progress** – For students only: list of their submissions and progress by challenge.
- **Admin areas** – Manage challenges, review submissions, view all progress.

The site uses **Bootstrap** for layout and styling so it works on different screen sizes.

### The Data the App Keeps
- **Users** – Name, email, password (stored securely), and role (Student, Mentor, Admin).
- **Challenges** – Title, description, category, difficulty, optional deadline, and who created them.
- **Submissions** – Who submitted, for which challenge, the answer text, optional file name, score, status, feedback, and when it was submitted and reviewed.

Progress (e.g. “how many challenges completed”, “average score”) is **calculated** from challenges and submissions; there is no separate “progress” table.

### Where Things Live in the Project
- **`app/`** – Core application code:
  - **`models.py`** – Defines users, roles, challenges, and submissions (the “shape” of the data).
  - **`forms.py`** – Defines the forms (register, login, create/edit challenge, submit answer, review submission) and their validation rules.
  - **`routes.py`** – Connects URLs to actions (e.g. “when someone goes to /challenges, show the challenge list”).
  - **`templates/`** – The HTML pages (one per screen, using a shared layout and navigation).
  - **`static/css/`** – Extra styling if needed.
- **`instance/`** – The database file (`skillquest.db`) is created here when you run the app for the first time. You can delete this file to start with a fresh database.
- **`run.py`** – The script you run to start the app.
- **`requirements.txt`** – List of Python packages the app needs.
- **`requirements-dev.txt`** – Extra packages for running tests.
- **`tests/`** – Automated tests that check that registration, login, challenges, submissions, and progress work as expected.

Nothing here is “magic”: it’s a normal Python web app that uses a small database (SQLite) and a set of web pages and forms.

---

## How to Run the Project

1. **Install Python** (if needed) and open a terminal in the project folder.
2. **Create a virtual environment** (recommended):
   - `python -m venv venv`
   - On Windows: `venv\Scripts\activate`
   - On Mac/Linux: `source venv/bin/activate`
3. **Install dependencies:**  
   `pip install -r requirements.txt`
4. **Start the app:**  
   `python run.py`
5. **Open a browser** and go to: **http://127.0.0.1:5000**

The first time you run it, the app will create the database and the default roles (Student, Mentor, Admin). You can then register users with different roles and try the flows above.

---

## Running Tests

If you want to check that the app still works after changes:

1. Install test dependencies:  
   `pip install -r requirements-dev.txt`
2. Run tests:  
   `pytest tests/ -v`

The tests use a temporary in-memory database so your real data is not touched.

---

## Features That Are Implemented

- User registration and login (with role).
- Student: view challenges, submit, see own submissions and progress.
- Mentor: view challenges, submissions, and student progress (read-only).
- Admin: create/edit/delete challenges, review submissions (score, status, feedback), view all progress.
- Optional deadline on challenges; submissions after the deadline are marked **Late**.
- Challenge deadline shown on submission and review pages so reviewers can see why something might be Late.
- Optional date validation on the challenge form (deadline must be YYYY-MM-DD if provided).
- Navigation in the top bar that changes by role (e.g. Admins see links to Challenges, Submissions, Progress).

---

## What Is Not in the Project (Yet)

- **User management** – Admins cannot yet edit or delete user accounts (mentioned as “later” in the app).
- **Real file upload** – Submissions have an optional “file name” field only; no actual file is stored.
- **Deleting a single submission** – You can delete a challenge (and its submissions), but there is no “delete this submission” button for admins.
- **Automatic “Late” only on submit** – If a deadline is added after a submission, that submission is not automatically updated to Late; an admin can set status to Late when reviewing.

---

## Quick Reference

| I want to…              | Do this…                                      |
|-------------------------|-----------------------------------------------|
| Run the app             | `python run.py` then open http://127.0.0.1:5000 |
| Run tests               | `pytest tests/ -v`                             |
| Start with a fresh DB   | Delete the file `instance/skillquest.db`      |
| Install app packages    | `pip install -r requirements.txt`            |
| Install test packages   | `pip install -r requirements-dev.txt`        |

---

If you need more technical detail (e.g. exact URLs, database schema, or code structure), see **README.md** in the same folder.
