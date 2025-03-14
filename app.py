import os
import sqlite3
import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from ai_agent import MainAgent

# Initialize Main Agent
agent = MainAgent()

# Ensure database schema is created
if not os.path.exists("leave_management.db"):
    from schema import create_database
    create_database()

# Authenticate Users
def authenticate(username, password):
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Logout Functionality
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# Streamlit UI
st.title("AI-Powered Leave Management System")

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

if st.session_state.get("logged_in"):
    role = st.session_state["role"]
    
    # Student Dashboard: Leave Application and Certificate Generation
    if role == "student":
        # Leave Application Section
        st.subheader("Request Leave")
        
        # Fetch assigned mentor dynamically from the database
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mentor_id FROM mentor_students WHERE student_id=?
        """, (st.session_state["user_id"],))
        mentor_result = cursor.fetchone()
        conn.close()

        if not mentor_result:
            st.warning("No assigned mentor found. Contact admin.")
        else:
            mentor_id = mentor_result[0]
            days = st.number_input("Number of Leave Days", min_value=1, max_value=10)
            reason = st.text_area("Reason for Leave")
            
            if st.button("Submit Leave Request"):
                try:
                    result = agent.process_leave_request(st.session_state["user_id"], mentor_id, days)
                    if result == "pending":
                        st.warning("Leave request pending mentor approval.")
                    else:
                        st.success("Leave approved.")
                except Exception as e:
                    st.error(f"Error processing request: {str(e)}")

        # Certificate Generation Section
        cert_type = st.selectbox(
            "Select Certificate Type:", 
            ["Achievement Certificate", "NOC", "Bonafide", "Leaving"]
        )
        
        if st.button("Generate Certificate"):
            try:
                cert_path = agent.certificate_agent.generate_certificate(
                    student_id=st.session_state["user_id"],
                    cert_type=cert_type,
                )
                
                with open(cert_path, "rb") as f:
                    st.download_button(
                        label="Download Certificate",
                        data=f,
                        file_name=cert_path.split("/")[-1],
                        mime="application/pdf",
                    )
            
            except Exception as e:
                st.error(f"Error generating certificate: {str(e)}")

    # Mentor Dashboard: Approve/Reject Leave Requests
    elif role == "mentor":
        mentor_id = st.session_state["user_id"]
        
        # Fetch pending leave requests for this mentor dynamically from the database
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, student_id, days FROM leave_requests WHERE mentor_id=? AND status='pending'
        """, (mentor_id,))
        requests = cursor.fetchall()
        conn.close()

        if not requests:
            st.info("No pending leave requests.")
        else:
            for req in requests:
                request_id, student_id, days = req
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Approve Request {request_id}"):
                        agent.leave_agent.update_leave_status(request_id, "approved")
                        st.experimental_rerun()
                with col2:
                    if st.button(f"Reject Request {request_id}"):
                        agent.leave_agent.update_leave_status(request_id, "rejected")
                        st.experimental_rerun()

    # Admin Dashboard: Upload Academic Calendar and Backlog Data
    elif role == "admin":
        # Upload Academic Calendar (PDF)
        academic_file = st.file_uploader("Upload Academic Calendar (PDF)", type=["pdf"])
        
        if academic_file:
            with open("academic_calendar.pdf", "wb") as f:
                f.write(academic_file.getbuffer())
            conn = sqlite3.connect("leave_management.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO academic_calendar (file_path) VALUES (?)
            """, ("academic_calendar.pdf",))
            conn.commit()
            conn.close()
            st.success("Academic Calendar Uploaded!")

        # Upload Backlog Student List (CSV)
        backlog_file = st.file_uploader("Upload Backlog Student List (CSV)", type=["csv"])
        
        if backlog_file:
            import pandas as pd
            df = pd.read_csv(backlog_file)
            
            conn = sqlite3.connect("leave_management.db")
            df.to_sql("backlog_records", conn, if_exists="replace", index=False)
            conn.close()
            
            st.success("Backlog Student Data Updated!")

# Logout Button in Sidebar
if st.sidebar.button("Logout"):
    logout()
