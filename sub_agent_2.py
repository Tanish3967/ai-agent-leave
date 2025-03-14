from textwrap import dedent
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.exa import ExaTools
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()

# Initialize ExaTools with API key from .streamlit/secrets.toml
EXA_API_KEY = os.getenv("EXA_API_KEY")
exa_tools_api = ExaTools(api_key=EXA_API_KEY)

# Function to check backlog status from the database
def check_backlog(student_id):
    """Check if a student has a backlog before answering queries."""
    conn = sqlite3.connect("leave_management.db")
    cursor = conn.cursor()
    cursor.execute("SELECT has_backlog FROM students WHERE id=?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Function to create the academic query agent with ExaTools integrated
def create_academic_query_agent(exa_tools_api):
    academic_agent = Agent(
        name="Academic Query Agent",
        tools=[exa_tools_api],  # ExaTools API for academic data retrieval
        model=Groq(id="deepseek-r1-distill-llama-70b"),
        description=dedent("""\
            You are an AI academic assistant that helps students with queries related to their university schedule, 
            exams, and backlogs. You also verify if students have any pending backlogs before answering queries.
        """),
        instructions=dedent("""\
            - Always check the student's backlog status before providing an answer.
            - If a backlog exists, inform the student and direct them to relevant backlog policies.
            - If the query is related to academic dates (like exams, holidays), check the provided academic calendar.
            - If the answer is not found in the database, use ExaTools to retrieve relevant information.
            - If ExaTools cannot find an answer, use the LLM (DeepSeek R1 Distill LLaMA-70B) to generate a response.
            - Keep responses accurate and concise.
        """),
        markdown=True,
        add_datetime_to_instructions=True,
        show_tool_calls=True,
    )
    return academic_agent

# Create the academic agent with ExaTools
academic_query_agent = create_academic_query_agent(exa_tools_api)

# Function to process queries while checking backlog
def handle_academic_query(student_id, query):
    """Process academic queries while verifying backlog status."""
    if check_backlog(student_id):
        return "You have a backlog. Please check with the admin for backlog exam details."

    # Use ExaTools to fetch academic-related information
    exa_response = academic_query_agent.chat(query)

    # If no answer is found, fallback to LLM
    if not exa_response:
        exa_response = academic_query_agent.chat(query, use_tools=False)

    return exa_response

# Example usage
if __name__ == "__main__":
    response = handle_academic_query(student_id=1, query="When is the next backlog exam?")
    print(response)
