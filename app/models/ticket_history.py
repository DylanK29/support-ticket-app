#Ticket history model for tracking status changes.

from datetime import datetime, timezone
from app import db
from app.models.ticket import Status


class TicketHistory(db.Model):
    #History entry for ticket status changes.
    
    __tablename__ = 'ticket_history'
    
    id = db.Column(db.Integer, primary_key=True)
    
    #Foreign keys
    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey('tickets.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )

    #Status change
    old_status = db.Column(db.Enum(Status), nullable=False)
    new_status = db.Column(db.Enum(Status), nullable=False)
    
    #Timestamp
    changed_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    #Optional note
    note = db.Column(db.String(500), nullable=True)
    
    @property
    def status_changed_to_closed(self):
        #Check if this change closed the ticket.
        return (
            self.old_status in Status.open_statuses() and
            self.new_status in Status.closed_statuses()
        )
    
    @property
    def status_changed_to_open(self):
        #Check if this change reopened the ticket.
        return (
            self.old_status in Status.closed_statuses() and
            self.new_status in Status.open_statuses()
        )
    
    @classmethod
    def get_ticket_history(cls, ticket_id):
        #Get all history entries for a ticket.
        return cls.query.filter_by(ticket_id=ticket_id)\
            .order_by(cls.changed_date.desc()).all()
    
    @classmethod
    def get_user_activity(cls, user_id, limit=50):
        #Get recent activity by a user.
        return cls.query.filter_by(user_id=user_id)\
            .order_by(cls.changed_date.desc())\
            .limit(limit).all()
    
    def to_dict(self):
        #Convert history entry to dictionary.
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'old_status': self.old_status.value,
            'new_status': self.new_status.value,
            'changed_date': self.changed_date.isoformat(),
            'note': self.note
        }
    
    def __repr__(self):
        return f'<TicketHistory {self.id}: {self.old_status} -> {self.new_status}>'