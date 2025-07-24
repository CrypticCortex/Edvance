# FILE: app/agents/viva_agent/agent.py

from google.adk.agents import Agent
from app.core.config import settings
from app.agents.tools.viva_tools import (
    get_viva_topic,
    start_viva_session,
    process_student_response,
    end_viva_session
)

viva_agent = Agent(
    model=settings.gemini_model_name,
    name="viva_agent",
    description="An agent that conducts oral exams (vivas) with students in multiple languages.",
    instruction="""
    You are an AI Viva Voce examiner. Your role is to conduct a fair and engaging oral examination.
    
    **Instructions:**
    1.  Start by getting the viva topic using `get_viva_topic`.
    2.  Initiate the session with `start_viva_session`, choosing from English, Telugu, or Tamil.
    3.  Ask clear, relevant questions based on the topic.
    4.  Listen to the student's response (`process_student_response`) without interrupting.
    5.  Evaluate the response and ask follow-up questions to probe deeper understanding.
    6.  When the examination is complete, end the session with `end_viva_session`.
    """,
    tools=[
        get_viva_topic,
        start_viva_session,
        process_student_response,
        end_viva_session
    ],
)