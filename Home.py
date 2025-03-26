import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
from models import Task
import sheets_utils

st.set_page_config(
    page_title="智能待辦事項管理系統",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("智能待辦事項管理系統")
    
    # 載入數據
    tasks = sheets_utils.get_active_tasks()
    parameters = sheets_utils.load_parameters()
    
    # 創建頁籤
    tab1, tab2, tab3 = st.tabs(["任務列表", "新增/編輯任務", "任務概覽"])
    
    with tab1:
        display_tasks(tasks, parameters)
    
    with tab2:
        add_edit_task(parameters)
    
    with tab3:
        task_overview(tasks)

def display_tasks(tasks, parameters):
    """Display and manage existing tasks."""
    st.header("Task List")
    
    if not tasks:
        st.info("No tasks available. Add a task to get started.")
        return
    
    # Convert tasks to DataFrame for display
    df = sheets_utils.tasks_to_dataframe(tasks)
    
    # Add filter options in sidebar
    with st.expander("Filter Tasks", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Text search
            search_term = st.text_input("Search in Sub Task", key="search_subtask")
            
            # Main task filter
            selected_main_task = st.selectbox(
                "Main Task", 
                options=["All"] + parameters["main_task"],
                key="filter_main_task"
            )
            
            # Priority filter
            selected_priority = st.selectbox(
                "Priority", 
                options=["All"] + parameters["priority"],
                key="filter_priority"
            )
        
        with col2:
            # Status filter
            selected_status = st.selectbox(
                "Status", 
                options=["All"] + parameters["status"],
                key="filter_status"
            )
            
            # Responsible filter
            selected_responsible = st.selectbox(
                "Responsible", 
                options=["All"] + parameters["responsible"],
                key="filter_responsible"
            )
            
            # Date range
            use_date_filter = st.checkbox("Filter by End Date", key="use_date_filter")
            if use_date_filter:
                date_range = st.date_input(
                    "End Date Range",
                    value=(date.today(), date.today()),
                    key="date_filter"
                )
    
    # Apply filters
    filtered_tasks = tasks
    
    if search_term:
        filtered_tasks = [t for t in filtered_tasks if search_term.lower() in t.sub_task.lower()]
    
    if selected_main_task != "All":
        filtered_tasks = [t for t in filtered_tasks if t.main_task == selected_main_task]
    
    if selected_priority != "All":
        filtered_tasks = [t for t in filtered_tasks if t.priority == selected_priority]
    
    if selected_status != "All":
        filtered_tasks = [t for t in filtered_tasks if t.status == selected_status]
    
    if selected_responsible != "All":
        filtered_tasks = [t for t in filtered_tasks if t.responsible == selected_responsible]
    
    if use_date_filter and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_tasks = [
            t for t in filtered_tasks 
            if t.end_date and start_date <= t.end_date <= end_date
        ]
    
    # Convert filtered tasks to DataFrame
    filtered_df = sheets_utils.tasks_to_dataframe(filtered_tasks)
    
    if filtered_df.empty:
        st.info("No tasks match the selected filters.")
        return
    
    # Display tasks with edit and delete buttons
    for index, row in filtered_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 0.5])
            
            with col1:
                task_title = f"**{row['Sub Task']}** ({row['Main Task']})"
                st.markdown(task_title)
                
                details = (
                    f"**Priority:** {row['Priority']} | "
                    f"**Status:** {row['Status']} | "
                    f"**Responsible:** {row['Responsible']}"
                )
                st.markdown(details)
                
                if row['Start Date'] and row['End Date']:
                    dates = f"**Timeline:** {row['Start Date'].strftime('%Y-%m-%d')} to {row['End Date'].strftime('%Y-%m-%d')}"
                    st.markdown(dates)
                
                if row['Notes']:
                    st.markdown(f"**Notes:** {row['Notes']}")
            
            with col2:
                st.button("Edit", key=f"edit_{row['ID']}", on_click=set_task_for_edit, args=(row['ID'],))
            
            with col3:
                st.button("🗑️", key=f"delete_{row['ID']}", on_click=delete_task, args=(row['ID'],))
            
            st.divider()

def set_task_for_edit(task_id):
    """Set the task to be edited in session state."""
    task = sheets_utils.get_task_by_id(task_id)
    if task:
        st.session_state['editing_task'] = task
        st.session_state['is_editing'] = True

def delete_task(task_id):
    """Delete a task."""
    if st.session_state.get('is_editing', False) and \
       st.session_state.get('editing_task') and \
       st.session_state['editing_task'].id == task_id:
        st.session_state['is_editing'] = False
        st.session_state['editing_task'] = None
    
    sheets_utils.delete_task(task_id)
    st.success("Task marked as deleted!")
    st.rerun()

