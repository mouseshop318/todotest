import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sheets_utils
from models import Task

st.set_page_config(
    page_title="篩選視圖 - 待辦事項管理系統",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.title("任務篩選視圖")
    st.write("以不同方式篩選和視覺化任務。")
    
    # 載入數據
    tasks = sheets_utils.get_active_tasks()
    parameters = sheets_utils.load_parameters()
    
    if not tasks:
        st.info("沒有可用的任務。請先在主頁面新增一些任務。")
        return
    
    # 創建不同視圖的頁籤
    tab1, tab2, tab3, tab4 = st.tabs([
        "進階篩選", 
        "日曆視圖", 
        "預設篩選器",
        "任務統計"
    ])
    
    with tab1:
        advanced_filter_view(tasks, parameters)
    
    with tab2:
        calendar_view(tasks)
    
    with tab3:
        predefined_filters_view(tasks)
    
    with tab4:
        task_statistics_view(tasks, parameters)

def advanced_filter_view(tasks, parameters):
    """Advanced filter view with multiple filter options."""
    st.header("Advanced Filter")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Text search
        search_term = st.text_input("Search in Sub Task", key="adv_search_subtask")
        
        # Main task filter
        selected_main_task = st.multiselect(
            "Main Task", 
            options=parameters["main_task"],
            key="adv_filter_main_task"
        )
        
        # Priority filter
        selected_priority = st.multiselect(
            "Priority", 
            options=parameters["priority"],
            key="adv_filter_priority"
        )
    
    with col2:
        # Status filter
        selected_status = st.multiselect(
            "Status", 
            options=parameters["status"],
            key="adv_filter_status"
        )
        
        # Responsible filter
        selected_responsible = st.multiselect(
            "Responsible", 
            options=parameters["responsible"],
            key="adv_filter_responsible"
        )
    
    with col3:
        # Date range for start date
        use_start_date_filter = st.checkbox("Filter by Start Date", key="use_start_date_filter")
        if use_start_date_filter:
            start_date_range = st.date_input(
                "Start Date Range",
                value=(date.today() - timedelta(days=30), date.today() + timedelta(days=30)),
                key="start_date_filter"
            )
        
        # Date range for end date
        use_end_date_filter = st.checkbox("Filter by End Date", key="use_end_date_filter")
        if use_end_date_filter:
            end_date_range = st.date_input(
                "End Date Range",
                value=(date.today() - timedelta(days=30), date.today() + timedelta(days=30)),
                key="end_date_filter"
            )
    
    # Apply filters
    filtered_tasks = tasks
    
    if search_term:
        filtered_tasks = [t for t in filtered_tasks if search_term.lower() in t.sub_task.lower()]
    
    if selected_main_task:
        filtered_tasks = [t for t in filtered_tasks if t.main_task in selected_main_task]
    
    if selected_priority:
        filtered_tasks = [t for t in filtered_tasks if t.priority in selected_priority]
    
    if selected_status:
        filtered_tasks = [t for t in filtered_tasks if t.status in selected_status]
    
    if selected_responsible:
        filtered_tasks = [t for t in filtered_tasks if t.responsible in selected_responsible]
    
    if use_start_date_filter and len(start_date_range) == 2:
        start_date, end_date = start_date_range
        filtered_tasks = [
            t for t in filtered_tasks 
            if t.start_date and start_date <= t.start_date <= end_date
        ]
    
    if use_end_date_filter and len(end_date_range) == 2:
        start_date, end_date = end_date_range
        filtered_tasks = [
            t for t in filtered_tasks 
            if t.end_date and start_date <= t.end_date <= end_date
        ]
    
    # Display results
    st.subheader("Filter Results")
    if not filtered_tasks:
        st.info("No tasks match the selected filters.")
        return
    
    # Display options
    view_option = st.radio(
        "Select View",
        options=["Table View", "Card View"],
        horizontal=True
    )
    
    if view_option == "Table View":
        display_table_view(filtered_tasks)
    else:
        display_card_view(filtered_tasks)

def display_table_view(tasks):
    """Display tasks in a table format."""
    df = sheets_utils.tasks_to_dataframe(tasks)
    
    # Reorder columns for better display
    display_columns = [
        'Sub Task', 'Main Task', 'Priority', 'Status', 
        'Start Date', 'End Date', 'Responsible', 'Notes'
    ]
    
    # Format dates for display
    if 'Start Date' in df.columns:
        df['Start Date'] = df['Start Date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '')
    
    if 'End Date' in df.columns:
        df['End Date'] = df['End Date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '')
    
    # Display the table
    st.dataframe(df[display_columns], use_container_width=True)
    
    # Export options
    if st.button("Export to CSV"):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="tasks_export.csv",
            mime="text/csv"
        )

def display_card_view(tasks):
    """Display tasks in a card format."""
    # Create columns for cards layout
    col1, col2 = st.columns(2)
    
    # Distribute tasks between columns
    for i, task in enumerate(tasks):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            with st.container(border=True):
                st.subheader(task.sub_task)
                st.caption(f"**Main Task:** {task.main_task}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Priority:** {task.priority}")
                    st.write(f"**Status:** {task.status}")
                
                with col_b:
                    st.write(f"**Responsible:** {task.responsible}")
                    if task.start_date and task.end_date:
                        st.write(f"**Timeline:** {task.start_date.strftime('%Y-%m-%d')} to {task.end_date.strftime('%Y-%m-%d')}")
                
                if task.notes:
                    st.write(f"**Notes:** {task.notes}")

def calendar_view(tasks):
    """Display tasks in a calendar-like view."""
    st.header("Calendar View")
    
    # Filter to tasks with dates
    tasks_with_dates = [task for task in tasks if task.start_date and task.end_date]
    
    if not tasks_with_dates:
        st.info("No tasks with defined start and end dates available.")
        return
    
    # Month view selection
    today = date.today()
    selected_month = st.selectbox(
        "Select Month",
        options=[
            (today.replace(month=((today.month - i - 1) % 12) + 1, year=today.year - ((today.month - i - 1) // 12)))
            for i in range(-3, 9)  # Show 3 months before and 8 months ahead
        ],
        format_func=lambda x: x.strftime("%B %Y"),
        index=3  # Default to current month
    )
    
    # Get the first and last day of selected month
    first_day = selected_month.replace(day=1)
    if selected_month.month == 12:
        last_day = selected_month.replace(year=selected_month.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = selected_month.replace(month=selected_month.month + 1, day=1) - timedelta(days=1)
    
    # Filter tasks for the selected month
    month_tasks = []
    for task in tasks_with_dates:
        # Check if task falls within or overlaps with the selected month
        if (task.start_date <= last_day and 
            (task.end_date >= first_day if task.end_date else True)):
            month_tasks.append(task)
    
    if not month_tasks:
        st.info(f"No tasks found for {selected_month.strftime('%B %Y')}.")
        return
    
    # Create a timeline view for the selected month
    df_timeline = pd.DataFrame([
        {
            'Task': task.sub_task,
            'Start': max(task.start_date, first_day),
            'End': min(task.end_date, last_day) if task.end_date else last_day,
            'Status': task.status,
            'Priority': task.priority,
            'Main Task': task.main_task
        }
        for task in month_tasks
    ])
    
    fig_timeline = px.timeline(
        df_timeline,
        x_start='Start',
        x_end='End',
        y='Task',
        color='Status',
        hover_data=['Priority', 'Main Task'],
        title=f"Task Calendar - {selected_month.strftime('%B %Y')}"
    )
    fig_timeline.update_yaxes(autorange="reversed")
    
    # Add vertical line for today if today is in the selected month
    if first_day <= today <= last_day:
        # Convert datetime.date to timestamp for plotly
        today_str = today.strftime('%Y-%m-%d')
        fig_timeline.add_vline(
            x=today_str,
            line_width=2,
            line_dash="dash",
            line_color="green",
            annotation_text="今天"
        )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Daily view
    st.subheader("Daily Task View")
    
    # Create a date range for the entire month
    all_days = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
    selected_day = st.select_slider(
        "Select Day",
        options=all_days,
        value=today if first_day <= today <= last_day else first_day,
        format_func=lambda x: x.strftime("%a, %b %d")
    )
    
    # Filter tasks for the selected day
    day_tasks = [
        task for task in tasks_with_dates
        if task.start_date <= selected_day <= task.end_date
    ]
    
    if not day_tasks:
        st.info(f"No tasks for {selected_day.strftime('%A, %B %d')}.")
        return
    
    # Display tasks for the selected day
    st.write(f"Tasks for {selected_day.strftime('%A, %B %d, %Y')}:")
    
    for task in day_tasks:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(task.sub_task)
                st.caption(f"**{task.main_task}** | {task.status}")
                st.write(f"**Priority:** {task.priority} | **Responsible:** {task.responsible}")
                
                # Calculate days remaining or overdue
                if task.end_date:
                    if task.end_date >= today:
                        days_left = (task.end_date - today).days
                        st.write(f"**Due in:** {days_left} days")
                    else:
                        days_overdue = (today - task.end_date).days
                        st.write(f"**Overdue by:** {days_overdue} days")
            
            with col2:
                # Show a colored indicator based on status
                status_color = {
                    "Not Started": "gray",
                    "In Progress": "blue",
                    "Completed": "green",
                    "On Hold": "orange"
                }.get(task.status, "gray")
                
                st.markdown(
                    f"<div style='background-color: {status_color}; "
                    f"width: 20px; height: 20px; border-radius: 50%; margin: auto;'></div>",
                    unsafe_allow_html=True
                )

def predefined_filters_view(tasks):
    """Display predefined filter options and results."""
    st.header("Predefined Filters")
    
    filter_option = st.selectbox(
        "Select Filter",
        options=[
            "Recently Completed Tasks (Past Week)",
            "Upcoming Tasks (Next 3 Weeks)",
            "Current Year Tasks",
            "Custom Date Range"
        ]
    )
    
    filtered_tasks = []
    
    if filter_option == "Recently Completed Tasks (Past Week)":
        filtered_tasks = sheets_utils.get_recently_completed_tasks(7)
        time_description = "completed in the past 7 days"
    
    elif filter_option == "Upcoming Tasks (Next 3 Weeks)":
        filtered_tasks = sheets_utils.get_upcoming_tasks(21)
        time_description = "due in the next 3 weeks"
    
    elif filter_option == "Current Year Tasks":
        filtered_tasks = sheets_utils.get_current_year_tasks()
        current_year = date.today().year
        time_description = f"for the year {current_year}"
    
    elif filter_option == "Custom Date Range":
        # Custom date range selector
        date_range = st.date_input(
            "Select Date Range",
            value=(date.today() - timedelta(days=30), date.today() + timedelta(days=30)),
            key="custom_date_range"
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_tasks = sheets_utils.get_custom_period_tasks(start_date, end_date)
            time_description = f"between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}"
        else:
            st.error("Please select both start and end dates.")
            return
    
    # Display results
    if not filtered_tasks:
        st.info(f"No tasks {time_description}.")
        return
    
    st.subheader(f"Tasks {time_description} ({len(filtered_tasks)} tasks)")
    
    # Display options
    view_option = st.radio(
        "Select View",
        options=["Table View", "Summary View"],
        horizontal=True
    )
    
    if view_option == "Table View":
        display_table_view(filtered_tasks)
    else:
        # Summary view with grouping
        df = sheets_utils.tasks_to_dataframe(filtered_tasks)
        
        # Group by selected fields
        group_by = st.multiselect(
            "Group By",
            options=["Main Task", "Status", "Priority", "Responsible"],
            default=["Status"]
        )
        
        if not group_by:
            st.warning("Please select at least one field to group by.")
            display_table_view(filtered_tasks)
        else:
            # Create summary dataframe with counts
            summary = df.groupby(group_by).size().reset_index(name='Count')
            
            # Display summary table
            st.dataframe(summary, use_container_width=True)
            
            # Create a visualization based on the grouping
            if len(group_by) == 1:
                # Single dimension grouping - use pie chart
                fig = px.pie(
                    summary, 
                    values='Count', 
                    names=group_by[0], 
                    title=f'Tasks by {group_by[0]}'
                )
                st.plotly_chart(fig, use_container_width=True)
            elif len(group_by) == 2:
                # Two dimensions - use grouped bar chart
                fig = px.bar(
                    summary, 
                    x=group_by[0], 
                    y='Count', 
                    color=group_by[1],
                    title=f'Tasks by {group_by[0]} and {group_by[1]}'
                )
                st.plotly_chart(fig, use_container_width=True)

def task_statistics_view(tasks, parameters):
    """Display task statistics and visualizations."""
    st.header("Task Statistics")
    
    if not tasks:
        st.info("No tasks available for analysis.")
        return
    
    # Basic statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == "Completed")
    completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    
    # Create a summary box
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        st.metric("Completed Tasks", completed_tasks)
    
    with col3:
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Tasks by status
    status_counts = {}
    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        else:
            status_counts[task.status] = 1
    
    # Tasks by priority
    priority_counts = {}
    for task in tasks:
        if task.priority in priority_counts:
            priority_counts[task.priority] += 1
        else:
            priority_counts[task.priority] = 1
    
    # Tasks by responsible person
    responsible_counts = {}
    for task in tasks:
        if task.responsible in responsible_counts:
            responsible_counts[task.responsible] += 1
        else:
            responsible_counts[task.responsible] = 1
    
    # Display visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        df_status = pd.DataFrame({
            'Status': list(status_counts.keys()),
            'Count': list(status_counts.values())
        })
        
        fig_status = px.bar(
            df_status,
            x='Status',
            y='Count',
            title='Tasks by Status',
            color='Status'
        )
        st.plotly_chart(fig_status, use_container_width=True)
        
        # Responsible distribution
        df_responsible = pd.DataFrame({
            'Responsible': list(responsible_counts.keys()),
            'Count': list(responsible_counts.values())
        })
        
        fig_responsible = px.bar(
            df_responsible,
            x='Responsible',
            y='Count',
            title='Tasks by Responsible Person',
            color='Responsible'
        )
        st.plotly_chart(fig_responsible, use_container_width=True)
    
    with col2:
        # Priority distribution
        df_priority = pd.DataFrame({
            'Priority': list(priority_counts.keys()),
            'Count': list(priority_counts.values())
        })
        
        fig_priority = px.bar(
            df_priority,
            x='Priority',
            y='Count',
            title='Tasks by Priority',
            color='Priority'
        )
        st.plotly_chart(fig_priority, use_container_width=True)
        
        # Completion rate over time (if there are enough tasks with dates)
        tasks_with_updates = [task for task in tasks if task.status_update_time]
        
        if tasks_with_updates:
            # Group tasks by week
            df_tasks = pd.DataFrame([
                {
                    'Date': task.status_update_time,
                    'Status': task.status
                }
                for task in tasks_with_updates
            ])
            
            # Add a week column
            df_tasks['Week'] = df_tasks['Date'].dt.strftime('%Y-%U')
            df_tasks['IsCompleted'] = df_tasks['Status'] == 'Completed'
            
            # Group by week and count completed vs. total
            weekly_stats = df_tasks.groupby('Week').agg(
                Completed=('IsCompleted', 'sum'),
                Total=('IsCompleted', 'count')
            ).reset_index()
            
            # Calculate completion rate
            weekly_stats['CompletionRate'] = (weekly_stats['Completed'] / weekly_stats['Total']) * 100
            
            # Create line chart
            fig_completion = px.line(
                weekly_stats,
                x='Week',
                y='CompletionRate',
                title='Weekly Task Completion Rate',
                markers=True
            )
            fig_completion.update_layout(yaxis_title='Completion Rate (%)')
            st.plotly_chart(fig_completion, use_container_width=True)

if __name__ == "__main__":
    main()
