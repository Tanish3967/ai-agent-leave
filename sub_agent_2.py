import autogen

class AcademicQueryAgent:
    def __init__(self):
        self.agent = autogen.AssistantAgent(
            name="AcademicQueryAgent",
            system_message="Answers academic queries using Groq AI.",
            llm_config={"model": "deepseek-r1-distill-llama-70b"}
        )

    def get_response(self, query):
        return self.agent.generate_reply(f"Query: {query}")
