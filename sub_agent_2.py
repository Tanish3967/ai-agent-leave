import autogen

class AcademicQueryAgent:
    def __init__(self):
        self.agent = autogen.AssistantAgent(
            name="AcademicQueryAgent",
            system_message="Answers academic queries using Groq AI.",
            llm_config={
                "config_list": [{"model": "deepseek-r1-distill-llama-70b", "api_key": "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"}],
                "use_openai_api": False  # ✅ Disable OpenAI
            }
        )

    def get_response(self, query):
        return self.agent.generate_reply(f"Query: {query}")
