"""
SkillQuest - Flask routes and views.
Handles GET/POST, CRUD, flash messages, redirects, and role-based access.
Uses Flask-Login for session handling; login_required and require_role for protection.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import Role, User, Challenge, Submission
from app.forms import RegistrationForm, LoginForm, ChallengeForm, SubmissionForm, ReviewSubmissionForm
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("main", __name__)


def require_role(*allowed_roles):
    """Decorator: allow access only if current user has one of the allowed roles. Use after @login_required."""
    def decorator(f):
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("main.login"))
            if allowed_roles and current_user.role.name not in allowed_roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("main.index"))
            return f(*args, **kwargs)
        wrapped.__name__ = f.__name__
        return wrapped
    return decorator


def _redirect_by_role(user):
    """Redirect user to the correct dashboard based on role."""
    if user.role.name == "Admin":
        return redirect(url_for("main.admin_dashboard"))
    if user.role.name == "Mentor":
        return redirect(url_for("main.mentor_dashboard"))
    return redirect(url_for("main.student_dashboard"))


def _student_progress_stats(user_id):
    """Calculate progress stats for a student from Submission and Challenge data. Returns dict."""
    total_challenges = Challenge.query.count()
    user_submissions = Submission.query.filter_by(user_id=user_id).all()
    total_submissions = len(user_submissions)
    reviewed = [s for s in user_submissions if (s.status or "").lower() == "reviewed"]
    pending = [s for s in user_submissions if (s.status or "").lower() == "pending"]
    reviewed_count = len(reviewed)
    pending_count = len(pending)
    completed_challenges = len({s.challenge_id for s in user_submissions})
    total_score = sum(s.score for s in reviewed if s.score is not None)
    scores_count = sum(1 for s in reviewed if s.score is not None)
    average_score = (total_score / scores_count) if scores_count else None
    completion_rate = (completed_challenges / total_challenges * 100) if total_challenges else 0
    return {
        "total_challenges": total_challenges,
        "total_submissions": total_submissions,
        "reviewed_count": reviewed_count,
        "pending_count": pending_count,
        "completed_challenges": completed_challenges,
        "total_score": total_score,
        "average_score": average_score,
        "completion_rate": round(completion_rate, 1),
    }


# ----- Public -----

@bp.route("/")
def index():
    """Home page. Logged-in users are redirected to their dashboard."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)
    return render_template("index.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration. GET: show form. POST: validate, check duplicate email, hash password, save user, flash, redirect to login."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)
    form = RegistrationForm()
    form.role_id.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("That email is already registered.", "danger")
            return render_template("register.html", form=form)
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.lower().strip(),
            password_hash=generate_password_hash(form.password.data),
            role_id=form.role_id.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. You can log in now.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login. GET: show form. POST: validate, check user exists, verify password, login_user, flash, redirect to role dashboard."""
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Welcome back!", "success")
            return _redirect_by_role(user)
        flash("Invalid email or password.", "danger")
    return render_template("login.html", form=form)


@bp.route("/logout")
def logout():
    """Log out user, flash message, redirect to home."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@bp.route("/auth/register", methods=["GET", "POST"])
def auth_register():
    """Alias: /auth/register uses the same handler as /register."""
    return register()


@bp.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    """Alias: /auth/login uses the same handler as /login."""
    return login()


# ----- Dashboards (protected: login required + role check) -----

@bp.route("/student")
def student_redirect():
    """Redirect /student to dashboard."""
    return redirect(url_for("main.student_dashboard"))


@bp.route("/student/dashboard")
@login_required
@require_role("Student")
def student_dashboard():
    """Student dashboard with progress summary: stats, recent submissions, challenges."""
    submissions = Submission.query.filter_by(user_id=current_user.id).order_by(Submission.submitted_at.desc()).all()
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    progress = _student_progress_stats(current_user.id)
    return render_template("student_dashboard.html", submissions=submissions, challenges=challenges, progress=progress)


@bp.route("/student/progress")
@login_required
@require_role("Student")
def student_progress():
    """Student: progress by challenge – all challenges with submission status, score, feedback."""
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    my_submissions = {s.challenge_id: s for s in Submission.query.filter_by(user_id=current_user.id).order_by(Submission.submitted_at.desc())}
    challenge_rows = []
    for c in challenges:
        sub = my_submissions.get(c.id)
        challenge_rows.append({"challenge": c, "submission": sub})
    progress = _student_progress_stats(current_user.id)
    return render_template("student_progress.html", challenge_rows=challenge_rows, progress=progress)


@bp.route("/mentor")
@login_required
@require_role("Mentor")
def mentor_dashboard():
    """Mentor dashboard: only logged-in Mentors."""
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    return render_template("mentor_dashboard.html", challenges=challenges)


@bp.route("/admin")
@login_required
@require_role("Admin")
def admin_dashboard():
    """Admin dashboard: only logged-in Admins."""
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin_dashboard.html", challenges=challenges, users=users)


