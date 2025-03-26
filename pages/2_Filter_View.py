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
    """進階篩選視圖，提供多種篩選選項。"""
    st.header("進階篩選")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 文字搜索
        search_term = st.text_input("搜索任務子項", key="adv_search_subtask")
        
        # 任務大項篩選
        selected_main_task = st.multiselect(
            "任務大項", 
            options=parameters["main_task"],
            key="adv_filter_main_task"
        )
        
        # 優先級篩選
        selected_priority = st.multiselect(
            "優先級", 
            options=parameters["priority"],
            key="adv_filter_priority"
        )
    
    with col2:
        # 狀態篩選
        selected_status = st.multiselect(
            "狀態", 
            options=parameters["status"],
            key="adv_filter_status"
        )
        
        # 負責人篩選
        selected_responsible = st.multiselect(
            "負責人", 
            options=parameters["responsible"],
            key="adv_filter_responsible"
        )
    
    with col3:
        # 開始日期範圍
        use_start_date_filter = st.checkbox("按開始日期篩選", key="use_start_date_filter")
        if use_start_date_filter:
            start_date_range = st.date_input(
                "開始日期範圍",
                value=(date.today() - timedelta(days=30), date.today() + timedelta(days=30)),
                key="start_date_filter"
            )
        
        # 結束日期範圍
        use_end_date_filter = st.checkbox("按結束日期篩選", key="use_end_date_filter")
        if use_end_date_filter:
            end_date_range = st.date_input(
                "結束日期範圍",
                value=(date.today() - timedelta(days=30), date.today() + timedelta(days=30)),
                key="end_date_filter"
            )
    
    # 應用篩選條件
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
    
    # 顯示結果
    st.subheader("篩選結果")
    if not filtered_tasks:
        st.info("沒有符合所選篩選條件的任務。")
        return
    
    # 顯示選項
    view_option = st.radio(
        "選擇視圖",
        options=["表格視圖", "卡片視圖"],
        horizontal=True
    )
    
    if view_option == "表格視圖":
        display_table_view(filtered_tasks)
    else:
        display_card_view(filtered_tasks)

def display_table_view(tasks):
    """以表格格式顯示任務。"""
    df = sheets_utils.tasks_to_dataframe(tasks)
    
    # 重新排序列以便更好地顯示
    display_columns = [
        'Sub Task', 'Main Task', 'Priority', 'Status', 
        'Start Date', 'End Date', 'Responsible', 'Notes'
    ]
    
    # 格式化日期以便顯示
    if 'Start Date' in df.columns:
        df['Start Date'] = df['Start Date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '')
    
    if 'End Date' in df.columns:
        df['End Date'] = df['End Date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else '')
    
    # 顯示表格
    st.dataframe(df[display_columns], use_container_width=True)
    
    # 導出選項
    if st.button("導出為CSV"):
        # 使用 BOM 標記確保 Excel 能正確識別 UTF-8 編碼
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="下載CSV",
            data=csv,
            file_name="任務導出.csv",
            mime="text/csv",
            help="下載包含所有任務資料的 CSV 檔案，支援中文字符"
        )

def display_card_view(tasks):
    """以卡片格式顯示任務。"""
    # 創建卡片布局的列
    col1, col2 = st.columns(2)
    
    # 在列之間分配任務
    for i, task in enumerate(tasks):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            with st.container(border=True):
                st.subheader(task.sub_task)
                st.caption(f"**任務大項:** {task.main_task}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**優先級:** {task.priority}")
                    st.write(f"**狀態:** {task.status}")
                
                with col_b:
                    st.write(f"**負責人:** {task.responsible}")
                    if task.start_date and task.end_date:
                        st.write(f"**時間線:** {task.start_date.strftime('%Y-%m-%d')} 至 {task.end_date.strftime('%Y-%m-%d')}")
                
                if task.notes:
                    st.write(f"**備註:** {task.notes}")

def calendar_view(tasks):
    """以日曆形式顯示任務。"""
    st.header("日曆視圖")
    
    # 篩選有日期的任務
    tasks_with_dates = [task for task in tasks if task.start_date and task.end_date]
    
    if not tasks_with_dates:
        st.info("沒有可用的帶有已定義開始和結束日期的任務。")
        return
    
    # 月份視圖選擇
    today = date.today()
    selected_month = st.selectbox(
        "選擇月份",
        options=[
            (today.replace(month=((today.month - i - 1) % 12) + 1, year=today.year - ((today.month - i - 1) // 12)))
            for i in range(-3, 9)  # 顯示之前3個月和之後8個月
        ],
        format_func=lambda x: x.strftime("%Y年%m月"),
        index=3  # 默認為當前月份
    )
    
    # 獲取所選月份的第一天和最後一天
    first_day = selected_month.replace(day=1)
    if selected_month.month == 12:
        last_day = selected_month.replace(year=selected_month.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = selected_month.replace(month=selected_month.month + 1, day=1) - timedelta(days=1)
    
    # 篩選所選月份的任務
    month_tasks = []
    for task in tasks_with_dates:
        # 檢查任務是否在所選月份內或與之重疊
        if (task.start_date <= last_day and 
            (task.end_date >= first_day if task.end_date else True)):
            month_tasks.append(task)
    
    if not month_tasks:
        st.info(f"{selected_month.strftime('%Y年%m月')} 沒有找到任務。")
        return
    
    # 為所選月份創建時間線視圖
    df_timeline = pd.DataFrame([
        {
            '任務': task.sub_task,
            '開始': max(task.start_date, first_day),
            '結束': min(task.end_date, last_day) if task.end_date else last_day,
            '狀態': task.status,
            '優先級': task.priority,
            '任務大項': task.main_task
        }
        for task in month_tasks
    ])
    
    fig_timeline = px.timeline(
        df_timeline,
        x_start='開始',
        x_end='結束',
        y='任務',
        color='狀態',
        hover_data=['優先級', '任務大項'],
        title=f"任務日曆 - {selected_month.strftime('%Y年%m月')}"
    )
    fig_timeline.update_yaxes(autorange="reversed")
    
    # 如果今天在所選月份內，添加一條垂直線表示今天
    if first_day <= today <= last_day:
        # 轉換為時間戳，確保是數值格式而非字符串
        today_timestamp = pd.Timestamp(today).timestamp() * 1000  # 轉換為毫秒時間戳
        fig_timeline.add_vline(
            x=today_timestamp,
            line_width=2,
            line_dash="dash",
            line_color="green",
            annotation_text="今天"
        )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # 每日視圖
    st.subheader("每日任務視圖")
    
    # 為整個月創建日期範圍
    all_days = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]
    selected_day = st.select_slider(
        "選擇日期",
        options=all_days,
        value=today if first_day <= today <= last_day else first_day,
        format_func=lambda x: x.strftime("%m月%d日, %a")
    )
    
    # 篩選所選日期的任務
    day_tasks = [
        task for task in tasks_with_dates
        if task.start_date <= selected_day <= task.end_date
    ]
    
    if not day_tasks:
        st.info(f"{selected_day.strftime('%m月%d日, %A')} 沒有任務。")
        return
    
    # 顯示所選日期的任務
    st.write(f"{selected_day.strftime('%Y年%m月%d日, %A')} 的任務：")
    
    for task in day_tasks:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(task.sub_task)
                st.caption(f"**{task.main_task}** | {task.status}")
                st.write(f"**優先級:** {task.priority} | **負責人:** {task.responsible}")
                
                # 計算剩餘天數或過期天數
                if task.end_date:
                    if task.end_date >= today:
                        days_left = (task.end_date - today).days
                        st.write(f"**剩餘:** {days_left} 天")
                    else:
                        days_overdue = (today - task.end_date).days
                        st.write(f"**已過期:** {days_overdue} 天")
            
            with col2:
                # 根據狀態顯示彩色指示器
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
    """顯示預定義的篩選選項和結果。"""
    st.header("預設篩選器")
    
    filter_option = st.selectbox(
        "選擇篩選器",
        options=[
            "最近完成的任務（過去一週）",
            "即將到期的任務（未來三週）",
            "本年度任務",
            "自定義日期範圍"
        ]
    )
    
    filtered_tasks = []
    
    if filter_option == "最近完成的任務（過去一週）":
        filtered_tasks = sheets_utils.get_recently_completed_tasks(7)
        time_description = "在過去7天內完成"
    
    elif filter_option == "即將到期的任務（未來三週）":
        filtered_tasks = sheets_utils.get_upcoming_tasks(21)
        time_description = "在未來3週內到期"
    
    elif filter_option == "本年度任務":
        filtered_tasks = sheets_utils.get_current_year_tasks()
        current_year = date.today().year
        time_description = f"{current_year}年的"
    
    elif filter_option == "自定義日期範圍":
        # 自定義日期範圍選擇器
        date_range = st.date_input(
            "選擇日期範圍",
            value=(date.today() - timedelta(days=30), date.today() + timedelta(days=30)),
            key="custom_date_range"
        )
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_tasks = sheets_utils.get_custom_period_tasks(start_date, end_date)
            time_description = f"在 {start_date.strftime('%Y-%m-%d')} 和 {end_date.strftime('%Y-%m-%d')} 之間"
        else:
            st.error("請同時選擇開始和結束日期。")
            return
    
    # 顯示結果
    if not filtered_tasks:
        st.info(f"沒有{time_description}的任務。")
        return
    
    st.subheader(f"{time_description}的任務 ({len(filtered_tasks)} 個任務)")
    
    # 顯示選項
    view_option = st.radio(
        "選擇視圖",
        options=["表格視圖", "摘要視圖"],
        horizontal=True
    )
    
    if view_option == "表格視圖":
        display_table_view(filtered_tasks)
    else:
        # 帶分組的摘要視圖
        df = sheets_utils.tasks_to_dataframe(filtered_tasks)
        
        # 按選定字段分組
        group_by = st.multiselect(
            "分組依據",
            options=["Main Task", "Status", "Priority", "Responsible"],
            default=["Status"]
        )
        
        if not group_by:
            st.warning("請至少選擇一個分組字段。")
            display_table_view(filtered_tasks)
        else:
            # 創建帶計數的摘要數據框
            summary = df.groupby(group_by).size().reset_index(name='Count')
            
            # 顯示摘要表
            st.dataframe(summary, use_container_width=True)
            
            # 根據分組創建可視化
            if len(group_by) == 1:
                # 單維度分組 - 使用餅圖
                fig = px.pie(
                    summary, 
                    values='Count', 
                    names=group_by[0], 
                    title=f'按 {group_by[0]} 分類的任務'
                )
                st.plotly_chart(fig, use_container_width=True)
            elif len(group_by) == 2:
                # 雙維度 - 使用分組條形圖
                fig = px.bar(
                    summary, 
                    x=group_by[0], 
                    y='Count', 
                    color=group_by[1],
                    title=f'按 {group_by[0]} 和 {group_by[1]} 分類的任務'
                )
                st.plotly_chart(fig, use_container_width=True)

def task_statistics_view(tasks, parameters):
    """顯示任務統計和視覺化圖表。"""
    st.header("任務統計")
    
    if not tasks:
        st.info("沒有可分析的任務。")
        return
    
    # 基本統計
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == "Completed")
    completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    
    # 創建摘要框
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("總任務數", total_tasks)
    
    with col2:
        st.metric("已完成任務", completed_tasks)
    
    with col3:
        st.metric("完成率", f"{completion_rate:.1f}%")
    
    # 按狀態分類的任務
    status_counts = {}
    for task in tasks:
        if task.status in status_counts:
            status_counts[task.status] += 1
        else:
            status_counts[task.status] = 1
    
    # 按優先級分類的任務
    priority_counts = {}
    for task in tasks:
        if task.priority in priority_counts:
            priority_counts[task.priority] += 1
        else:
            priority_counts[task.priority] = 1
    
    # 按負責人分類的任務
    responsible_counts = {}
    for task in tasks:
        if task.responsible in responsible_counts:
            responsible_counts[task.responsible] += 1
        else:
            responsible_counts[task.responsible] = 1
    
    # 顯示視覺化圖表
    col1, col2 = st.columns(2)
    
    with col1:
        # 狀態分佈
        df_status = pd.DataFrame({
            '狀態': list(status_counts.keys()),
            '數量': list(status_counts.values())
        })
        
        fig_status = px.bar(
            df_status,
            x='狀態',
            y='數量',
            title='按狀態分類的任務',
            color='狀態'
        )
        st.plotly_chart(fig_status, use_container_width=True)
        
        # 負責人分佈
        df_responsible = pd.DataFrame({
            '負責人': list(responsible_counts.keys()),
            '數量': list(responsible_counts.values())
        })
        
        fig_responsible = px.bar(
            df_responsible,
            x='負責人',
            y='數量',
            title='按負責人分類的任務',
            color='負責人'
        )
        st.plotly_chart(fig_responsible, use_container_width=True)
    
    with col2:
        # 優先級分佈
        df_priority = pd.DataFrame({
            '優先級': list(priority_counts.keys()),
            '數量': list(priority_counts.values())
        })
        
        fig_priority = px.bar(
            df_priority,
            x='優先級',
            y='數量',
            title='按優先級分類的任務',
            color='優先級'
        )
        st.plotly_chart(fig_priority, use_container_width=True)
        
        # 隨時間的完成率（如果有足夠的帶日期的任務）
        tasks_with_updates = [task for task in tasks if task.status_update_time]
        
        if tasks_with_updates:
            # 按週分組任務
            df_tasks = pd.DataFrame([
                {
                    '日期': task.status_update_time,
                    '狀態': task.status
                }
                for task in tasks_with_updates
            ])
            
            # 添加週列
            df_tasks['週'] = df_tasks['日期'].dt.strftime('%Y-%U')
            df_tasks['已完成'] = df_tasks['狀態'] == 'Completed'
            
            # 按週分組並計算已完成與總數
            weekly_stats = df_tasks.groupby('週').agg(
                已完成=('已完成', 'sum'),
                總數=('已完成', 'count')
            ).reset_index()
            
            # 計算完成率
            weekly_stats['完成率'] = (weekly_stats['已完成'] / weekly_stats['總數']) * 100
            
            # 創建折線圖
            fig_completion = px.line(
                weekly_stats,
                x='週',
                y='完成率',
                title='每週任務完成率',
                markers=True
            )
            fig_completion.update_layout(yaxis_title='完成率 (%)')
            st.plotly_chart(fig_completion, use_container_width=True)

if __name__ == "__main__":
    main()
