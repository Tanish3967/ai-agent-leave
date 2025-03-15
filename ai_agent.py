import autogen
from sub_agent_1 import LeaveAgent
from sub_agent_2 import AcademicQueryAgent
from sub_agent_3 import CertificateAgent

# ✅ Define Multi-Agent System
class MainAgent:
    def __init__(self):
        # Convert existing agents into Autogen agents
        self.leave_agent = autogen.AssistantAgent(
            name="LeaveAgent",
            system_message="Handles leave requests and approvals based on student-mentor mapping.",
            llm_config={"model": "deepseek-r1-distill-llama-70b"}
        )

        self.academic_agent = autogen.AssistantAgent(
            name="AcademicQueryAgent",
            system_message="Answers academic queries using ExaTools.",
            llm_config={"model": "deepseek-r1-distill-llama-70b"}
        )

        self.certificate_agent = autogen.AssistantAgent(
            name="CertificateAgent",
            system_message="Generates certificates and provides downloadable PDFs.",
            llm_config={"model": "deepseek-r1-distill-llama-70b"}
        )

        # ✅ Define a User Proxy (to handle user interactions)
        self.user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            system_message="Routes requests to appropriate AI agents based on task type."
        )

        # ✅ Setup agent collaboration
        self.user_proxy.register_assistant(self.leave_agent)
        self.user_proxy.register_assistant(self.academic_agent)
        self.user_proxy.register_assistant(self.certificate_agent)

    # ✅ Process Leave Request
    def process_leave(self, student_id, days):
        response = self.user_proxy.initiate_chat(self.leave_agent, message=f"Student {student_id} requests {days} days leave.")
        return response

    # ✅ Handle Academic Queries
    def handle_query(self, query, student_id):
        response = self.user_proxy.initiate_chat(self.academic_agent, message=f"Query from student {student_id}: {query}")
        return response

    # ✅ Generate Certificates
    def generate_certificate(self, student_id, email=None):
        response = self.user_proxy.initiate_chat(self.certificate_agent, message=f"Generate a certificate for student {student_id}. Email: {email}")
        return response
