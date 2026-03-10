# SkillQuest

A web-based student skill-building platform. Students participate in weekly challenges, submit work, receive scores, and track progress.

## Technologies

- **Flask** – web framework
- **Flask-Login** – session and login state (Phase 2)
- **Flask-SQLAlchemy** – database ORM with SQLite
- **Flask-WTF** – forms and validation
- **Jinja2** – templates
- **Bootstrap 5** – styling

## Project structure

```
skillquest/
├── app/
│   ├── __init__.py      # Application factory, db init, table creation, role seeding
│   ├── models.py        # Role, User, Challenge, Submission; One-to-Many & Many-to-Many
│   ├── forms.py         # RegistrationForm, LoginForm, ChallengeForm, SubmissionForm
│   ├── routes.py        # Routes, GET/POST, CRUD, flash, redirects, role-based access
│   ├── templates/       # Jinja2 + Bootstrap pages
│   └── static/css/
├── instance/            # SQLite DB created here (skillquest.db)
├── run.py               # Entry point
├── requirements.txt
└── README.md
```

## Setup and run (local)

1. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**

   The database and tables are created automatically on first run. Default roles (Student, Mentor, Admin) are seeded in `app/__init__.py` when the app starts. If you had a database from before Phase 2, delete `instance/skillquest.db` so the app can create tables with the updated schema (e.g. `User.password_hash`).

4. **Run the application**

   ```bash
   python run.py
   ```

   Then open http://127.0.0.1:5000 in your browser.

## Commands summary

| Action              | Command              |
|---------------------|----------------------|
| Install dependencies| `pip install -r requirements.txt` |
| Run the app         | `python run.py`      |

Database file: `instance/skillquest.db` (created on first run).

## Course concepts covered

- **Flask application factory** – `create_app()` in `app/__init__.py`
- **Flask-SQLAlchemy** – models, `db.create_all()`, relationships
- **SQLite** – default `SQLALCHEMY_DATABASE_URI`
- **Flask-WTF** – forms in `forms.py`, CSRF, validation
- **Jinja2** – `base.html`, `{% block %}`, `url_for()`, flash messages
- **Bootstrap** – layout and components in templates
- **Routes and views** – `routes.py` with Blueprint
- **GET/POST** – form actions and `methods=["GET", "POST"]`
- **CRUD** – Create (register, create challenge, submit), Read (dashboards, challenge list/detail), Update/Delete (later phases)
- **Flash messages and redirects** – after login, register, create, submit
- **Database relationships** – One-to-Many (Role–User, User–Challenge, User–Submission, Challenge–Submission), Many-to-Many (User–Challenge via `challenge_participants`)
- **Security** – hashed passwords (Werkzeug), secret key, role-based access
- **Phase 2 – Authentication** – Flask-Login (`login_user`, `logout_user`, `current_user`, `login_required`), `User.password_hash`, role-based redirects, protected routes, flash messages for auth
- **Phase 4 – Submissions & scoring** – Submission model (feedback, reviewed_at), SubmissionForm, ReviewSubmissionForm, my-submissions, admin review (score, status, feedback), CRUD on submissions
- **Phase 5 – Progress tracking** – Progress calculated from Submission + Challenge (no new model); student dashboard stats (total/reviewed/pending submissions, total/avg score, completion rate); student progress-by-challenge page; admin and mentor progress overview and per-student detail

## Roles

- **Student** – view challenges, submit, see own submissions and progress (dashboard + My Progress)
- **Mentor** – view challenges, view submissions and student progress (read-only)
- **Admin** – manage challenges, review submissions, view all student progress
