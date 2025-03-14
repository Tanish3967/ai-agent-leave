import sqlite3
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

class CertificateAgent:
    def __init__(self):
        self.db_path = "leave_management.db"

    def generate_certificate(self, student_id, cert_type, email=None):
        """
        Generate a certificate for a student and optionally send it via email.

        Args:
            student_id (int): ID of the student.
            cert_type (str): Type of certificate (e.g., "Achievement", "NOC", "Bonafide", "Leaving").
            email (str, optional): Email address to send the certificate to. Defaults to None.

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
        from datetime import datetime
        ist_time = datetime.now().astimezone().strftime("%B %d, %Y at %I:%M %p IST")
        c.setFont("Helvetica", 12)
        c.drawCentredString(420, 200, f"Date: {ist_time}")
        
        # Save the PDF to a buffer
        c.save()
        pdf_buffer.seek(0)

        # Save the certificate path in the database
        certificate_path = f"certificates/student_{student_id}_{cert_type.lower()}.pdf"
        
        # Ensure the certificates directory exists
        import os
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

        # Optionally send the certificate via email
        if email:
            self.send_email(email, certificate_path)

        return certificate_path

    def send_email(self, recipient_email, attachment_path):
        """
        Send an email with the generated certificate as an attachment.

        Args:
            recipient_email (str): The recipient's email address.
            attachment_path (str): Path to the PDF file to attach.

        Returns:
            None
        """
        
        # Load SMTP configuration from Streamlit secrets
        smtp_server = st.secrets["email"]["smtp_server"]
        smtp_port = st.secrets["email"]["port"]
        smtp_username = st.secrets["email"]["username"]
        smtp_password = st.secrets["email"]["password"]

        sender_email = smtp_username

        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = "Your Certificate"

        body = "Please find your requested certificate attached."
        
        msg.attach(MIMEText(body, "plain"))

        # Attach the PDF file
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={attachment_path.split('/')[-1]}",
            )
            msg.attach(part)

        # Send the email via SMTP server
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
                st.success(f"Certificate sent successfully to {recipient_email}!")
        
        except Exception as e:
            st.error(f"Failed to send email: {str(e)}")
