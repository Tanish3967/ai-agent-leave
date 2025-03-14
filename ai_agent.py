import sqlite3
import os
import requests
from config import AGNO_API_KEY, GROQ_API_KEY, AGNO_API_URL, GROQ_API_URL
from certificate_generator import generate_certificate

class MainAgent:
    max_leave_days_per_student = 30  # Set max leave limit per student

    def __init__(self):
        self.session = requests.Session()  # Maintain session for API calls

    def call_ai_agent(self, student_id, days, use_agno=True):
        """Send leave request to Agno/Groq AI for auto-approval decision."""
        api_url = AGNO_API_URL if use_agno else GROQ_API_URL
        api_key = AGNO_API_KEY if use_agno else GROQ_API_KEY

        self.session.headers.update({"Authorization": f"Bearer {api_key}"})  # Set API key

        payload = {"student_id": student_id, "days": days}
        response = self.session.post(api_url, json=payload)

        if response.status_code == 200:
            return response.json().get("decision", "pending")  # AI returns 'approved' or 'pending'
        return "pending"

    def process_leave_request(self, student_id, mentor_id, days):
        """Handles leave requests using AI and mentor approvals."""
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()

        # Get total leave taken by student
        cursor.execute("SELECT SUM(days) FROM leave_requests WHERE student_id=?", (student_id,))
        total_leave_taken = cursor.fetchone()[0] or 0

        # Check if max leave limit is exceeded
        if total_leave_taken + days > self.max_leave_days_per_student:
            conn.close()
            return "Leave limit exceeded. Request denied."

        if days > 5:
            # Mentor approval required
            cursor.execute(
                "INSERT INTO leave_requests (student_id, mentor_id, days, status) VALUES (?, ?, ?, 'pending')",
                (student_id, mentor_id, days),
            )
            conn.commit()
            conn.close()
            return "pending"
        else:
            # AI makes the approval decision (use Agno by default)
            decision = self.call_ai_agent(student_id, days, use_agno=True)

            if decision == "approved":
                cursor.execute(
                    "INSERT INTO leave_requests (student_id, mentor_id, days, status) VALUES (?, ?, ?, 'approved')",
                    (student_id, mentor_id, days),
                )
                conn.commit()

                # Generate leave approval certificate
                certificate_path = generate_certificate(student_id, days)
                conn.close()
                return certificate_path  # Return certificate for download
            else:
                # If AI doesn't approve, send to mentor
                cursor.execute(
                    "INSERT INTO leave_requests (student_id, mentor_id, days, status) VALUES (?, ?, ?, 'pending')",
                    (student_id, mentor_id, days),
                )
                conn.commit()
                conn.close()
                return "pending"

    def approve_leave(self, request_id):
        """Mentor approves a leave request."""
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()

        # Update leave request status to approved
        cursor.execute("UPDATE leave_requests SET status='approved' WHERE id=?", (request_id,))
        conn.commit()

        # Fetch student ID and days for certificate
        cursor.execute("SELECT student_id, days FROM leave_requests WHERE id=?", (request_id,))
        student_id, days = cursor.fetchone()

        # Generate leave approval certificate
        certificate_path = generate_certificate(student_id, days)

        conn.close()
        return certificate_path

    def deny_leave(self, request_id):
        """Mentor denies a leave request."""
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()

        # Update leave request status to denied
        cursor.execute("UPDATE leave_requests SET status='denied' WHERE id=?", (request_id,))
        conn.commit()
        conn.close()
        return "Leave request denied."
