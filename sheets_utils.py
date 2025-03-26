import pandas as pd
import json
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Union
import streamlit as st
from models import Task, SystemParameter

# File paths for data storage
TASKS_FILE = "tasks_data.json"
PARAMS_FILE = "system_parameters.json"

def load_tasks() -> List[Task]:
    """Load tasks from session state or initialize if not exists."""
    if 'tasks' not in st.session_state:
        # Initialize with empty list or load from storage
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r') as f:
                    tasks_data = json.load(f)
                tasks = [Task.from_dict(task) for task in tasks_data]
                st.session_state['tasks'] = tasks
            except Exception as e:
                st.error(f"Error loading tasks: {e}")
                st.session_state['tasks'] = []
        else:
            st.session_state['tasks'] = []
    
    return st.session_state.tasks

def save_tasks(tasks: List[Task]) -> None:
    """Save tasks to session state and storage."""
    st.session_state['tasks'] = tasks
    tasks_data = [task.to_dict() for task in tasks]
    try:
        with open(TASKS_FILE, 'w') as f:
            json.dump(tasks_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving tasks: {e}")

def load_parameters() -> Dict[str, List[str]]:
    """Load system parameters from session state or initialize if not exists."""
    if 'parameters' not in st.session_state:
        # Initialize with default parameters or load from storage
        default_params = {
            'status': ['Not Started', 'In Progress', 'Completed', 'On Hold'],
            'priority': ['Low', 'Medium', 'High', 'Critical'],
            'responsible': ['Team Member 1', 'Team Member 2', 'Team Member 3'],
            'main_task': ['Project A', 'Project B', 'Maintenance', 'Research']
        }
        
        if os.path.exists(PARAMS_FILE):
            try:
                with open(PARAMS_FILE, 'r') as f:
                    loaded_params = json.load(f)
                st.session_state['parameters'] = loaded_params
            except Exception as e:
                st.error(f"Error loading parameters: {e}")
                st.session_state['parameters'] = default_params
        else:
            st.session_state['parameters'] = default_params
    
    return st.session_state.parameters

def save_parameters(parameters: Dict[str, List[str]]) -> None:
    """Save system parameters to session state and storage."""
    st.session_state['parameters'] = parameters
    try:
        with open(PARAMS_FILE, 'w') as f:
            json.dump(parameters, f, indent=2)
    except Exception as e:
        st.error(f"Error saving parameters: {e}")

def add_task(task: Task) -> None:
    """Add a new task to the task list."""
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

def update_task(task_id: str, updated_task: Task) -> None:
    """Update an existing task."""
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks[i] = updated_task
            break
    save_tasks(tasks)

def delete_task(task_id: str) -> None:
    """Mark a task as deleted."""
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks[i].is_deleted = True
            tasks[i].status_update_time = datetime.now()
            break
    save_tasks(tasks)

def restore_task(task_id: str) -> None:
    """Restore a deleted task."""
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks[i].is_deleted = False
            tasks[i].status_update_time = datetime.now()
            break
    save_tasks(tasks)

def permanently_delete_task(task_id: str) -> None:
    """Permanently remove a task from the list."""
    tasks = load_tasks()
    tasks = [task for task in tasks if task.id != task_id]
    save_tasks(tasks)

def get_active_tasks() -> List[Task]:
    """Get all non-deleted tasks."""
    return [task for task in load_tasks() if not task.is_deleted]

def get_deleted_tasks() -> List[Task]:
    """Get all deleted tasks."""
    return [task for task in load_tasks() if task.is_deleted]

def filter_tasks(
    tasks: List[Task],
    sub_task: Optional[str] = None,
    main_task: Optional[str] = None,
    priority: Optional[str] = None,
    responsible: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Task]:
    """Filter tasks based on given criteria."""
    filtered_tasks = tasks
    
    if sub_task:
        filtered_tasks = [t for t in filtered_tasks if sub_task.lower() in t.sub_task.lower()]
    
    if main_task:
        filtered_tasks = [t for t in filtered_tasks if t.main_task == main_task]
    
    if priority:
        filtered_tasks = [t for t in filtered_tasks if t.priority == priority]
    
    if responsible:
        filtered_tasks = [t for t in filtered_tasks if t.responsible == responsible]
    
    if status:
        filtered_tasks = [t for t in filtered_tasks if t.status == status]
    
    if start_date:
        filtered_tasks = [t for t in filtered_tasks if t.start_date and t.start_date >= start_date]
    
    if end_date:
        filtered_tasks = [t for t in filtered_tasks if t.end_date and t.end_date <= end_date]
    
    return filtered_tasks

def get_recently_completed_tasks(days: int = 7) -> List[Task]:
    """Get tasks completed in the last 'days' days."""
    cutoff_date = datetime.now() - timedelta(days=days)
    active_tasks = get_active_tasks()
    return [
        task for task in active_tasks 
        if task.status == "Completed" and task.status_update_time >= cutoff_date
    ]

def get_upcoming_tasks(days: int = 21) -> List[Task]:
    """Get incomplete tasks due in the next 'days' days."""
    today = date.today()
    future_date = today + timedelta(days=days)
    active_tasks = get_active_tasks()
    return [
        task for task in active_tasks 
        if task.status != "Completed" and task.end_date and today <= task.end_date <= future_date
    ]

def get_current_year_tasks() -> List[Task]:
    """Get all tasks for the current year."""
    current_year = date.today().year
    active_tasks = get_active_tasks()
    return [
        task for task in active_tasks 
        if (task.start_date and task.start_date.year == current_year) or
           (task.end_date and task.end_date.year == current_year)
    ]

def get_custom_period_tasks(start: date, end: date) -> List[Task]:
    """Get tasks within a custom date range."""
    active_tasks = get_active_tasks()
    return [
        task for task in active_tasks 
        if (task.start_date and start <= task.start_date <= end) or
           (task.end_date and start <= task.end_date <= end) or
           (task.start_date and task.end_date and task.start_date <= start and task.end_date >= end)
    ]

def tasks_to_dataframe(tasks: List[Task]) -> pd.DataFrame:
    """Convert a list of tasks to a pandas DataFrame."""
    if not tasks:
        return pd.DataFrame(columns=['ID', 'Sub Task', 'Main Task', 'Priority', 'Status', 
                                     'Start Date', 'End Date', 'Responsible', 'Notes'])
    
    data = [
        {
            'ID': task.id,
            'Sub Task': task.sub_task,
            'Main Task': task.main_task,
            'Priority': task.priority,
            'Status': task.status,
            'Start Date': task.start_date,
            'End Date': task.end_date,
            'Responsible': task.responsible,
            'Notes': task.notes
        } for task in tasks
    ]
    
    return pd.DataFrame(data)

def calculate_task_progress(tasks: List[Task]) -> float:
    """Calculate overall progress as percentage of completed tasks."""
    if not tasks:
        return 0.0
    
    completed = sum(1 for task in tasks if task.status == "Completed")
    return (completed / len(tasks)) * 100

def get_task_by_id(task_id: str) -> Optional[Task]:
    """Get a task by its ID."""
    tasks = load_tasks()
    for task in tasks:
        if task.id == task_id:
            return task
    return None
