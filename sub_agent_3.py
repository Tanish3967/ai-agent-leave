import autogen
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class CertificateAgent:
    def __init__(self):
        self.agent = autogen.AssistantAgent(
            name="CertificateAgent",
            system_message="Generates certificates and provides downloadable PDFs.",
            llm_config={
                "config_list": [{"model": "deepseek-r1-distill-llama-70b", "api_key": "YOUR_GROQ_API_KEY"}],
                "use_openai_api": False  # ✅ Disable OpenAI
            }
        )

    def generate_certificate(self, student_id, email=None):
        pdf_path = f"generated_pdfs/certificate_{student_id}.pdf"
        os.makedirs("generated_pdfs", exist_ok=True)

        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, "Academic Certificate")
        c.drawString(100, 730, f"Student ID: {student_id}")
        c.save()

        return f"Certificate generated at {pdf_path}"
