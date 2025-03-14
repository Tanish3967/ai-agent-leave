import sqlite3
import time
import random
import os
from fpdf import FPDF  # For generating PDF certificates

class LeaveApprovalAgent:
    def approve_leave(self, student_id, mentor_id, days):
        if days <= 5:
            return "approved"
        else:
            return "pending"

class CertificateAgent:
    def generate_certificate(self, student_name, leave_id):
        filename = f"leave_certificate_{leave_id}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, f"Leave Certificate for {student_name}", ln=True, align="C")
        pdf.output(filename)
        return filename

class MainAgent:
    def __init__(self):
        self.leave_agent = LeaveApprovalAgent()
        self.certificate_agent = CertificateAgent()

    def process_leave_request(self, student_id, mentor_id, days):
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()

        status = self.leave_agent.approve_leave(student_id, mentor_id, days)
        cursor.execute("INSERT INTO leave_requests (student_id, mentor_id, start_date, end_date, days, status) VALUES (?, ?, ?, ?, ?, ?)",
                       (student_id, mentor_id, "2025-03-15", "2025-03-20", days, status))
        leave_id = cursor.lastrowid
        conn.commit()
        conn.close()

        if status == "approved":
            student_name = f"Student_{student_id}"
            return self.certificate_agent.generate_certificate(student_name, leave_id)
        return "pending"

if __name__ == "__main__":
    agent = MainAgent()
    print("AI Agent is running...")
