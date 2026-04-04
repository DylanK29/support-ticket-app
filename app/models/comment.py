#Comment model for ticket discussions.
from datetime import datetime, timezone
from app import db


class Comment(db.Model):
    #Comment on a ticket.
    
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
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

    #Relationships
    user = db.relationship('User', backref='user_comments')
    
    #Timestamps
    created_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    edited_date = db.Column(db.DateTime, nullable=True)
    is_edited = db.Column(db.Boolean, default=False)
    
    def edit(self, new_content):
        #Edit the comment content.
        self.content = new_content
        self.edited_date = datetime.now(timezone.utc)
        self.is_edited = True
    
    def can_edit(self, user):
        #Check if user can edit this comment.
        return user.id == self.user_id or user.is_admin
    
    def can_delete(self, user):
        #Check if user can delete this comment.
        return user.id == self.user_id or user.is_admin
    
    def to_dict(self):
        #Convert comment to dictionary.
        return {
            'id': self.id,
            'content': self.content,
            'ticket_id': self.ticket_id,
            'user_id': self.user_id,
            'author_name': self.author.name if self.author else None,
            'created_date': self.created_date.isoformat(),
            'edited_date': self.edited_date.isoformat() if self.edited_date else None,
            'is_edited': self.is_edited
        }
    
    def __repr__(self):
        return f'<Comment {self.id} on Ticket {self.ticket_id}>'