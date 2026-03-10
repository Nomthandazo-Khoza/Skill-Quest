"""
SkillQuest - Database models.
Demonstrates: model creation, table creation, One-to-Many and Many-to-Many relationships.
"""
from datetime import datetime
from flask_login import UserMixin
from app import db


# ----- Association table for Many-to-Many: Students <-> Challenges -----
# Students can participate in many Challenges; Challenges can involve many Students.
challenge_participants = db.Table(
    "challenge_participants",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("challenge_id", db.Integer, db.ForeignKey("challenge.id"), primary_key=True),
)


class Role(db.Model):
    """Role model: Student, Mentor, Admin. One-to-Many with User."""
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship("User", backref="role", lazy="dynamic")


class User(UserMixin, db.Model):
    """User model. Many users belong to one Role. One user has many Submissions and many Challenges (created)."""
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship("Submission", backref="user", lazy="dynamic", foreign_keys="Submission.user_id")
    challenges_created = db.relationship("Challenge", backref="creator", lazy="dynamic", foreign_keys="Challenge.created_by")
    # Many-to-Many: this user (student) participates in many challenges
    participated_challenges = db.relationship(
        "Challenge",
        secondary=challenge_participants,
        backref=db.backref("participants", lazy="dynamic"),
        lazy="dynamic",
    )


class Challenge(db.Model):
    """Challenge model. One creator (User). Many Submissions. Many participants (Users) via association table."""
    __tablename__ = "challenge"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # e.g. Easy, Medium, Hard
    deadline = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship("Submission", backref="challenge", lazy="dynamic")


class Submission(db.Model):
    """Submission model. One User, one Challenge. One-to-Many: User->Submissions, Challenge->Submissions."""
    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenge.id"), nullable=False)
    text_answer = db.Column(db.Text, nullable=True)
    file_name = db.Column(db.String(255), nullable=True)
    score = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), default="Pending")  # Pending, Reviewed, Late, Rejected
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
