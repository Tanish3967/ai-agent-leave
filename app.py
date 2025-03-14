import os
import sqlite3
import streamlit as st
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from ai_agent import MainAgent

# Initialize Main Agent
agent = MainAgent()

# Initialize Database
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
st.title("Leave Management System")

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
    
    # Student Dashboard
    if role == "student":
        st.subheader("Request Leave")
        days = st.number_input("Number of Leave Days", min_value=1, max_value=10)
        reason = st.text_area("Reason for Leave")
        if st.button("Submit Leave Request"):
            try:
                result = agent.process_leave_request(st.session_state["user_id"], days)
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
        recipient_email = st.text_input("Recipient Email (Optional)")
        
        if st.button("Generate Certificate"):
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))
            
            # Generate certificate content based on type
            c.setFont("Helvetica-Bold", 30)
            c.drawCentredString(420, 400, f"{cert_type} Certificate")
            c.setFont("Helvetica", 20)
            c.drawCentredString(420, 350, f"Awarded to: {st.session_state['user_id']}")
            
            # Add IST timestamp to certificate
            ist_timezone = datetime.now().astimezone().strftime("%B %d, %Y at %I:%M %p IST")
            c.setFont("Helvetica", 12)
            c.drawCentredString(420, 200, f"Date: {ist_timezone}")
            
            c.save()
            
            pdf_buffer.seek(0)
            
            # Download button for the certificate PDF
            file_name = f"{cert_type.lower().replace(' ', '_')}_certificate.pdf"
            st.download_button(
                label="📄 Download Certificate",
                data=pdf_buffer,
                file_name=file_name,
                mime="application/pdf"
            )
            
            # Optionally send the certificate via email (if recipient_email is provided)
            if recipient_email:
                # Simulate email sending (replace with actual email-sending logic)
                st.success(f"Certificate sent to {recipient_email}!")

    # Mentor Dashboard
    elif role == "mentor":
        mentor_id = st.session_state["user_id"]
        
        # Fetch pending leave requests for this mentor
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
                    if st.button(f"Approve {request_id}"):
                        agent.leave_agent.update_leave_status(request_id, "approved")
                        st.experimental_rerun()
                with col2:
                    if st.button(f"Reject {request_id}"):
                        agent.leave_agent.update_leave_status(request_id, "rejected")
                        st.experimental_rerun()

    # Admin Dashboard
    elif role == "admin":
        academic_file = st.file_uploader("Upload Academic Calendar (PDF)", type=["pdf"])
