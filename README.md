# INTERNAL SUPPORT TICKET TRACKER

A full-stack web application for logging, managing, and resolving internal support tickets for the Innovation team.

## LIVE DEMO

https://support-ticket-app-ftx6.onrender.com

## Features

### Core Features
- User registration and authentication
- Create support tickets with title, description, priority, and category
- Assign tickets to team members
- View all tickets in a dashboard
- Filter tickets by status
- Search tickets by title or description
- View detailed ticket information
- Update ticket status and assignee
- Add comments and notes to tickets
- Track ticket history and status changes

### Bonus Features
- **Dashboard Metrics** - Visual cards showing ticket counts by status
- **Loading States** - Visual feedback when submitting forms
- **Empty States** - Helpful messages when no data exists
- **Keyboard Shortcuts** - Press 'c' to create ticket, 'd' for dashboard
- **Role-Based Access** - Admin panel for user management
- **AI Categorization** - Auto-suggest category and priority using AI
- **AI Ticket Summary** - Generate concise summaries of tickets
- **AI Suggested Responses** - Help agents write replies
- **Email Simulation** - Notification log showing sent emails

## Technology Stack

| Layer | Technology |
|----------------|----------------|
| Backend | Python, Flask |
| Database | PostgreSQL (production), SQLite (development) |
| ORM | SQLAlchemy |
| Authentication | Flask-Login |
| Frontend | HTML, Jinja2, Bootstrap 5 |
| AI | OpenAI GPT-3.5 |
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
- OpenAI API key (for AI features)

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
    OPENAI_API_KEY=your-openai-api-key
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
| OPENAI_API_KEY | For accessing AI features |

## Keyboard Shortcuts
| Key | Action |
|---------------|---------------|
| c | Create New Ticket |
| d | Go to Dashboard |