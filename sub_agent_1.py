import autogen

class LeaveAgent:
    def __init__(self):
        self.agent = autogen.AssistantAgent(
            name="LeaveAgent",
            system_message="Handles leave requests and approvals based on student-mentor mapping.",
            llm_config={
                "config_list": [{"model": "deepseek-r1-distill-llama-70b", "api_key": "YOUR_GROQ_API_KEY"}]
            }
        )

    def process_leave(self, student_id, days):
        return self.agent.generate_reply(f"Student {student_id} requests {days} days leave.")
