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