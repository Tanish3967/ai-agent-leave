from sub_agent_1 import LeaveAgent
from sub_agent_2 import AcademicQueryAgent
from sub_agent_3 import CertificateAgent

class MainAgent:
    def __init__(self):
        self.leave_agent = LeaveAgent()
        self.academic_agent = AcademicQueryAgent()
        self.certificate_agent = CertificateAgent()

    def process_leave(self, student_id, days):
        return self.leave_agent.process_leave(student_id, days)

    def handle_query(self, query, student_id):
        return self.academic_agent.answer_query(query, student_id)

    def generate_certificate(self, student_id, email=None):
        return self.certificate_agent.generate_certificate(student_id, email)
