#Application Routes

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Ticket, Comment, TicketHistory
from app.models.ticket import Priority, Category, Status

main = Blueprint('main', __name__)

@main.route('/')
def home():
    #Redirect home to login or dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    #User registration
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        #Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        #Create new user
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    #User login
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    #User logout
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    #Main dashboard showing all tickets
    status_filter = request.args.get('status')
    search_query = request.args.get('search')
    
    #Calculate metrics
    total_tickets = Ticket.query.count()
    new_tickets = Ticket.query.filter_by(status=Status.NEW).count()
    in_progress_tickets = Ticket.query.filter_by(status=Status.IN_PROGRESS).count()
    resolved_tickets = Ticket.query.filter_by(status=Status.RESOLVED).count()
    
    #Start with all tickets
    query = Ticket.query
    
    #Apply status filter
    if status_filter and status_filter != 'all':
        try:
            status_enum = Status(status_filter)
            query = query.filter_by(status=status_enum)
        except ValueError:
            pass
    
    #Apply search filter
    if search_query:
        search_term = f'%{search_query}%'
        query = query.filter(
            db.or_(
                Ticket.title.ilike(search_term),
                Ticket.description.ilike(search_term)
            )
        )
    
    tickets = query.order_by(Ticket.created_date.desc()).all()
    users = User.query.all()
    
    return render_template(
        'dashboard.html',
        tickets=tickets,
        users=users,
        current_status=status_filter,
        search_query=search_query,
        total_tickets=total_tickets,
        new_tickets=new_tickets,
        in_progress_tickets=in_progress_tickets,
        resolved_tickets=resolved_tickets
    )

@main.route('/tickets/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    #Create a new ticket
    users = User.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority_value = request.form.get('priority')
        category_value = request.form.get('category')
        assignee_id = request.form.get('assignee_id')
        
        #Convert to enums
        priority = Priority(priority_value)
        category = Category(category_value)
        
        #Handle empty assignee
        if assignee_id == '':
            assignee_id = None
        
        ticket = Ticket(
            title=title,
            description=description,
            priority=priority,
            category=category,
            status='new',
            creator_id=current_user.id,
            assignee_id=assignee_id
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        flash('Ticket created successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('create_ticket.html', users=users)

@main.route('/tickets/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    #View ticket details
    ticket = Ticket.query.get_or_404(ticket_id)
    comments = Comment.query.filter_by(ticket_id=ticket_id).order_by(Comment.created_date.asc()).all()
    history = TicketHistory.query.filter_by(ticket_id=ticket_id).order_by(TicketHistory.changed_date.desc()).all()
    users = User.query.all()
    
    return render_template('ticket_detail.html', ticket=ticket, comments=comments, history=history, users=users)

@main.route('/tickets/<int:ticket_id>/update', methods=['POST'])
@login_required
def update_ticket(ticket_id):
    #Update ticket status and assignee
    ticket = Ticket.query.get_or_404(ticket_id)
    
    new_status_value = request.form.get('status')
    new_assignee_id = request.form.get('assignee_id')
    
    #Convert status to enum
    new_status = Status(new_status_value)
    
    #Handle empty assignee
    if new_assignee_id == '':
        new_assignee_id = None
    else:
        new_assignee_id = int(new_assignee_id)
    
    #Record status change in history
    if ticket.status != new_status:
        history = TicketHistory(
            ticket_id=ticket_id,
            user_id=current_user.id,
            old_status=ticket.status,
            new_status=new_status
        )
        db.session.add(history)
        ticket.status = new_status
    
    #Update assignee (no history tracking for assignee)
    ticket.assignee_id = new_assignee_id
    
    db.session.commit()
    flash('Ticket updated successfully!', 'success')
    return redirect(url_for('main.ticket_detail', ticket_id=ticket_id))

@main.route('/tickets/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    #Add comment to ticket
    ticket = Ticket.query.get_or_404(ticket_id)
    content = request.form.get('content')
    
    comment = Comment(
        content=content,
        ticket_id=ticket_id,
        user_id=current_user.id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added!', 'success')
    return redirect(url_for('main.ticket_detail', ticket_id=ticket_id))