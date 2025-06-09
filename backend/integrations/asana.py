"""Asana integration stubs."""

import os

API_TOKEN = os.getenv("ASANA_API_TOKEN")
PROJECT_ID = os.getenv("ASANA_PROJECT_ID")


def create_task(title: str, description: str):
    """Simulate creating a task in Asana."""
    if not API_TOKEN or not PROJECT_ID:
        print("Asana credentials not configured")
        return False
    print(f"Would create Asana task '{title}' in project {PROJECT_ID}")
    return True


def update_task(task_id: str, status: str):
    """Simulate updating a task's status in Asana."""
    if not API_TOKEN or not PROJECT_ID:
        print("Asana credentials not configured")
        return False
    print(f"Would update Asana task {task_id} to status '{status}'")
    return True
