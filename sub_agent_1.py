import autogen

class LeaveAgent:
    def __init__(self):
        self.agent = autogen.AssistantAgent(
            name="LeaveAgent",
            system_message="Handles leave requests and approvals based on student-mentor mapping.",
            llm_config={
                "config_list": [{"model": "deepseek-r1-distill-llama-70b", "api_key": "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"}],
                "use_openai_api": False  # ✅ Force Autogen to disable OpenAI
            }
        )

    def process_leave(self, student_id, days):
        return self.agent.generate_reply(f"Student {student_id} requests {days} days leave.")
