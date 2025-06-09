"""Jira integration stubs."""

import os

API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")


def create_issue(title: str, description: str):
    """Simulate creating an issue in Jira."""
    if not API_TOKEN or not PROJECT_KEY:
        print("Jira credentials not configured")
        return False
    print(f"Would create Jira issue '{title}' in {PROJECT_KEY}")
    return True


def update_issue(issue_id: str, status: str):
    """Simulate updating an issue's status in Jira."""
    if not API_TOKEN or not PROJECT_KEY:
        print("Jira credentials not configured")
        return False
    print(f"Would update Jira issue {issue_id} to status '{status}'")
    return True
