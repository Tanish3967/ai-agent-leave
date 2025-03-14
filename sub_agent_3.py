import sqlite3
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from datetime import datetime
import os

class CertificateAgent:
    def __init__(self):
        self.db_path = "leave_management.db"

    def generate_certificate(self, student_id, cert_type):
        """
        Generate a certificate for a student.

        Args:
            student_id (int): ID of the student.
            cert_type (str): Type of certificate (e.g., "Achievement", "NOC", "Bonafide", "Leaving").

        Returns:
            str: Path to the generated certificate PDF.
        """
        # Fetch student details from the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE id=?", (student_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"No student found with ID {student_id}")

        student_name = result[0]

        # Generate the certificate using ReportLab
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))

        # Add certificate content
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(420, 400, f"{cert_type} Certificate")
        c.setFont("Helvetica", 20)
        c.drawCentredString(420, 350, f"Awarded to: {student_name}")
        
        # Add IST timestamp to the certificate
        ist_time = datetime.now().astimezone().strftime("%B %d, %Y at %I:%M %p IST")
        c.setFont("Helvetica", 12)
        c.drawCentredString(420, 200, f"Date: {ist_time}")
        
        # Save the PDF to a buffer
        c.save()
        pdf_buffer.seek(0)

        # Save the certificate path in the database
        certificate_path = f"certificates/student_{student_id}_{cert_type.lower()}.pdf"
        
        # Ensure the certificates directory exists
        os.makedirs("certificates", exist_ok=True)
        
        with open(certificate_path, "wb") as f:
            f.write(pdf_buffer.getvalue())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO certificates (student_id, certificate_path) VALUES (?, ?)",
            (student_id, certificate_path)
        )
        conn.commit()
        conn.close()

        return certificate_path
