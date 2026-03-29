from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'is_admin': self.is_admin
        }

class Analysis(db.Model):
    """Analysis history model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    text_hash = db.Column(db.String(64), nullable=False)  # For duplicate detection
    text_length = db.Column(db.Integer, nullable=False)
    prediction = db.Column(db.String(10), nullable=False)  # 'Real' or 'Fake'
    confidence = db.Column(db.Float, nullable=True)
    reasons = db.Column(db.Text, nullable=True)  # JSON string of reasons
    processing_time = db.Column(db.Float, nullable=False)  # in milliseconds
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'text_length': self.text_length,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'reasons': self.reasons,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat()
        }

class Feedback(db.Model):
    """User feedback on predictions"""
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_correct = db.Column(db.Boolean, nullable=False)  # User agrees/disagrees
    user_correction = db.Column(db.String(10), nullable=True)  # User's correction
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    analysis = db.relationship('Analysis', backref='feedback')

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'user_id': self.user_id,
            'is_correct': self.is_correct,
            'user_correction': self.user_correction,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }