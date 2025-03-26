import streamlit as st
import pandas as pd
from datetime import datetime
import sheets_utils

st.set_page_config(
    page_title="已移除任務 - 待辦事項管理系統",
    page_icon="🗑️",
    layout="wide"
)

def main():
    st.title("已移除任務")
    st.write("查看和管理已刪除的任務。您可以恢復任務或永久刪除它們。")
    
    # 載入已刪除的任務
    deleted_tasks = sheets_utils.get_deleted_tasks()
    
    if not deleted_tasks:
        st.info("沒有找到已刪除的任務。")
        return
    
    # 轉換為DataFrame以便顯示
    df = sheets_utils.tasks_to_dataframe(deleted_tasks)
    
    # 按刪除時間（status_update_time）排序，最近的優先
    df['Deletion Time'] = pd.to_datetime([task.status_update_time for task in deleted_tasks])
    df = df.sort_values('Deletion Time', ascending=False)
    
    # 顯示帶有恢復和永久刪除選項的任務
    st.subheader(f"已刪除任務 ({len(deleted_tasks)})")
    
    # 顯示選項
    view_option = st.radio(
        "選擇視圖",
        options=["表格視圖", "詳細視圖"],
        horizontal=True
    )
    
    if view_option == "表格視圖":
        display_table_view(deleted_tasks, df)
    else:
        display_detailed_view(deleted_tasks)
    
    # 清理選項
    st.subheader("清理選項")
    if st.button("永久刪除所有任務"):
        if st.warning("此操作無法撤銷。您確定嗎？"):
            if st.button("是的，永久刪除所有"):
                for task in deleted_tasks:
                    sheets_utils.permanently_delete_task(task.id)
                st.success("所有已刪除的任務已被永久移除。")
                st.rerun()

def display_table_view(deleted_tasks, df):
    """以表格格式顯示已刪除的任務和操作按鈕。"""
    # 格式化日期以便顯示
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
    
    # 表格視圖的顯示列
    display_columns = [
        'Sub Task', 'Main Task', 'Priority', 'Status', 
        'Start Date', 'End Date', 'Responsible', 'Deletion Time'
    ]
    
    # 顯示表格
    st.dataframe(display_df[display_columns], use_container_width=True)
    
    # 選定任務的操作
    st.subheader("任務操作")
    
    # 選擇要操作的任務
    task_options = {f"{task.sub_task} ({task.main_task})": task.id for task in deleted_tasks}
    selected_task_ids = st.multiselect(
        "選擇要恢復或永久刪除的任務",
        options=list(task_options.keys())
    )
    
    # 將選定的任務名稱轉換為ID
    selected_ids = [task_options[name] for name in selected_task_ids]
    
    if selected_ids:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("恢復選定項目", key="restore_selected"):
                for task_id in selected_ids:
                    sheets_utils.restore_task(task_id)
                st.success(f"已恢復 {len(selected_ids)} 個任務。")
                st.rerun()
        
        with col2:
            if st.button("永久刪除選定項目", key="delete_selected"):
                for task_id in selected_ids:
                    sheets_utils.permanently_delete_task(task_id)
                st.success(f"已永久刪除 {len(selected_ids)} 個任務。")
                st.rerun()

def display_detailed_view(deleted_tasks):
    """使用卡片顯示已刪除任務的詳細視圖。"""
    # 按刪除時間排序任務（最近的優先）
    sorted_tasks = sorted(
        deleted_tasks,
        key=lambda x: x.status_update_time if x.status_update_time else datetime.min,
        reverse=True
    )
    
    # 為卡片佈局創建列
    col1, col2 = st.columns(2)
    
    # 在列之間分配任務
    for i, task in enumerate(sorted_tasks):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            with st.container(border=True):
                st.subheader(task.sub_task)
                st.caption(f"**主要任務:** {task.main_task}")
                
                col_a, col_b, col_c = st.columns([2, 2, 1])
                
                with col_a:
                    st.write(f"**優先級:** {task.priority}")
                    st.write(f"**狀態:** {task.status}")
                
                with col_b:
                    st.write(f"**負責人:** {task.responsible}")
                    if task.start_date and task.end_date:
                        st.write(f"**時間線:** {task.start_date.strftime('%Y-%m-%d')} 至 {task.end_date.strftime('%Y-%m-%d')}")
                
                with col_c:
                    # 顯示刪除時間
                    if task.status_update_time:
                        st.write(f"**已刪除:** {task.status_update_time.strftime('%Y-%m-%d')}")
                
                if task.notes:
                    st.write(f"**備註:** {task.notes}")
                
                # 操作按鈕
                col_action1, col_action2 = st.columns(2)
                
                with col_action1:
                    if st.button("恢復", key=f"restore_{task.id}"):
                        sheets_utils.restore_task(task.id)
                        st.success(f"任務 '{task.sub_task}' 已恢復！")
                        st.rerun()
                
                with col_action2:
                    if st.button("永久刪除", key=f"perm_delete_{task.id}"):
                        sheets_utils.permanently_delete_task(task.id)
                        st.success(f"任務 '{task.sub_task}' 已永久刪除！")
                        st.rerun()

if __name__ == "__main__":
    main()
