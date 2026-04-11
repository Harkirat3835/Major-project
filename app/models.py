from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """User model for authentication with enhanced security"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    failed_logins = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    refresh_token_hash = db.Column(db.String(256), nullable=True)
    email_verification_token = db.Column(db.String(64), nullable=True)
    password_reset_token = db.Column(db.String(64), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    feedback = db.relationship('Feedback', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.password_reset_token = None
        self.password_reset_expires = None

    def check_password(self, password):
        """Check password with lockout logic"""
        if self.is_locked():
            return False
        return check_password_hash(self.password_hash, password)

    def increment_failed_login(self):
        """Increment failed login count and check for lockout"""
        self.failed_logins += 1
        if self.failed_logins >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)
        self.updated_at = datetime.utcnow()

    def reset_failed_logins(self):
        """Reset failed login count"""
        self.failed_logins = 0
        self.locked_until = None
        self.updated_at = datetime.utcnow()

    def is_locked(self):
        """Check if account is locked"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def set_refresh_token(self, refresh_token):
        """Securely store refresh token hash"""
        import hashlib
        self.refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    def verify_refresh_token(self, refresh_token):
        """Verify refresh token"""
        import hashlib
        return self.refresh_token_hash == hashlib.sha256(refresh_token.encode()).hexdigest()

    def generate_verification_token(self):
        """Generate secure email verification token"""
        import secrets
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        self.updated_at = datetime.utcnow()
        return token

    def generate_reset_token(self):
        """Generate secure password reset token"""
        import secrets
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        from datetime import timedelta
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        self.updated_at = datetime.utcnow()
        return token

    def clear_reset_token(self):
        """Clear password reset token"""
        self.password_reset_token = None
        self.password_reset_expires = None

    def is_reset_token_valid(self, token):
        """Validate password reset token"""
        return (self.password_reset_token == token and 
                self.password_reset_expires and 
                self.password_reset_expires > datetime.utcnow())

    def to_dict(self, include_sensitive=False):
        base_dict = {
            'id': self.id,
            'name': self.username.replace('_', ' ').title(),
            'username': self.username,
            'email': self.email,
            'email_verified': self.email_verified,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_sensitive:
            base_dict['locked_until'] = self.locked_until.isoformat() if self.locked_until else None
        return base_dict

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
