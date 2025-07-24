# FILE: app/services/viva_service.py

import logging
import uuid
import json
from typing import Dict, Any, List
from datetime import datetime
from app.models.viva_models import VivaSession, VivaStatus, VivaMessage
from app.core.vertex import get_vertex_model

logger = logging.getLogger(__name__)

class VivaService:
    """Service to manage viva sessions with live AI interaction."""

    def __init__(self):
        self.sessions: Dict[str, VivaSession] = {} # In-memory store for active sessions
        self.model = get_vertex_model("gemini-2.5-pro")

    def _get_language_name(self, lang_code: str) -> str:
        """Get the full language name from a code."""
        return {"english": "English", "telugu": "Telugu", "tamil": "Tamil"}.get(lang_code, "English")

    async def start_viva(self, student_id: str, learning_step_id: str, language: str) -> VivaSession:
        """Starts a new viva session."""
        session_id = str(uuid.uuid4())
        topic = "Introduction to Algebra" # This would be fetched from the learning step
        lang_name = self._get_language_name(language)

        initial_prompt = f"""You are a friendly and encouraging AI examiner. 
        Start a viva voce (oral exam) with the student.
        The topic is '{topic}'. The language of the viva is {lang_name}.
        Begin by warmly welcoming the student and asking if they are ready to start."""

        try:
            response = await self.model.generate_content_async(initial_prompt)
            welcome_message = response.text
        except Exception as e:
            logger.error(f"Failed to generate welcome message: {e}")
            welcome_message = f"Hello! Welcome to your viva on {topic}. Are you ready to begin?"

        session = VivaSession(
            session_id=session_id,
            student_id=student_id,
            learning_step_id=learning_step_id,
            topic=topic,
            language=language,
            status=VivaStatus.IN_PROGRESS,
            started_at=datetime.utcnow(),
            conversation_history=[VivaMessage(sender="agent", text=welcome_message)]
        )
        self.sessions[session_id] = session
        return session

    async def handle_student_speech(self, session_id: str, student_speech: str) -> Dict[str, Any]:
        """Handles student speech by calling the AI model and returns the agent's response."""
        session = self.sessions.get(session_id)
        if not session:
            return {"agent_response": "Session not found."}

        session.conversation_history.append(VivaMessage(sender="student", text=student_speech))

        # Construct the prompt for the AI
        history_str = "\n".join([f"{msg.sender}: {msg.text}" for msg in session.conversation_history])
        lang_name = self._get_language_name(session.language)
        
        prompt = f"""You are an AI examiner conducting a viva in {lang_name} on the topic '{session.topic}'.
        Below is the conversation history. The student has just spoken. 
        Your task is to evaluate their last response and ask the next logical question.
        Keep your questions clear and concise. Be encouraging.

        Conversation History:
        {history_str}

        Agent, what is your next response?
        """

        try:
            response = await self.model.generate_content_async(prompt)
            agent_response_text = response.text
        except Exception as e:
            logger.error(f"Failed to generate AI response for viva session {session_id}: {e}")
            agent_response_text = "I'm sorry, I encountered an issue. Could you please repeat your answer?"

        session.conversation_history.append(VivaMessage(sender="agent", text=agent_response_text))
        return {"agent_response": agent_response_text}

    async def end_viva(self, session_id: str) -> Dict[str, Any]:
        """Ends a viva session and generates a final score and feedback using AI."""
        session = self.sessions.get(session_id)
        if not session:
            return {"summary": "Session not found."}

        history_str = "\n".join([f"{msg.sender}: {msg.text}" for msg in session.conversation_history])
        lang_name = self._get_language_name(session.language)

        prompt = f"""You are an AI examiner. The viva in {lang_name} on the topic '{session.topic}' has concluded. 
        Based on the entire conversation history below, provide a final score out of 100 and brief, constructive feedback for the student.

        Conversation History:
        {history_str}

        Respond ONLY with a JSON object with two keys: "score" (an integer) and "feedback" (a string).
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            # Clean and parse the JSON response
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            result = json.loads(cleaned_response)
            score = result.get("score", 0)
            feedback = result.get("feedback", "No feedback generated.")
        except Exception as e:
            logger.error(f"Failed to parse final viva evaluation for session {session_id}: {e}")
            score = 0
            feedback = "Could not generate a final score. Please review the conversation manually."

        session.status = VivaStatus.COMPLETED
        session.ended_at = datetime.utcnow()
        session.score = score
        session.feedback = feedback
        
        # In a real app, you would save the completed session to Firestore here.
        # For this example, we remove it from the in-memory store.
        self.sessions.pop(session_id, None)

        return {
            "summary": "Viva completed!",
            "score": session.score,
            "feedback": session.feedback
        }

viva_service = VivaService()