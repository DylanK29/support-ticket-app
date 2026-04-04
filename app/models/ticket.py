#Ticket model with priority, category, and status enums.

from enum import Enum
from datetime import datetime, timezone
from app import db


class Priority(str, Enum):
    #Ticket priority levels.
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'
    
    def __str__(self):
        return self.value
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.name.title()) for choice in cls]


class Category(str, Enum):
    #Ticket categories.
    BUG = 'bug'
    USER_SUPPORT = 'user_support'
    DATA_ISSUE = 'data_issue'
    FEATURE_REQUEST = 'feature_request'
    ACCESS_PERMISSIONS = 'access_permissions'
    OTHER = 'other'
    
    def __str__(self):
        return self.value
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.name.replace('_', ' ').title()) for choice in cls]


class Status(str, Enum):
    #Ticket status options.
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    WAITING_ON_USER = 'waiting_on_user'
    BLOCKED = 'blocked'
    RESOLVED = 'resolved'
    CLOSED = 'closed'
    
    def __str__(self):
        return self.value
    
    @classmethod
    def choices(cls):
        return [(choice.value, choice.name.replace('_', ' ').title()) for choice in cls]
    
    @classmethod
    def open_statuses(cls):
        #Return statuses considered 'open'.
        return [cls.NEW, cls.IN_PROGRESS, cls.WAITING_ON_USER]
    
    @classmethod
    def closed_statuses(cls):
        #Return statuses considered 'closed'.
        return [cls.RESOLVED, cls.CLOSED, cls.BLOCKED]


class Ticket(db.Model):
    #Support ticket model.
    
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Enum(Priority), default=Priority.MEDIUM, nullable=False)
    category = db.Column(db.Enum(Category), default=Category.OTHER, nullable=False)
    status = db.Column(db.Enum(Status), default=Status.NEW, nullable=False, index=True)
    
    #Foreign keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    #Timestamps
    created_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    #Relationships
    comments = db.relationship(
        'Comment',
        backref='ticket',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='Comment.created_date.desc()'
    )
    history = db.relationship(
        'TicketHistory',
        backref='ticket',
        lazy='dynamic',
        cascade='all, delete-orphan',
        order_by='TicketHistory.changed_date.desc()'
    )
    
    #Helper methods
    def is_open(self):
        #Check if ticket is in an open state.
        return self.status in Status.open_statuses()
    
    def is_closed(self):
        #Check if ticket is in a closed state.
        return self.status in Status.closed_statuses()
    
    def is_assigned(self):
        #Check if ticket has an assignee.
        return self.assignee_id is not None
    
    def can_edit(self, user):
        #Check if user can edit this ticket.
        return (
            user.is_admin() or
            user.id == self.creator_id or
            user.id == self.assignee_id
        )
    
    def update_status(self, new_status, user):
        #Update ticket status and create history entry.
        if self.status == new_status:
            return None
        
        from app.models.ticket_history import TicketHistory
        
        history_entry = TicketHistory(
            ticket_id=self.id,
            user_id=user.id,
            old_status=self.status,
            new_status=new_status
        )
        
        self.status = new_status
        db.session.add(history_entry)
        
        return history_entry
    
    def assign_to(self, user, assigned_by=None):
        #Assign ticket to a user.
        self.assignee_id = user.id if user else None
        
        #Optionally update status when assigned
        if user and self.status == Status.NEW:
            if assigned_by:
                self.update_status(Status.IN_PROGRESS, assigned_by)
            else:
                self.status = Status.IN_PROGRESS
    
    def add_comment(self, content, user):
        #Add a comment to the ticket.
        from app.models.comment import Comment
        
        comment = Comment(
            content=content,
            ticket_id=self.id,
            user_id=user.id
        )
        db.session.add(comment)
        return comment
    

    @property
    def comment_count(self):
        #Return the number of comments.
        return self.comments.count()
    
    @classmethod
    def get_open_tickets(cls):
        #Get all open tickets.
        return cls.query.filter(cls.status.in_(Status.open_statuses()))
    
    @classmethod
    def get_by_status(cls, status):
        #Get tickets by status.
        return cls.query.filter_by(status=status)
    
    @classmethod
    def get_by_assignee(cls, user_id):
        #Get tickets assigned to a user.
        return cls.query.filter_by(assignee_id=user_id)
    
    @classmethod
    def get_by_creator(cls, user_id):
        #Get tickets created by a user.
        return cls.query.filter_by(creator_id=user_id)
    
    def to_dict(self):
        #Convert ticket to dictionary.
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'category': self.category.value,
            'status': self.status.value,
            'creator_id': self.creator_id,
            'creator_name': self.creator.name if self.creator else None,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee.name if self.assignee else None,
            'created_date': self.created_date.isoformat(),
            'updated_date': self.updated_date.isoformat() if self.updated_date else None,
            'comment_count': self.comment_count
        }
    
    def __repr__(self):
        return f'<Ticket {self.id}: {self.title[:30]}>'