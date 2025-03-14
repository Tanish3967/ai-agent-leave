from sub_agent_1 import LeaveAgent
from sub_agent_2 import AcademicQueryAgent
from sub_agent_3 import CertificateAgent

class MainAgent:
    """Main agent that integrates sub-agents for leave management, academic queries, and certificate generation."""

    def __init__(self):
        # Initialize sub-agents
        self.leave_agent = LeaveAgent()
        self.academic_agent = AcademicQueryAgent()
        self.certificate_agent = CertificateAgent()

    def process_leave_request(self, student_id, mentor_id, days):
        """
        Process a leave request using the Leave Management AI agent.

        Args:
            student_id (int): ID of the student requesting leave.
            mentor_id (int): ID of the assigned mentor.
            days (int): Number of leave days requested.

        Returns:
            str: Status of the leave request ("approved" or "pending").
        """
        return self.leave_agent.process_leave(student_id, mentor_id, days)

    def handle_academic_query(self, student_id, query):
        """
        Handle academic queries using the Academic Query AI agent.

        Args:
            student_id (int): ID of the student asking the query.
            query (str): The academic query.

        Returns:
            str: Response to the academic query.
        """
        return self.academic_agent.handle_academic_query(student_id, query)

    def generate_certificate(self, student_id, email=None):
        """
        Generate a certificate using the Certificate Generation AI agent.

        Args:
            student_id (int): ID of the student for whom the certificate is generated.
            email (str, optional): Email address to send the certificate. Defaults to None.

        Returns:
            str: Path to the generated certificate PDF.
        """
        return self.certificate_agent.generate_certificate(student_id, email)
