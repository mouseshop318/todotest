import streamlit as st
import pandas as pd
import sheets_utils

st.set_page_config(
    page_title="系統參數 - 待辦事項管理系統",
    page_icon="⚙️",
    layout="wide"
)

def main():
    st.title("系統參數")
    st.write("管理系統參數，如狀態選項、優先級別等。")
    
    # 載入參數
    parameters = sheets_utils.load_parameters()
    
    # 創建不同參數類型的頁籤
    tab1, tab2, tab3, tab4 = st.tabs([
        "狀態選項", 
        "優先級選項", 
        "負責人",
        "任務大項類別"
    ])
    
    with tab1:
        parameters["status"] = manage_parameter_list(
            "狀態選項", 
            parameters["status"],
            "status"
        )
    
    with tab2:
        parameters["priority"] = manage_parameter_list(
            "優先級選項", 
            parameters["priority"],
            "priority"
        )
    
    with tab3:
        parameters["responsible"] = manage_parameter_list(
            "負責人", 
            parameters["responsible"],
            "responsible"
        )
    
    with tab4:
        parameters["main_task"] = manage_parameter_list(
            "任務大項類別", 
            parameters["main_task"],
            "main_task"
        )
    
    # 當有更改時儲存參數
    sheets_utils.save_parameters(parameters)

def manage_parameter_list(title, param_list, param_key):
    """管理參數值列表的UI元件。"""
    st.header(title)
    
    # 顯示當前參數
    st.subheader("當前選項")
    for i, param in enumerate(param_list):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(param)
        with col2:
            if st.button("刪除", key=f"delete_{param_key}_{i}"):
                param_list.remove(param)
                st.success(f"已移除: {param}")
                st.rerun()
    
    # 添加新參數
    st.subheader("添加新選項")
    with st.form(key=f"add_{param_key}_form"):
        new_param = st.text_input("新值")
        submit = st.form_submit_button("添加")
        
        if submit and new_param:
            if new_param in param_list:
                st.error(f"'{new_param}' 已存在！")
            else:
                param_list.append(new_param)
                st.success(f"已添加: {new_param}")
                st.rerun()
    
    # 重新排序參數
    st.subheader("重新排序選項")
    st.write("拖放以更改順序（即將推出）")
    
    return param_list

if __name__ == "__main__":
    main()
