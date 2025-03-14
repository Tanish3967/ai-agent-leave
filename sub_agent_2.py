from phi.agent import Agent
from phi.model.groq import Groq
from exa import ExaSearch

class AcademicQueryAgent:
    def __init__(self):
        self.agent = Agent(
            name="Academic Query AI",
            model=Groq(id="deepseek-r1-distill-llama-70b"),
            tools=[ExaSearch()],
            instructions=["Check if the student has a backlog before answering."],
            debug_mode=True
        )

    def answer_query(self, query, student_id):
        conn = sqlite3.connect("leave_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT has_backlog FROM backlog_records WHERE student_id=?", (student_id,))
        has_backlog = cursor.fetchone()

        if has_backlog and has_backlog[0] == 1:
            return "You have a backlog. Please clear it before proceeding."
        
        return self.agent.get_response(query)
