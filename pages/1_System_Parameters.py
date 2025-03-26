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
    
    # 顯示當前參數並支持拖曳排序
    st.subheader("當前選項")
    
    # 創建一個帶有排序功能的數據框
    df_params = pd.DataFrame({
        "選項值": param_list,
        "操作": ["刪除"] * len(param_list)
    })
    
    # 使用 st.data_editor 允許拖放排序
    edited_df = st.data_editor(
        df_params,
        use_container_width=True,
        column_config={
            "選項值": st.column_config.TextColumn(
                "選項值",
                width="large",
                help="拖動行進行重新排序"
            ),
            "操作": st.column_config.SelectboxColumn(
                "操作",
                options=["刪除"],
                width="small",
                required=True
            )
        },
        disabled=["選項值"],
        hide_index=True,
        num_rows="fixed",
        key=f"data_editor_{param_key}",
        on_change=None
    )
    
    # 檢查是否有選項被標記為刪除
    for i, row in edited_df.iterrows():
        if row["操作"] == "刪除":
            value = row["選項值"]
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("確認刪除", key=f"confirm_delete_{param_key}_{i}"):
                    param_list.remove(value)
                    st.success(f"已移除: {value}")
                    st.rerun()
    
    # 檢查排序是否更改
    if list(edited_df["選項值"]) != param_list:
        if st.button("套用新排序", key=f"apply_sort_{param_key}"):
            # 更新參數順序
            param_list.clear()
            param_list.extend(edited_df["選項值"].tolist())
            st.success("已更新順序！")
            st.rerun()
    
    # 添加新參數
    st.subheader("添加新選項")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_param = st.text_input("新值", key=f"new_param_{param_key}")
    
    with col2:
        if st.button("添加", key=f"add_btn_{param_key}"):
            if not new_param:
                st.error("請輸入值！")
            elif new_param in param_list:
                st.error(f"'{new_param}' 已存在！")
            else:
                param_list.append(new_param)
                st.success(f"已添加: {new_param}")
                st.rerun()
    
    # 添加顯示拖曳指南
    st.info("提示：您可以通過拖動行來重新排序項目，排序後點擊「套用新排序」按鈕保存更改。")
    
    # 支持批量添加（可選）
    with st.expander("批量添加"):
        with st.form(key=f"bulk_add_{param_key}_form"):
            bulk_params = st.text_area(
                "每行輸入一個選項", 
                height=100, 
                help="每行一個選項，批量添加多個選項值"
            )
            
            submitted = st.form_submit_button("批量添加")
            
            if submitted and bulk_params:
                # 分割文本並過濾空行
                new_params = [p.strip() for p in bulk_params.split("\n") if p.strip()]
                added = 0
                skipped = 0
                
                for p in new_params:
                    if p and p not in param_list:
                        param_list.append(p)
                        added += 1
                    else:
                        skipped += 1
                
                if added > 0:
                    st.success(f"已添加 {added} 個新選項")
                if skipped > 0:
                    st.info(f"跳過了 {skipped} 個已存在或空白的選項")
                
                if added > 0:
                    st.rerun()
    
    return param_list

if __name__ == "__main__":
    main()
