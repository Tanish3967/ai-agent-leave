import pdfkit
import sqlite3
import smtplib

class CertificateAgent:
    def generate_certificate(self, student_id, email=None):
        certificate_path = f"certificates/student_{student_id}.pdf"
        
        # Create Certificate
        pdfkit.from_string(f"Certificate of Completion for Student {student_id}", certificate_path)
        
        # Store in DB
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO certificates (student_id, certificate_path) VALUES (?, ?)", 
                       (student_id, certificate_path))
        conn.commit()
        conn.close()

        # Email Certificate
        if email:
            self.send_email(email, certificate_path)

        return certificate_path

    def send_email(self, email, attachment_path):
        smtp = smtplib.SMTP("smtp.example.com", 587)
        smtp.sendmail("admin@example.com", email, f"Your certificate is attached.")
        smtp.quit()
