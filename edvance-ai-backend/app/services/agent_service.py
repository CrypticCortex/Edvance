# FILE: app/services/agent_service.py

from __future__ import annotations
from typing import AsyncGenerator, Dict, Any
import logging

from google.adk.runners import InMemoryRunner
from google.genai import types

from app.agents.orchestrator_agent.agent import root_agent as orchestrator_agent
from app.agents.tools.profile_tools import current_user_uid
from app.agents.tools.onboarding_tools import current_user_uid as onboarding_current_user_uid
from app.agents.tools.onboarding_tools import current_user_uid as onboarding_current_user_uid
from app.core.language import SupportedLanguage, validate_language, create_language_prompt_prefix

logger = logging.getLogger(__name__)

class AgentService:
    """Service for handling comprehensive teacher agent interactions."""
    
    def __init__(self):
        self.app_name = "comprehensive_teacher_agent"
    
    async def invoke_agent(self, user_uid: str, prompt: str, language: str = "english") -> str:
        """
        Invoke the comprehensive teacher agent with a user's prompt.
        This agent handles both onboarding for new users and profile management for existing users.
        
        Args:
            user_uid: The authenticated user's UID
            prompt: The user's prompt text
            language: Language for AI generation (english, tamil, telugu)
            
        Returns:
            The agent's response text
            
        Raises:
            Exception: If agent invocation fails
        """
        try:
            # Validate and normalize language
            validated_language = validate_language(language)
            
            # Set the user UID in context for all tools to use
            current_user_uid.set(user_uid)
            onboarding_current_user_uid.set(user_uid)
            
            # Create an InMemoryRunner with the orchestrator_agent
            runner = InMemoryRunner(orchestrator_agent, app_name=self.app_name)
            
            # Create or get session for the user
            session_id = f"session_{user_uid}"
            
            # Try to get existing session, create if it doesn't exist
            session = await runner.session_service.get_session(
                app_name=self.app_name,
                user_id=user_uid,
                session_id=session_id
            )
            
            if session is None:
                # Session doesn't exist, create it
                session = await runner.session_service.create_session(
                    app_name=self.app_name,
                    user_id=user_uid,
                    session_id=session_id
                )
            
            # Create language-aware prompt
            language_prefix = create_language_prompt_prefix(validated_language, "Teacher assistance and guidance")
            enhanced_prompt = f"{language_prefix}\n\nUser Request: {prompt}"
            
            # Create a Content object with the enhanced prompt
            user_message = types.Content(
                parts=[types.Part(text=enhanced_prompt)],
                role="user"
            )
            
            # Use the new API to run the agent
            response_generator = runner.run_async(
                user_id=user_uid,
                session_id=session_id,
                new_message=user_message
            )
            
            # Process the response
            final_response = await self._process_agent_response(response_generator)
            
            logger.info(f"Agent response processed successfully for user {user_uid}")
            return final_response
            
        except Exception as e:
            logger.error(f"Failed to invoke agent for user {user_uid}: {str(e)}")
            raise
    
    async def _process_agent_response(self, response_generator: AsyncGenerator) -> str:
        """
        Process the agent response generator and extract text.
        
        Args:
            response_generator: The async generator from agent execution
            
        Returns:
            The final response text
        """
        final_response = ""
        
        async for event in response_generator:
            # Debug logging (remove in production)
            logger.debug(f"Event type: {type(event)}")
            logger.debug(f"Event has content: {hasattr(event, 'content')}")
            
            if hasattr(event, 'content') and event.content:
                logger.debug(f"Event.content type: {type(event.content)}")
                
                # Check if content has parts
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            logger.debug(f"Found text in part: {part.text}")
                            final_response += part.text
                # Check if content has text directly
                elif hasattr(event.content, 'text') and event.content.text:
                    logger.debug(f"Found text in content: {event.content.text}")
                    final_response += event.content.text
            
            # Check if event has text directly
            elif hasattr(event, 'text') and event.text:
                logger.debug(f"Found text in event: {event.text}")
                final_response += event.text
        
        # If we still don't have a response, return a success message
        if not final_response.strip():
            final_response = "Task completed successfully."
        
        return final_response

# Create a singleton instance
agent_service = AgentService()
