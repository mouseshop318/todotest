
import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from models import Task
import sheets_utils

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
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/mouseshop318/todotest',
        'Report a bug': 'https://github.com/mouseshop318/todotest/issues',
        'About': '# 智能待辦事項管理系統\n By mouseshop318'
    }
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
    """顯示和管理現有任務。"""
    st.header("任務列表")
    
    if not tasks:
        st.info("目前沒有可用的任務。請新增一個任務開始使用。")
        return
    
    # 將任務轉換為DataFrame以便顯示
    df = sheets_utils.tasks_to_dataframe(tasks)
    
    # 添加篩選選項
    with st.expander("篩選任務", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # 文字搜索
            search_term = st.text_input("搜索任務子項", key="search_subtask")
            
            # 任務大項篩選
            selected_main_task = st.selectbox(
                "任務大項", 
                options=["全部"] + parameters["main_task"],
                key="filter_main_task"
            )
            
            # 優先級篩選
            selected_priority = st.selectbox(
                "優先級", 
                options=["全部"] + parameters["priority"],
                key="filter_priority"
            )
        
        with col2:
            # 狀態篩選
            selected_status = st.selectbox(
                "狀態", 
                options=["全部"] + parameters["status"],
                key="filter_status"
            )
            
            # 負責人篩選
            selected_responsible = st.selectbox(
                "負責人", 
                options=["全部"] + parameters["responsible"],
                key="filter_responsible"
            )
            
            # 日期範圍
            use_date_filter = st.checkbox("按結束日期篩選", key="use_date_filter")
            if use_date_filter:
                date_range = st.date_input(
                    "結束日期範圍",
                    value=(date.today(), date.today()),
                    key="date_filter"
                )
    
    # 應用篩選條件
    filtered_tasks = tasks
    
    if search_term:
        filtered_tasks = [t for t in filtered_tasks if search_term.lower() in t.sub_task.lower()]
    
    if selected_main_task != "全部":
        filtered_tasks = [t for t in filtered_tasks if t.main_task == selected_main_task]
    
    if selected_priority != "全部":
        filtered_tasks = [t for t in filtered_tasks if t.priority == selected_priority]
    
    if selected_status != "全部":
        filtered_tasks = [t for t in filtered_tasks if t.status == selected_status]
    
    if selected_responsible != "全部":
        filtered_tasks = [t for t in filtered_tasks if t.responsible == selected_responsible]
    
    if use_date_filter and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_tasks = [
            t for t in filtered_tasks 
            if t.end_date and start_date <= t.end_date <= end_date
        ]
    
    # 將篩選後的任務轉換為DataFrame
    filtered_df = sheets_utils.tasks_to_dataframe(filtered_tasks)
    
    if filtered_df.empty:
        st.info("沒有符合篩選條件的任務。")
        return
    
    # 預處理數據以便表格顯示
    display_df = filtered_df.copy()
    
    # 格式化日期列
    if 'Start Date' in display_df.columns:
        display_df['Start Date'] = display_df['Start Date'].apply(
            lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else ''
        )
    
    if 'End Date' in display_df.columns:
        display_df['End Date'] = display_df['End Date'].apply(
            lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else ''
        )
    
    # 創建任務操作的按鈕
    # 首先創建編輯和刪除的功能性按鈕
    edit_buttons = {}
    delete_buttons = {}
    
    # 表格顯示列
    display_columns = [
        'Sub Task', 'Main Task', 'Priority', 'Status', 
        'Start Date', 'End Date', 'Responsible', 'Notes'
    ]
    
    # 顯示表格
    st.dataframe(display_df[display_columns], use_container_width=True)
    
    # 任務操作區域
    st.subheader("任務操作")
    
    # 選擇要操作的任務
    task_options = {f"{task.sub_task} ({task.main_task})": task.id for task in filtered_tasks}
    selected_task = st.selectbox(
        "選擇要編輯或刪除的任務",
        options=list(task_options.keys())
    )
    
    if selected_task:
        selected_task_id = task_options[selected_task]
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("編輯選定的任務", key="edit_selected"):
                set_task_for_edit(selected_task_id)
                st.rerun()
        
        with col2:
            if st.button("刪除選定的任務", key="delete_selected"):
                delete_task(selected_task_id)
                st.rerun()

def set_task_for_edit(task_id):
    """設置要編輯的任務在 session state 中。"""
    task = sheets_utils.get_task_by_id(task_id)
    if task:
        st.session_state['editing_task'] = task
        st.session_state['is_editing'] = True

def delete_task(task_id):
    """刪除任務。"""
    if st.session_state.get('is_editing', False) and \
       st.session_state.get('editing_task') and \
       st.session_state['editing_task'].id == task_id:
        st.session_state['is_editing'] = False
        st.session_state['editing_task'] = None
    
    sheets_utils.delete_task(task_id)
    st.success("任務已標記為刪除！")
    st.rerun()

def add_edit_task(parameters):
    """新增或編輯任務。"""
    is_editing = st.session_state.get('is_editing', False)
    editing_task = st.session_state.get('editing_task', None)
    
    if is_editing:
        st.header("編輯任務")
    else:
        st.header("新增任務")
    
    with st.form(key="task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sub_task = st.text_input(
                "任務子項", 
                value=editing_task.sub_task if is_editing else ""
            )
            
            main_task = st.selectbox(
                "任務大項", 
                options=parameters["main_task"],
                index=parameters["main_task"].index(editing_task.main_task) if is_editing and editing_task.main_task in parameters["main_task"] else 0
            )
            
            priority = st.selectbox(
                "優先級", 
                options=parameters["priority"],
                index=parameters["priority"].index(editing_task.priority) if is_editing and editing_task.priority in parameters["priority"] else 1
            )
            
            status = st.selectbox(
                "狀態", 
                options=parameters["status"],
                index=parameters["status"].index(editing_task.status) if is_editing and editing_task.status in parameters["status"] else 0
            )
        
        with col2:
            start_date = st.date_input(
                "開始日期",
                value=editing_task.start_date if is_editing and editing_task.start_date else date.today()
            )
            
            end_date = st.date_input(
                "結束日期",
                value=editing_task.end_date if is_editing and editing_task.end_date else date.today()
            )
            
            responsible = st.selectbox(
                "負責人", 
                options=parameters["responsible"],
                index=parameters["responsible"].index(editing_task.responsible) if is_editing and editing_task.responsible in parameters["responsible"] else 0
            )
        
        notes = st.text_area(
            "備註",
            value=editing_task.notes if is_editing else ""
        )
        
        submit_label = "更新任務" if is_editing else "新增任務"
        submitted = st.form_submit_button(submit_label)
        
        if submitted:
            if not sub_task:
                st.error("任務子項不能為空！")
                return
            
            if end_date < start_date:
                st.error("結束日期必須在開始日期當天或之後！")
                return
            
            if is_editing:
                # 更新現有任務
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
                st.success("任務更新成功！")
            else:
                # 創建新任務
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
                st.success("任務新增成功！")
            
            st.rerun()
    
    if is_editing:
        if st.button("取消編輯"):
            st.session_state['is_editing'] = False
            st.session_state['editing_task'] = None
            st.rerun()

def task_overview(tasks):
    """顯示任務概覽和視覺化圖表。"""
    st.header("任務概覽")
    
    if not tasks:
        st.info("沒有可分析的任務。請先新增一些任務。")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 狀態分佈
        status_counts = {}
        for task in tasks:
            if task.status in status_counts:
                status_counts[task.status] += 1
            else:
                status_counts[task.status] = 1
                
        df_status = pd.DataFrame({
            '狀態': list(status_counts.keys()),
            '數量': list(status_counts.values())
        })
        
        fig_status = px.pie(
            df_status, 
            values='數量', 
            names='狀態', 
            title='任務狀態分佈',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # 優先級分佈
        priority_counts = {}
        for task in tasks:
            if task.priority in priority_counts:
                priority_counts[task.priority] += 1
            else:
                priority_counts[task.priority] = 1
                
        df_priority = pd.DataFrame({
            '優先級': list(priority_counts.keys()),
            '數量': list(priority_counts.values())
        })
        
        fig_priority = px.pie(
            df_priority, 
            values='數量', 
            names='優先級', 
            title='任務優先級分佈',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # 計算總體進度
    progress = sheets_utils.calculate_task_progress(tasks)
    st.subheader("總體進度")
    st.progress(progress / 100)
    st.text(f"{progress:.1f}% 的任務已完成")
    
    # 任務時間線
    tasks_with_dates = [task for task in tasks if task.start_date and task.end_date]
    if tasks_with_dates:
        st.subheader("任務時間線")
        
        df_timeline = pd.DataFrame([
            {
                '任務': task.sub_task,
                '開始': task.start_date,
                '結束': task.end_date,
                '狀態': task.status,
                '優先級': task.priority
            }
            for task in tasks_with_dates
        ])
        
        fig_timeline = px.timeline(
            df_timeline,
            x_start='開始',
            x_end='結束',
            y='任務',
            color='狀態',
            hover_data=['優先級'],
            title="任務時間線"
        )
        fig_timeline.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_timeline, use_container_width=True)

if __name__ == "__main__":
    main()
