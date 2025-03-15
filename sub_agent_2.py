import autogen
from agno.tools.exa import ExaTools

EXA_API_KEY = "cf630edc-9843-4c86-8ac4-a55b830d9f34"
exa_tools_api = ExaTools(api_key=EXA_API_KEY)

class AcademicQueryAgent:
    def __init__(self):
        self.agent = autogen.AssistantAgent(
            name="AcademicQueryAgent",
            system_message="Answers academic queries using ExaTools.",
            llm_config={"model": "deepseek-r1-distill-llama-70b"}
        )

    def get_response(self, query):
        return self.agent.generate_reply(f"Query: {query}")
