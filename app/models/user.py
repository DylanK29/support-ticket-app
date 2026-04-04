#User model with Flask-Login integration.

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from app import db


class Role:
    #User role constants.
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    
    ALL_ROLES = [USER, MODERATOR, ADMIN]


class User(UserMixin, db.Model):
    #User account model.
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default=Role.USER, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    #Relationships
    created_tickets = db.relationship(
        'Ticket',
        foreign_keys='Ticket.creator_id',
        backref='creator',
        lazy='dynamic'
    )
    assigned_tickets = db.relationship(
        'Ticket',
        foreign_keys='Ticket.assignee_id',
        backref='assignee',
        lazy='dynamic'
    )
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    history_entries = db.relationship('TicketHistory', backref='user', lazy='dynamic')

    def set_password(self, password):
        #Hash and the set user's password.
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        #Verify the user's password.
        return check_password_hash(self.password_hash, password)
    
    #Role helper methods
    def has_admin_role(self):
        #Check if user is an admin.
        return self.role == Role.ADMIN
    
    def is_moderator(self):
        #Check if user is a moderator or higher.
        return self.role in [Role.MODERATOR, Role.ADMIN]
    
    def has_role(self, role):
        #Check if user has a specific role.
        return self.role == role
    
    def set_role(self, role):
        #Set user role with validation.
        if role not in Role.ALL_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {Role.ALL_ROLES}")
        self.role = role
    
    def make_admin(self):
        #Promote user to admin
        self.is_admin = True
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'