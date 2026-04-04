#AI helper functions for ticket analysis

import os
from openai import OpenAI

def get_ai_suggestions(title, description):
    #Get AI-suggested category and priority for a ticket
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""Analyze this support ticket and suggest a category and priority.

            Title: {title}
            Description: {description}

            Categories (choose one):
            - bug (software errors, crashes, things not working)
            - user_support (help requests, how-to questions)
            - data_issue (incorrect data, missing data, data problems)
            - feature_request (new feature ideas, enhancements)
            - access_permissions (login issues, permission problems, access requests)
            - other (anything else)

            Priorities (choose one):
            - low (minor issues, no urgency)
            - medium (normal priority)
            - high (important, affecting work)
            - urgent (critical, needs immediate attention)

            Respond in exactly this format:
            CATEGORY: [category]
            PRIORITY: [priority]
            REASON: [one sentence explanation]"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        
        #Parse response
        lines = result.split('\n')
        category = None
        priority = None
        reason = None
        
        for line in lines:
            if line.startswith('CATEGORY:'):
                category = line.replace('CATEGORY:', '').strip().lower()
            elif line.startswith('PRIORITY:'):
                priority = line.replace('PRIORITY:', '').strip().lower()
            elif line.startswith('REASON:'):
                reason = line.replace('REASON:', '').strip()
        
        return {
            'category': category,
            'priority': priority,
            'reason': reason
        }
    
    except Exception as e:
        print(f"AI suggestion error: {e}")
        return None

def generate_ticket_summary(title, description, comments):
    #Generate a summary of the ticket
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        comments_text = ""
        if comments:
            comments_text = "\n\nComments:\n" + "\n".join([f"- {c}" for c in comments])
        
        prompt = f"""Summarize this support ticket in 2-3 sentences:

            Title: {title}
            Description: {description}{comments_text}

            Provide a concise summary that captures the main issue and current status."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"AI summary error: {e}")
        return None
    
def suggest_response(title, description, category, status):
    #Suggest a response for the ticket
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = f"""You are a helpful IT support agent. Suggest a professional response for this ticket:

            Title: {title}
            Description: {description}
            Category: {category}
            Status: {status}

            Write a helpful, professional response (2-3 sentences) that:
            1. Acknowledges the issue
            2. Provides next steps or asks for more information
            3. Is friendly and professional"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"AI response error: {e}")
        return None