def add_edit_task(parameters):
    """Add a new task or edit an existing one."""
    is_editing = st.session_state.get('is_editing', False)
    editing_task = st.session_state.get('editing_task', None)
    
    if is_editing:
        st.header("Edit Task")
    else:
        st.header("Add New Task")
    
    with st.form(key="task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sub_task = st.text_input(
                "Sub Task", 
                value=editing_task.sub_task if is_editing else ""
            )
            
            main_task = st.selectbox(
                "Main Task", 
                options=parameters["main_task"],
                index=parameters["main_task"].index(editing_task.main_task) if is_editing and editing_task.main_task in parameters["main_task"] else 0
            )
            
            priority = st.selectbox(
                "Priority", 
                options=parameters["priority"],
                index=parameters["priority"].index(editing_task.priority) if is_editing and editing_task.priority in parameters["priority"] else 1
            )
            
            status = st.selectbox(
                "Status", 
                options=parameters["status"],
                index=parameters["status"].index(editing_task.status) if is_editing and editing_task.status in parameters["status"] else 0
            )
        
        with col2:
            start_date = st.date_input(
                "Start Date",
                value=editing_task.start_date if is_editing and editing_task.start_date else date.today()
            )
            
            end_date = st.date_input(
                "End Date",
                value=editing_task.end_date if is_editing and editing_task.end_date else date.today()
            )
            
            responsible = st.selectbox(
                "Responsible", 
                options=parameters["responsible"],
                index=parameters["responsible"].index(editing_task.responsible) if is_editing and editing_task.responsible in parameters["responsible"] else 0
            )
        
        notes = st.text_area(
            "Notes",
            value=editing_task.notes if is_editing else ""
        )
        
        submit_label = "Update Task" if is_editing else "Add Task"
        submitted = st.form_submit_button(submit_label)
        
        if submitted:
            if not sub_task:
                st.error("Sub Task cannot be empty!")
                return
            
            if end_date < start_date:
                st.error("End Date must be on or after Start Date!")
                return
            
            if is_editing:
                # Update existing task
                updated_task = Task(
                    id=editing_task.id,
                    sub_task=sub_task,
                    main_task=main_task,
                    priority=priority,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    responsible=responsible,
                    notes=notes,
                    status_update_time=datetime.now(),
                    is_deleted=False
                )
                sheets_utils.update_task(editing_task.id, updated_task)
                st.session_state['is_editing'] = False
                st.session_state['editing_task'] = None
                st.success("Task updated successfully!")
            else:
                # Create new task
                new_task = Task(
                    sub_task=sub_task,
                    main_task=main_task,
                    priority=priority,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    responsible=responsible,
                    notes=notes
                )
                sheets_utils.add_task(new_task)
                st.success("Task added successfully!")
            
            st.rerun()
    
    if is_editing:
        if st.button("Cancel Editing"):
            st.session_state['is_editing'] = False
            st.session_state['editing_task'] = None
            st.rerun()

def task_overview(tasks):
    """Show task overview and visualizations."""
    st.header("Task Overview")
    
    if not tasks:
        st.info("No tasks available for analysis. Add some tasks first.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = {}
        for task in tasks:
            if task.status in status_counts:
                status_counts[task.status] += 1
            else:
                status_counts[task.status] = 1
                
        df_status = pd.DataFrame({
            'Status': list(status_counts.keys()),
            'Count': list(status_counts.values())
        })
        
        fig_status = px.pie(
            df_status, 
            values='Count', 
            names='Status', 
            title='Task Status Distribution',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Priority distribution
        priority_counts = {}
        for task in tasks:
            if task.priority in priority_counts:
                priority_counts[task.priority] += 1
            else:
                priority_counts[task.priority] = 1
                
        df_priority = pd.DataFrame({
            'Priority': list(priority_counts.keys()),
            'Count': list(priority_counts.values())
        })
        
        fig_priority = px.pie(
            df_priority, 
            values='Count', 
            names='Priority', 
            title='Task Priority Distribution',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # Calculate overall progress
    progress = sheets_utils.calculate_task_progress(tasks)
    st.subheader("Overall Progress")
    st.progress(progress / 100)
    st.text(f"{progress:.1f}% of tasks completed")
    
    # Task timeline
    tasks_with_dates = [task for task in tasks if task.start_date and task.end_date]
    if tasks_with_dates:
        st.subheader("Task Timeline")
        
        df_timeline = pd.DataFrame([
            {
                'Task': task.sub_task,
                'Start': task.start_date,
                'End': task.end_date,
                'Status': task.status,
                'Priority': task.priority
            }
            for task in tasks_with_dates
        ])
        
        fig_timeline = px.timeline(
            df_timeline,
            x_start='Start',
            x_end='End',
            y='Task',
            color='Status',
            hover_data=['Priority'],
            title="Task Timeline"
        )
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)

if __name__ == "__main__":
    main()
