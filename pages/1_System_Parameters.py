import streamlit as st
import pandas as pd
import sheets_utils

st.set_page_config(
    page_title="System Parameters - To-Do Management System",
    page_icon="⚙️",
    layout="wide"
)

def main():
    st.title("System Parameters")
    st.write("Manage system parameters such as status options, priority levels, and more.")
    
    # Load parameters
    parameters = sheets_utils.load_parameters()
    
    # Create tabs for different parameter types
    tab1, tab2, tab3, tab4 = st.tabs([
        "Status Options", 
        "Priority Options", 
        "Responsible Persons",
        "Main Task Categories"
    ])
    
    with tab1:
        parameters["status"] = manage_parameter_list(
            "Status Options", 
            parameters["status"],
            "status"
        )
    
    with tab2:
        parameters["priority"] = manage_parameter_list(
            "Priority Options", 
            parameters["priority"],
            "priority"
        )
    
    with tab3:
        parameters["responsible"] = manage_parameter_list(
            "Responsible Persons", 
            parameters["responsible"],
            "responsible"
        )
    
    with tab4:
        parameters["main_task"] = manage_parameter_list(
            "Main Task Categories", 
            parameters["main_task"],
            "main_task"
        )
    
    # Save parameters when changes are made
    sheets_utils.save_parameters(parameters)

def manage_parameter_list(title, param_list, param_key):
    """UI component to manage a list of parameter values."""
    st.header(title)
    
    # Display current parameters
    st.subheader("Current Options")
    for i, param in enumerate(param_list):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(param)
        with col2:
            if st.button("Delete", key=f"delete_{param_key}_{i}"):
                param_list.remove(param)
                st.success(f"Removed: {param}")
                st.rerun()
    
    # Add new parameter
    st.subheader("Add New Option")
    with st.form(key=f"add_{param_key}_form"):
        new_param = st.text_input("New Value")
        submit = st.form_submit_button("Add")
        
        if submit and new_param:
            if new_param in param_list:
                st.error(f"'{new_param}' already exists!")
            else:
                param_list.append(new_param)
                st.success(f"Added: {new_param}")
                st.rerun()
    
    # Reorder parameters
    st.subheader("Reorder Options")
    st.write("Drag and drop to change the order (coming soon)")
    
    return param_list

if __name__ == "__main__":
    main()
