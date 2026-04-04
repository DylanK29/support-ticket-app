#Email Simulation

import os
from datetime import datetime, timezone

#Store sent emails in memory
sent_emails = []

def send_notification(to_email, to_name, subject, message):
    #Simulate sending an email notification
    
    email_record = {
        'to': to_email,
        'to_name': to_name,
        'subject': subject,
        'message': message,
        'sent_at': datetime.now(timezone.utc),
        'status': 'sent'
    }
    
    sent_emails.append(email_record)

    print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")
    
    return True

def send_ticket_assigned_notification(ticket, assignee, assigned_by):
    #Send notification when ticket is assigned
    
    subject = f"Ticket Assigned: {ticket.title}"
    message = f"""Hello {assignee.name},

        You have been assigned a new ticket:

        Title: {ticket.title}
        Priority: {ticket.priority.value}
        Category: {ticket.category.value}

        Description:
        {ticket.description}

        Assigned by: {assigned_by.name}

        Please review and update the ticket status accordingly.

        Best regards,
        Support Ticket Tracker System"""
    
    return send_notification(assignee.email, assignee.name, subject, message)

def send_ticket_status_notification(ticket, changed_by):
    #Send notification when ticket status changes
    
    if not ticket.creator:
        return False
    
    subject = f"Ticket Updated: {ticket.title}"
    message = f"""Hello {ticket.creator.name},

        Your ticket has been updated:

        Title: {ticket.title}
        New Status: {ticket.status.value}

        Updated by: {changed_by.name}

        Best regards,
        Support Ticket Tracker System"""
    
    return send_notification(ticket.creator.email, ticket.creator.name, subject, message)

def get_sent_emails():
    #Get all sent emails
    return sorted(sent_emails, key=lambda x: x['sent_at'], reverse=True)