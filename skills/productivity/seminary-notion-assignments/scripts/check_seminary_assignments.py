#!/usr/bin/env python3
"""
Check for seminary writing assignments in Notion databases.

This script searches for databases related to assignments/papers/essays/exegesis,
checks them for due dates and status, and reports on upcoming work.

Designed to work with the notion skill in Hermes.
"""

import os
import json
import requests
from datetime import datetime, timedelta
import subprocess
import sys

def get_notion_token():
    """Extract NOTION_TOKEN from ~/.mcp_servers.json"""
    try:
        result = subprocess.run([
            'jq', '-r', '.mcpServers.notion.env.NOTION_TOKEN', 
            '/home/deeone/.mcp_servers.json'
        ], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting token: {e}", file=sys.stderr)
        return None

def search_databases(query, headers):
    """Search for databases matching query"""
    try:
        response = requests.post(
            'https://api.notion.com/v1/search',
            headers=headers,
            json={'query': query, 'filter': {'property': 'object', 'value': 'database'}},
            timeout=10
        )
        if response.status_code ==  .response.json().get('results', []):
        else:
            print(f"Error searching for '{query}': {response.status_code}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Exception searching for '{query}': {e}", file=sys.stderr)
        return []

def get_database_properties(db_id, headers):
    """Get properties of a database"""
    try:
        response = requests.get(
            f'https://api.notion.com/v1/databases/{db_id}',
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('properties', {})
        else:
            print(f"Error getting properties for {db_id}: {response.status_code}", file=sys.stderr)
            return {}
    except Exception as e:
        print(f"Exception getting properties for {db_id}: {e}", file=sys.stderr)
        return {}

def query_database(db_id, headers):
    """Query a database for all entries"""
    try:
        response = requests.post(
            f'https://api.notion.com/v1/databases/{db_id}/query',
            headers=headers,
            json={},
            timeout=10
        )
        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            print(f"Error querying database {db_id}: {response.status_code}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Exception querying database {db_id}: {e}", file=sys.stderr)
        return []

def extract_property_value(prop):
    """Extract value from a Notion property"""
    if not prop:
        return None
        
    prop_type = prop.get('type')
    if prop_type == 'title':
        title_array = prop.get('title', [])
        if title_array:
            return title_array[0].get('plain_text', '')
    elif prop_type == 'rich_text':
        text_array = prop.get('rich_text', [])
        if text_array:
            return text_array[0].get('plain_text', '')
    elif prop_type == 'date':
        date_obj = prop.get('date')
        if date_obj:
            return date_obj.get('start')  # Return ISO date string
    elif prop_type == 'select':
        select_obj = prop.get('select')
        if select_obj:
            return select_obj.get('name')
    elif prop_type == 'checkbox':
        return prop.get('checkbox', False)
    elif prop_type == 'url':
        return prop.get('url')
    elif prop_type == 'email':
        return prop.get('email')
    elif prop_type == 'phone_number':
        return prop.get('phone_number')
    elif prop_type == 'number':
        return prop.get('number')
    return None

def main():
    NOTION_TOKEN = get_notion_token()
    if not NOTION_TOKEN:
        print("Error: Could not retrieve NOTION_TOKEN", file=sys.stderr)
        sys.exit(1)

    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }

    search_terms = ['assignment', 'paper', 'essay', 'exegesis']
    database_ids = set()
    
    # Search for databases
    for term in search_terms:
        results = search_databases(term, headers)
        for db in results:
            if db.get('object') == 'database':
                database_ids.add(db['id'])
    
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    active_assignments = []
    upcoming_deadlines = []
    
    # Process each database
    for db_id in database_ids:
        properties = get_database_properties(db_id, headers)
        if not properties:
            continue
            
        # Find relevant properties
        name_prop = None
        due_date_prop = None
        status_prop = None
        
        for prop_name, prop_details in properties.items():
            prop_type = prop_details.get('type')
            if prop_type == 'title' and name_prop is None:
                name_prop = prop_name
            elif prop_type == 'date' and due_date_prop is None:
                due_date_prop = prop_name
            elif prop_type in ['select', 'status', 'checkbox'] and status_prop is None:
                status_prop = prop_name
        
        if not name_prop:
            continue
            
        # Query the database
        results = query_database(db_id, headers)
        for page in results:
            props = page.get('properties', {})
            
            # Extract name
            name_prop_val = props.get(name_prop, {})
            name = extract_property_value(name_prop_val) or "Untitled"
            
            # Extract due date
            due_date = None
            if due_date_prop:
                due_date_prop_val = props.get(due_date_prop, {})
                date_str = extract_property_value(due_date_prop_val)
                if date_str:
                    try:
                        due_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                    except:
                        pass
            
            # Extract status
            status = "Unknown"
            if status_prop:
                status_prop_val = props.get(status_prop, {})
                status_val = extract_property_value(status_prop_val)
                if status_val is not None:
                    status = str(status_val)
            
            # Only process if we have a due date
            if due_date:
                # Check if active (not done/completed and due today or in future)
                is_done = False
                if status.lower() in ['done', 'completed', 'finished']:
                    is_done = True
                elif status_prop and props.get(status_prop, {}).get('type') == 'checkbox':
                    checkbox_val = props.get(status_prop, {}).get('checkbox')
                    if checkbox_val is True:
                        is_done = True
                
                if not is_done and due_date >= today:
                    active_assignments.append({
                        'name': name,
                        'due_date': due_date,
                        'status': status
                    })
                
                # Check if due in next 7 days
                if today <= due_date <= next_week:
                    upcoming_deadlines.append((due_date, name))
    
    # Sort results
    active_assignments.sort(key=lambda x: x['due_date'])
    upcoming_deadlines.sort(key=lambda x: x[0])
    
    # Remove duplicates from upcoming_deadlines
    seen = set()
    unique_upcoming = []
    for due_date, name in upcoming_deadlines:
        if (due_date, name) not in seen:
            seen.add((due_date, name))
            unique_upcoming.append((due_date, name))
    upcoming_deadlines = unique_upcoming
    
    # Output
    print("📝 Seminary Writing Check")
    print()
    print("📚 Active Assignments")
    if active_assignments:
        for a in active_assignments:
            print(f"- {a['name']} — due {a['due_date']} — {a['status']}")
    else:
        print("No assignments found")
    
    print()
    print("📅 Upcoming Deadlines (next 7 days)")
    if upcoming_deadlines:
        for due_date, name in upcoming_deadlines:
            print(f"- {due_date}: {name}")
    else:
        print("No upcoming deadlines")
    
    print()
    print("💡 Suggested Action")
    if active_assignments:
        next_assignment = active_assignments[0]
        print(f"Work on '{next_assignment['name']}' which is due {next_assignment['due_date']}")
    elif upcoming_deadlines:
        next_due, next_name = upcoming_deadlines[0]
        print(f"Start working on '{next_name}' which is due {next_due}")
    else:
        print("No active assignments tracked. Consider creating a writing tracker database in Notion.")

if __name__ == '__main__':
    main()