# INTERNAL SUPPORT TICKET TRACKER

A full-stack web application for logging, managing, and resolving internal support tickets for the Innovation team.

## LIVE DEMO

https://support-ticket-app-ftx6.onrender.com

## Features

- User registration and authentication
- Create support tickets with title, description, priority, category, and assignee
- Dashboard to view all tickets
- Filter tickets by status
- Freeform search bar to search tickets by title or description
- View ticket details
- Select tickets to update status and assignee, add comments, and track status changes
- Simulated email notification system
- Admin access to tickets and emails
- AI generated label suggestions, ticket summaries, and suggested replies
- Attachment support

## Technology Stack

| Layer | Technology |
|----------------|----------------|
| Backend | Python, Flask |
| Database | PostgreSQL (production), SQLite (development) |
| ORM | SQLAlchemy |
| Authentication | Flask-Login |
| Frontend | HTML, Jinja2, Bootstrap 5 |
| Deployment | Render.com |


## Ticket Statuses

- New
- In Progress
- Waiting on User
- Blocked
- Resolved
- Closed

## Categories

- Bug
- User Support
- Data Issue
- Feature Request
- Access / Permissions
- Other

## Local Development Setup

### Prerequisites

- Python 3.11
- Anaconda
- Git

### Installation

1. Clone the repository
```bash
   git clone https://github.com/DylanK29/support-ticket-app.git
   cd ticket-tracker
```
2. Create and activate virtual environments
```bash
    conda create -n ticket-app python=3.11
    conda activate ticket-app
```
3. Install Dependencies
```bash
    pip install -r requirements.txt
```
4. Create .env file in project root:
```bash   
    SECRET_KEY=your-secret-key
    FLASK_ENV=development
```    
5. Run the application
```bash    
    python run.py
```    
6. Open http://127.0.0.1:5000/ in your browser

## Project Structure
```bash
support-ticket-app/
├── app/
│   ├── __init__.py             #App factory
│   ├── ai_helper.py            #AI generation functions
│   ├── email_helper.py         #Email simulation functions
│   ├── routes.py               #Route handlers
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             #User model
│   │   ├── ticket.py           #Ticket model with enums
│   │   ├── comment.py          #Comment model
│   │   └── ticket_history.py   #History tracking model
│   └── templates/
│       ├── admin.html           
│       ├── base.html           #Base template with navbar
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html      #Ticket list with filters
│       ├── email_log.html           
│       ├── create_ticket.html
│       └── ticket_detail.html
├── config.py                   #Configuration classes
├── run.py                      #Application entry point
├── requirements.txt            #Python dependencies
├── Procfile                    #Deployment config
└── README.md
```
## Architecture

This app follows a Model-View-Controller pattern:
- Models: SQLAlchemy models define database structure (User, Ticket, Comment, Ticket_History).
- Visuals: Jinja2 templates render HTML pages with Bootstrap 5 styling.
- Controllers: Flask routes handle HTTP requests and business logic.

## Environment Variables

| Variable | Description |
|---------------|---------------|
| SECRET_KEY | Flask secret key for sessions |
| DATABASE_URL | PostgreSQL connection string (for production) |
| FLASK_ENV | For development or production |
| OPENAI_API_KEY | For accessing Open AI LLM |