@bp.route("/admin/progress")
@login_required
@require_role("Admin")
def admin_progress():
    """Admin: overall student progress – all students with submission/completion stats."""
    student_role = Role.query.filter_by(name="Student").first()
    students = User.query.filter_by(role_id=student_role.id).order_by(User.full_name).all() if student_role else []
    student_stats = [(u, _student_progress_stats(u.id)) for u in students]
    return render_template("admin_progress.html", student_stats=student_stats)


@bp.route("/admin/progress/<int:user_id>")
@login_required
@require_role("Admin")
def admin_student_progress(user_id):
    """Admin: one student's progress detail – submissions, scores, completion."""
    user = User.query.get_or_404(user_id)
    if user.role.name != "Student":
        flash("Progress tracking is for students only.", "warning")
        return redirect(url_for("main.admin_progress"))
    submissions = Submission.query.filter_by(user_id=user.id).order_by(Submission.submitted_at.desc()).all()
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    my_submissions = {s.challenge_id: s for s in submissions}
    challenge_rows = [{"challenge": c, "submission": my_submissions.get(c.id)} for c in challenges]
    progress = _student_progress_stats(user.id)
    return render_template("admin_student_progress.html", student=user, submissions=submissions, challenge_rows=challenge_rows, progress=progress)


@bp.route("/mentor/progress")
@login_required
@require_role("Mentor")
def mentor_progress():
    """Mentor: read-only student progress overview."""
    student_role = Role.query.filter_by(name="Student").first()
    students = User.query.filter_by(role_id=student_role.id).order_by(User.full_name).all() if student_role else []
    student_stats = [(u, _student_progress_stats(u.id)) for u in students]
    return render_template("mentor_progress.html", student_stats=student_stats)


@bp.route("/mentor/progress/<int:user_id>")
@login_required
@require_role("Mentor")
def mentor_student_progress(user_id):
    """Mentor: read-only view of one student's progress."""
    user = User.query.get_or_404(user_id)
    if user.role.name != "Student":
        flash("Progress tracking is for students only.", "warning")
        return redirect(url_for("main.mentor_progress"))
    submissions = Submission.query.filter_by(user_id=user.id).order_by(Submission.submitted_at.desc()).all()
    progress = _student_progress_stats(user.id)
    return render_template("mentor_student_progress.html", student=user, submissions=submissions, progress=progress)


# ----- Challenges (public: students/mentors view) -----

@bp.route("/challenges")
def challenges_list():
    """List all challenges (read)."""
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    return render_template("challenges.html", challenges=challenges)


@bp.route("/challenges/<int:challenge_id>")
def challenge_detail(challenge_id):
    """Show one challenge (read)."""
    challenge = Challenge.query.get_or_404(challenge_id)
    return render_template("challenge_detail.html", challenge=challenge, admin=False)


# ----- Admin: Challenge CRUD -----

@bp.route("/admin/challenges")
@login_required
@require_role("Admin")
def admin_challenges_list():
    """Admin: view all challenges."""
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    return render_template("admin_challenges.html", challenges=challenges)


@bp.route("/admin/challenges/create", methods=["GET", "POST"])
@login_required
@require_role("Admin")
def create_challenge():
    """Admin: create challenge (GET form, POST create)."""
    form = ChallengeForm()
    if form.validate_on_submit():
        from datetime import datetime
        deadline = None
        if form.deadline.data:
            try:
                deadline = datetime.strptime(form.deadline.data.strip(), "%Y-%m-%d")
            except ValueError:
                pass
        challenge = Challenge(
            title=form.title.data.strip(),
            description=form.description.data,
            category=form.category.data.strip(),
            difficulty=form.difficulty.data,
            deadline=deadline,
            created_by=current_user.id,
        )
        db.session.add(challenge)
        db.session.commit()
        flash("Challenge created successfully.", "success")
        return redirect(url_for("main.admin_challenges_list"))
    return render_template("create_challenge.html", form=form)


@bp.route("/admin/challenges/<int:challenge_id>")
@login_required
@require_role("Admin")
def admin_challenge_detail(challenge_id):
    """Admin: view one challenge (read) with edit/delete actions."""
    challenge = Challenge.query.get_or_404(challenge_id)
    return render_template("challenge_detail.html", challenge=challenge, admin=True)


