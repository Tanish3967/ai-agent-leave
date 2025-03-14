from agno.agent import Agent

class AcademicQueryAgent:
    def __init__(self):
        self.agent = Agent(
            name="Academic Assistant",
            model="deepseek-r1-distill-llama-70b",
            description="Handles academic queries."
        )

    def answer_query(self, query):
        return self.agent.chat(query)
