#Flask Application Entry Point


import os
from app import create_app, db
from app.models import User, Ticket, Comment, TicketHistory

# Create app instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    #Add objects to flask shell context for easy debugging.
    return {
        'db': db,
        'User': User,
        'Ticket': Ticket,
        'Comment': Comment,
        'TicketHistory': TicketHistory
    }


if __name__ == '__main__':
    app.run(debug=True)