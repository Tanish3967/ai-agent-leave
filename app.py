import os
import streamlit as st
import sqlite3
from ai_agent import MainAgent

# Ensure database schema is created
if not os.path.exists("leave_management.db"):
    import schema  

agent = MainAgent()

# Function to authenticate users
def authenticate(username, password):
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to fetch mentors from DB
def get_mentors():
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE role='mentor'")
    mentors = cursor.fetchall()
    conn.close()
    return mentors

# Streamlit UI
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
    role = st.session_state["role"]

    if role == "student":
        st.subheader("Request Leave")

        # Fetch mentor list dynamically
        mentors = get_mentors()
        if not mentors:
            st.warning("No mentors available. Contact admin.")
        else:
            mentor_options = {name: mid for mid, name in mentors}
            selected_mentor = st.selectbox("Select Mentor", list(mentor_options.keys()))
            mentor_id = mentor_options[selected_mentor]

            days = st.number_input("Number of Leave Days", min_value=1, max_value=10, step=1)

            if st.button("Submit Leave Request"):
                try:
                    result = agent.process_leave_request(st.session_state["user_id"], mentor_id, days)
                    if result == "pending":
                        st.warning("Leave request pending mentor approval.")
                    else:
                        st.success("Leave approved. Download your certificate below.")
                        st.download_button("Download Certificate", open(result, "rb"), file_name="leave_certificate.pdf")
                except Exception as e:
                    st.error(f"Error processing request: {str(e)}")

st.sidebar.button("Logout", on_click=st.session_state.clear)
