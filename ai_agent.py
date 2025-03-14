import autogen
from sub_agent_1 import LeaveAgent
from sub_agent_2 import AcademicQueryAgent
from sub_agent_3 import CertificateAgent

class MainAgent:
    def __init__(self):
        self.leave_agent = LeaveAgent()
        self.academic_agent = AcademicQueryAgent()
        self.certificate_agent = CertificateAgent()

        # ✅ Ensure OpenAI is completely disabled
        self.user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            system_message="Routes requests to appropriate AI agents based on task type.",
            llm_config={"use_openai_api": False}  # ✅ Force disable OpenAI
        )

        # Register all agents with the User Proxy
        self.user_proxy.register_assistant(self.leave_agent.agent)
        self.user_proxy.register_assistant(self.academic_agent.agent)
        self.user_proxy.register_assistant(self.certificate_agent.agent)

    # ✅ Process Leave Request
    def process_leave(self, student_id, days):
        response = self.user_proxy.initiate_chat(
            self.leave_agent.agent,
            message=f"Student {student_id} requests {days} days leave."
        )
        return response

    # ✅ Handle Academic Queries (Now Uses Groq AI Directly)
    def handle_query(self, query, student_id):
        response = self.user_proxy.initiate_chat(
            self.academic_agent.agent,
            message=f"Query from student {student_id}: {query}"
        )
        return response

    # ✅ Generate Certificates
    def generate_certificate(self, student_id, email=None):
        response = self.user_proxy.initiate_chat(
            self.certificate_agent.agent,
            message=f"Generate a certificate for student {student_id}. Email: {email}"
        )
        return response