@bp.route("/admin/challenges/<int:challenge_id>/edit", methods=["GET", "POST"])
@login_required
@require_role("Admin")
def edit_challenge(challenge_id):
    """Admin: update challenge (GET form, POST update)."""
    challenge = Challenge.query.get_or_404(challenge_id)
    form = ChallengeForm()
    if form.validate_on_submit():
        from datetime import datetime
        challenge.title = form.title.data.strip()
        challenge.description = form.description.data
        challenge.category = form.category.data.strip()
        challenge.difficulty = form.difficulty.data
        deadline = None
        if form.deadline.data:
            try:
                deadline = datetime.strptime(form.deadline.data.strip(), "%Y-%m-%d")
            except ValueError:
                pass
        challenge.deadline = deadline
        db.session.commit()
        flash("Challenge updated successfully.", "success")
        return redirect(url_for("main.admin_challenges_list"))
    if request.method == "GET":
        form.title.data = challenge.title
        form.description.data = challenge.description
        form.category.data = challenge.category
        form.difficulty.data = challenge.difficulty
        form.deadline.data = challenge.deadline.strftime("%Y-%m-%d") if challenge.deadline else ""
    return render_template("edit_challenge.html", form=form, challenge=challenge)


@bp.route("/admin/challenges/<int:challenge_id>/delete", methods=["POST"])
@login_required
@require_role("Admin")
def delete_challenge(challenge_id):
    """Admin: delete challenge (POST only)."""
    challenge = Challenge.query.get_or_404(challenge_id)
    title = challenge.title
    Submission.query.filter_by(challenge_id=challenge.id).delete()
    for u in list(challenge.participants):
        challenge.participants.remove(u)
    db.session.delete(challenge)
    db.session.commit()
    flash(f"Challenge \"{title}\" has been deleted.", "success")
    return redirect(url_for("main.admin_challenges_list"))


@bp.route("/challenges/<int:challenge_id>/submit", methods=["GET", "POST"])
@login_required
@require_role("Student")
def submit_challenge(challenge_id):
    """Submit a challenge (Student only). GET: form. POST: save submission, redirect to my submissions."""
    challenge = Challenge.query.get_or_404(challenge_id)
    form = SubmissionForm()
    if form.validate_on_submit():
        submission = Submission(
            user_id=current_user.id,
            challenge_id=challenge.id,
            text_answer=form.text_answer.data.strip(),
            file_name=form.file_name.data.strip() or None,
            status="Pending",
        )
        db.session.add(submission)
        if challenge not in current_user.participated_challenges:
            current_user.participated_challenges.append(challenge)
        db.session.commit()
        flash("Submission received. Good luck!", "success")
        return redirect(url_for("main.my_submissions"))
    return render_template("submit_challenge.html", form=form, challenge=challenge)


# ----- Student: My Submissions -----

@bp.route("/my-submissions")
@login_required
@require_role("Student")
def my_submissions():
    """Student: list own submissions only."""
    submissions = Submission.query.filter_by(user_id=current_user.id).order_by(Submission.submitted_at.desc()).all()
    return render_template("my_submissions.html", submissions=submissions)


@bp.route("/my-submissions/<int:submission_id>")
@login_required
@require_role("Student")
def my_submission_detail(submission_id):
    """Student: view own submission detail. 404 if not owner."""
    submission = Submission.query.get_or_404(submission_id)
    if submission.user_id != current_user.id:
        flash("You can only view your own submissions.", "danger")
        return redirect(url_for("main.my_submissions"))
    return render_template("submission_detail.html", submission=submission, admin_view=False)


# ----- Admin: Submissions and review -----

@bp.route("/admin/submissions")
@login_required
@require_role("Admin")
def admin_submissions_list():
    """Admin: list all submissions."""
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).all()
    return render_template("admin_submissions.html", submissions=submissions)


@bp.route("/admin/submissions/<int:submission_id>")
@login_required
@require_role("Admin")
def admin_submission_detail(submission_id):
    """Admin: view one submission."""
    submission = Submission.query.get_or_404(submission_id)
    return render_template("submission_detail.html", submission=submission, admin_view=True)


@bp.route("/admin/submissions/<int:submission_id>/review", methods=["GET", "POST"])
@login_required
@require_role("Admin")
def review_submission(submission_id):
    """Admin: review submission. GET: form. POST: update score, status, feedback; set reviewed_at."""
    from datetime import datetime
    submission = Submission.query.get_or_404(submission_id)
    form = ReviewSubmissionForm()
    if form.validate_on_submit():
        submission.score = form.score.data
        submission.status = form.status.data
        submission.feedback = form.feedback.data.strip() or None
        submission.reviewed_at = datetime.utcnow()
        db.session.commit()
        flash("Review saved successfully.", "success")
        return redirect(url_for("main.admin_submissions_list"))
    if request.method == "GET":
        form.score.data = submission.score
        form.status.data = submission.status or "Pending"
        form.feedback.data = submission.feedback or ""
    return render_template("review_submission.html", form=form, submission=submission)


# ----- Mentor: view submissions (optional) -----

@bp.route("/mentor/submissions")
@login_required
@require_role("Mentor")
def mentor_submissions_list():
    """Mentor: view all submissions (read-only)."""
    submissions = Submission.query.order_by(Submission.submitted_at.desc()).all()
    return render_template("mentor_submissions.html", submissions=submissions)
