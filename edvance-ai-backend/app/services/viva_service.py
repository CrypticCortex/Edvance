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
        
        # Get the actual learning step data
        learning_step = await self._get_learning_step_data(learning_step_id)
        
        if learning_step:
            topic = learning_step.get("topic", "General Review Topic")
            step_title = learning_step.get("title", topic)
            description = learning_step.get("description", "")
            difficulty = learning_step.get("difficulty_level", "medium")
            learning_objective = learning_step.get("learning_objective", "understand")
            content_text = learning_step.get("content_text", "")
        else:
            topic = "General Review Topic"
            step_title = topic
            description = ""
            difficulty = "medium"
            learning_objective = "understand"
            content_text = ""
        
        lang_name = self._get_language_name(language)

        # Create a more detailed prompt using learning step information
        initial_prompt = f"""You are a friendly and encouraging AI examiner conducting a viva voce (oral exam).

LEARNING STEP DETAILS:
- Title: {step_title}
- Topic: {topic}
- Description: {description}
- Difficulty Level: {difficulty}
- Learning Objective: {learning_objective}
- Content Focus: {content_text}

VIVA INSTRUCTIONS:
- Language: {lang_name}
- Assess the student's understanding of the specific learning step content
- Tailor questions to the {difficulty} difficulty level
- Focus on the {learning_objective} learning objective
- Be encouraging and supportive throughout

Begin by warmly welcoming the student, briefly explaining what this viva will cover based on their learning step, and asking if they are ready to start."""

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

        # Get learning step data for context
        learning_step = await self._get_learning_step_data(session.learning_step_id)
        
        # Construct the prompt for the AI with learning step context
        history_str = "\n".join([f"{msg.sender}: {msg.text}" for msg in session.conversation_history])
        lang_name = self._get_language_name(session.language)
        
        if learning_step:
            step_context = f"""
LEARNING STEP CONTEXT:
- Title: {learning_step.get('title', 'Unknown')}
- Topic: {learning_step.get('topic', session.topic)}
- Description: {learning_step.get('description', '')}
- Difficulty Level: {learning_step.get('difficulty_level', 'medium')}
- Learning Objective: {learning_step.get('learning_objective', 'understand')}
- Content Focus: {learning_step.get('content_text', '')}
"""
        else:
            step_context = f"Topic: {session.topic}"
        
        prompt = f"""You are an AI examiner conducting a viva in {lang_name}.

{step_context}

INSTRUCTIONS:
- Evaluate the student's last response in the context of the learning step
- Ask follow-up questions that assess their understanding of the specific learning objectives
- Tailor question difficulty to match the learning step's difficulty level
- Be encouraging and provide gentle guidance if needed
- Focus on the core concepts from the learning step content

Conversation History:
{history_str}

Based on the student's response and the learning step context, what is your next question or comment?
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

        # Get learning step data for context-aware evaluation
        learning_step = await self._get_learning_step_data(session.learning_step_id)
        
        history_str = "\n".join([f"{msg.sender}: {msg.text}" for msg in session.conversation_history])
        lang_name = self._get_language_name(session.language)

        if learning_step:
            step_context = f"""
LEARNING STEP EVALUATION CONTEXT:
- Title: {learning_step.get('title', 'Unknown')}
- Topic: {learning_step.get('topic', session.topic)}
- Description: {learning_step.get('description', '')}
- Difficulty Level: {learning_step.get('difficulty_level', 'medium')}
- Learning Objective: {learning_step.get('learning_objective', 'understand')}
- Content Focus: {learning_step.get('content_text', '')}

EVALUATION CRITERIA:
- Assess understanding specific to this learning step's objectives
- Consider the {learning_step.get('difficulty_level', 'medium')} difficulty level when scoring
- Focus on whether the student achieved the {learning_step.get('learning_objective', 'understand')} learning objective
- Evaluate comprehension of the specific content covered in this step
"""
        else:
            step_context = f"Topic: {session.topic}"

        prompt = f"""You are an AI examiner. The viva in {lang_name} has concluded.

{step_context}

Based on the entire conversation history below and the learning step context, provide a final score out of 100 and brief, constructive feedback for the student.

Conversation History:
{history_str}

Respond ONLY with a JSON object with two keys: "score" (an integer) and "feedback" (a string).
The feedback should be specific to the learning step objectives and provide actionable guidance for improvement.
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

    async def _get_learning_step_data(self, learning_step_id: str) -> Dict[str, Any]:
        """
        Get learning step data from the learning path service.
        
        Args:
            learning_step_id: The ID of the learning step.
            
        Returns:
            Dictionary containing learning step data or None if not found.
        """
        try:
            from app.core.firebase import db
            from app.models.learning_models import LearningStep, DifficultyLevel, LearningObjectiveType
            
            logger.info(f"Fetching learning step data for: {learning_step_id}")
            
            # Search through learning paths to find the step
            learning_paths_ref = db.collection("learning_paths")
            docs = learning_paths_ref.get()
            
            for doc in docs:
                path_data = doc.to_dict()
                if "steps" in path_data:
                    for step_data in path_data["steps"]:
                        if step_data.get("step_id") == learning_step_id:
                            logger.info(f"Found learning step: {step_data.get('title', 'Unknown')}")
                            return {
                                "step_id": step_data.get("step_id"),
                                "title": step_data.get("title", "Learning Step"),
                                "description": step_data.get("description", ""),
                                "subject": step_data.get("subject", "General"),
                                "topic": step_data.get("topic", "General"),
                                "subtopic": step_data.get("subtopic"),
                                "difficulty_level": step_data.get("difficulty_level", "medium"),
                                "learning_objective": step_data.get("learning_objective", "understand"),
                                "content_text": step_data.get("content_text", ""),
                                "addresses_gaps": step_data.get("addresses_gaps", [])
                            }
            
            logger.warning(f"Learning step {learning_step_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching learning step data for {learning_step_id}: {str(e)}")
            return None

viva_service = VivaService()