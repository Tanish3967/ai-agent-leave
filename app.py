import os
import streamlit as st
import sqlite3
from ai_agent import MainAgent

# ✅ Ensure database schema is created
if not os.path.exists("leave_management.db"):
    import schema

# Initialize AI Multi-Agent System
agent = MainAgent()

# ✅ Authenticate Users
def authenticate(username, password):
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# ✅ Streamlit App UI
def main():
    st.title("AI-Powered Academic System")

    # ✅ User Authentication
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.success(f"Welcome {username}!")
            role = user[1]  # Get role (admin, mentor, student)

            if role == "student":
                student_dashboard(user[0])
            elif role == "mentor":
                mentor_dashboard(user[0])
            elif role == "admin":
                admin_dashboard()
        else:
            st.error("Invalid credentials!")

# ✅ Student Dashboard
def student_dashboard(student_id):
    st.subheader("Student Dashboard")

    # ✅ Academic Chatbot
    st.subheader("Ask Your Academic Questions")
    query = st.text_area("Enter your question:")

    if st.button("Submit Query"):
        response = agent.handle_query(query, student_id)
        st.success(response)

    # ✅ Leave Request
    st.subheader("Request Leave")
    leave_days = st.number_input("Number of Leave Days", min_value=1, max_value=30, step=1)

    if st.button("Submit Leave Request"):
        status = agent.process_leave(student_id, leave_days)
        st.success(f"Leave Status: {status}")

# ✅ Mentor Dashboard
def mentor_dashboard(mentor_id):
    st.subheader("Mentor Dashboard")
    st.write("Mentors can approve or reject leave requests here.")

    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, student_id, days, status FROM leave_requests WHERE mentor_id=? AND status='pending'", (mentor_id,))
    leave_requests = cursor.fetchall()
    conn.close()

    for request in leave_requests:
        st.write(f"Student ID: {request[1]}, Leave Days: {request[2]}, Status: {request[3]}")
        if st.button(f"Approve {request[0]}"):
            update_leave_status(request[0], "approved")
        if st.button(f"Reject {request[0]}"):
            update_leave_status(request[0], "rejected")

# ✅ Admin Dashboard
def admin_dashboard():
    st.subheader("Admin Dashboard")
    st.write("Admin can upload academic data here.")

    file = st.file_uploader("Upload CSV (ID, Name, Backlog)", type=["csv"])
    if file:
        df = pd.read_csv(file)
        conn = sqlite3.connect("leave_management.db")
        df.to_sql("students", conn, if_exists="replace", index=False)
        conn.commit()
        conn.close()
        st.success("Data uploaded successfully!")

# ✅ Update Leave Status
def update_leave_status(request_id, status):
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE leave_requests SET status=? WHERE id=?", (status, request_id))
    conn.commit()
    conn.close()
    st.success(f"Leave request {request_id} {status} successfully!")

if __name__ == "__main__":
    main()
