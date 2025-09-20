# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    _tablename_ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('student', 'alumni', 'mentor'), nullable=False)
    skills = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationships
    opportunities = db.relationship("Opportunity", backref="poster", lazy=True)
    applications = db.relationship("Application", backref="applicant", lazy=True)
    mentorship_as_mentor = db.relationship("MentorshipSession", foreign_keys="[MentorshipSession.mentor_id]", backref="mentor", lazy=True)
    mentorship_as_mentee = db.relationship("MentorshipSession", foreign_keys="[MentorshipSession.mentee_id]", backref="mentee", lazy=True)
    stories = db.relationship("Story", backref="author", lazy=True)


class Opportunity(db.Model):
    _tablename_ = 'opportunities'
    opp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    type = db.Column(db.Enum('job', 'internship', 'scholarship', 'mentorship'), nullable=False)
    description = db.Column(db.Text)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    posted_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    applications = db.relationship("Application", backref="opportunity", lazy=True)


class Application(db.Model):
    _tablename_ = 'applications'
    app_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    opp_id = db.Column(db.Integer, db.ForeignKey('opportunities.opp_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    status = db.Column(db.Enum('applied', 'reviewed', 'selected', 'rejected'), default='applied')
    applied_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())


class MentorshipSession(db.Model):
    _tablename_ = 'mentorship_sessions'
    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    mentee_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    topic = db.Column(db.String(150))
    scheduled_at = db.Column(db.DateTime)


class Story(db.Model):
    _tablename_ = 'stories'
    story_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    posted_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
