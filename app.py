import os
import streamlit as st
import sqlite3
import pdfkit
from ai_agent import MainAgent

# ✅ PDFKit Workaround for Streamlit Cloud
WKHTMLTOPDF_PATH = "/usr/bin/wkhtmltopdf"
if not os.path.exists(WKHTMLTOPDF_PATH):
    st.warning("wkhtmltopdf not found! PDFs may not generate correctly.")
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# ✅ Ensure database schema is created
if not os.path.exists("leave_management.db"):
    import schema  

agent = MainAgent()

# ✅ Authenticate Users
def authenticate(username, password):
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# ✅ Fetch Mentors from DB
def get_mentors():
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE role='mentor'")
    mentors = cursor.fetchall()
    conn.close()
    return mentors

# ✅ Logout Function
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# ✅ Streamlit UI
st.title("Leave Management System")

# ✅ Login Section
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

# ✅ Leave Request Section
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

    elif role == "mentor":
        st.subheader("Mentor Dashboard")
        mentor_id = st.session_state["user_id"]

        # ✅ Fetch pending leave requests for this mentor
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, student_id, days FROM leave_requests WHERE mentor_id=? AND status='pending'", (mentor_id,))
        requests = cursor.fetchall()
        conn.close()

        if not requests:
            st.info("No pending leave requests.")
        else:
            for req in requests:
                request_id, student_id, days = req
                st.write(f"Student ID: {student_id}, Leave Days: {days}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Approve {request_id}"):
                        agent.update_leave_status(request_id, "approved")
                        st.experimental_rerun()
                with col2:
                    if st.button(f"Reject {request_id}"):
                        agent.update_leave_status(request_id, "rejected")
                        st.experimental_rerun()

    elif role == "admin":
        st.subheader("Admin Panel")

        # ✅ Upload Academic Calendar
        st.write("Upload Academic Calendar (PDF)")
        academic_file = st.file_uploader("Upload PDF", type=["pdf"])
        if academic_file:
            with open("academic_calendar.pdf", "wb") as f:
                f.write(academic_file.getbuffer())
            st.success("Academic Calendar Uploaded!")

        # ✅ Upload Backlog Student List
        st.write("Upload Backlog Student List (CSV)")
        backlog_file = st.file_uploader("Upload CSV", type=["csv"])
        if backlog_file:
            import pandas as pd
            df = pd.read_csv(backlog_file)
            conn = sqlite3.connect("leave_management.db")
            df.to_sql("backlogs", conn, if_exists="replace", index=False)
            conn.close()
            st.success("Backlog Student Data Updated!")

# ✅ Logout Button
st.sidebar.button("Logout", on_click=logout)
