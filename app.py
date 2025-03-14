import os
if not os.path.exists("leave_management.db"):
    import schema

import streamlit as st
import sqlite3
from ai_agent import MainAgent

agent = MainAgent()

# Function to authenticate users
def authenticate(username, password):
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

st.title("Leave Management System")

# Login Section
if "logged_in" not in st.session_state:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user[0]
            st.session_state["role"] = user[1]
            st.success(f"Logged in as {user[1]}")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

# Leave Request Section
if st.session_state.get("logged_in"):
    if st.session_state["role"] == "student":
        st.subheader("Request Leave")
        mentor_id = st.selectbox("Select Mentor", [1, 2])  # Example mentor IDs
        days = st.number_input("Number of Leave Days", min_value=1, max_value=10, step=1)

        if st.button("Submit Leave Request"):
            result = agent.process_leave_request(st.session_state["user_id"], mentor_id, days)
            if result == "pending":
                st.warning("Leave request pending mentor approval.")
            else:
                st.success("Leave approved. Download your certificate below.")
                st.download_button("Download Certificate", open(result, "rb"), file_name=result)

st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())
