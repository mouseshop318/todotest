import streamlit as st
import pandas as pd
from datetime import datetime
import sheets_utils

st.set_page_config(
    page_title="Removed Tasks - To-Do Management System",
    page_icon="🗑️",
    layout="wide"
)

def main():
    st.title("Removed Tasks")
    st.write("View and manage deleted tasks. You can restore tasks or permanently delete them.")
    
    # Load deleted tasks
    deleted_tasks = sheets_utils.get_deleted_tasks()
    
    if not deleted_tasks:
        st.info("No deleted tasks found.")
        return
    
    # Convert to DataFrame for display
    df = sheets_utils.tasks_to_dataframe(deleted_tasks)
    
    # Sort by deletion time (status_update_time) with most recent first
    df['Deletion Time'] = pd.to_datetime([task.status_update_time for task in deleted_tasks])
    df = df.sort_values('Deletion Time', ascending=False)
    
    # Display tasks with restore and permanently delete options
    st.subheader(f"Deleted Tasks ({len(deleted_tasks)})")
    
    # Display options
    view_option = st.radio(
        "Select View",
        options=["Table View", "Detailed View"],
        horizontal=True
    )
    
    if view_option == "Table View":
        display_table_view(deleted_tasks, df)
    else:
        display_detailed_view(deleted_tasks)
    
    # Cleanup options
    st.subheader("Cleanup Options")
    if st.button("Permanently Delete All Tasks"):
        if st.warning("This action cannot be undone. Are you sure?"):
            if st.button("Yes, Permanently Delete All"):
                for task in deleted_tasks:
                    sheets_utils.permanently_delete_task(task.id)
                st.success("All deleted tasks have been permanently removed.")
                st.rerun()

def display_table_view(deleted_tasks, df):
    """Display deleted tasks in a table format with action buttons."""
    # Format dates for display
    display_df = df.copy()
    
    if 'Start Date' in display_df.columns:
        display_df['Start Date'] = display_df['Start Date'].apply(
            lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else ''
        )
    
    if 'End Date' in display_df.columns:
        display_df['End Date'] = display_df['End Date'].apply(
            lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else ''
        )
    
    if 'Deletion Time' in display_df.columns:
        display_df['Deletion Time'] = display_df['Deletion Time'].apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M') if pd.notna(x) else ''
        )
    
    # Display columns for table view
    display_columns = [
        'Sub Task', 'Main Task', 'Priority', 'Status', 
        'Start Date', 'End Date', 'Responsible', 'Deletion Time'
    ]
    
    # Show the table
    st.dataframe(display_df[display_columns], use_container_width=True)
    
    # Actions for selected tasks
    st.subheader("Task Actions")
    
    # Select tasks to act on
    task_options = {f"{task.sub_task} ({task.main_task})": task.id for task in deleted_tasks}
    selected_task_ids = st.multiselect(
        "Select Tasks to Restore or Permanently Delete",
        options=list(task_options.keys())
    )
    
    # Convert selected task names to IDs
    selected_ids = [task_options[name] for name in selected_task_ids]
    
    if selected_ids:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Restore Selected", key="restore_selected"):
                for task_id in selected_ids:
                    sheets_utils.restore_task(task_id)
                st.success(f"Restored {len(selected_ids)} task(s).")
                st.rerun()
        
        with col2:
            if st.button("Permanently Delete Selected", key="delete_selected"):
                for task_id in selected_ids:
                    sheets_utils.permanently_delete_task(task_id)
                st.success(f"Permanently deleted {len(selected_ids)} task(s).")
                st.rerun()

def display_detailed_view(deleted_tasks):
    """Display detailed view of deleted tasks with cards."""
    # Sort tasks by deletion time (most recent first)
    sorted_tasks = sorted(
        deleted_tasks,
        key=lambda x: x.status_update_time if x.status_update_time else datetime.min,
        reverse=True
    )
    
    # Create columns for cards layout
    col1, col2 = st.columns(2)
    
    # Distribute tasks between columns
    for i, task in enumerate(sorted_tasks):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            with st.container(border=True):
                st.subheader(task.sub_task)
                st.caption(f"**Main Task:** {task.main_task}")
                
                col_a, col_b, col_c = st.columns([2, 2, 1])
                
                with col_a:
                    st.write(f"**Priority:** {task.priority}")
                    st.write(f"**Status:** {task.status}")
                
                with col_b:
                    st.write(f"**Responsible:** {task.responsible}")
                    if task.start_date and task.end_date:
                        st.write(f"**Timeline:** {task.start_date.strftime('%Y-%m-%d')} to {task.end_date.strftime('%Y-%m-%d')}")
                
                with col_c:
                    # Display deletion time
                    if task.status_update_time:
                        st.write(f"**Deleted:** {task.status_update_time.strftime('%Y-%m-%d')}")
                
                if task.notes:
                    st.write(f"**Notes:** {task.notes}")
                
                # Action buttons
                col_action1, col_action2 = st.columns(2)
                
                with col_action1:
                    if st.button("Restore", key=f"restore_{task.id}"):
                        sheets_utils.restore_task(task.id)
                        st.success(f"Task '{task.sub_task}' restored!")
                        st.rerun()
                
                with col_action2:
                    if st.button("Delete Permanently", key=f"perm_delete_{task.id}"):
                        sheets_utils.permanently_delete_task(task.id)
                        st.success(f"Task '{task.sub_task}' permanently deleted!")
                        st.rerun()

if __name__ == "__main__":
    main()
