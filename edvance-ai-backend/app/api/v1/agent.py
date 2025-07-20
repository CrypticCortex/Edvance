# FILE: app/api/v1/agent.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import logging

from app.models.requests import AgentPrompt, AgentResponse
from app.core.auth import get_current_user
from app.services.agent_service import agent_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/invoke", response_model=AgentResponse, tags=["Agent Interaction"])
async def invoke_agent(
    request: AgentPrompt,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> AgentResponse:
    """
    Invoke the comprehensive teacher agent with a user's prompt.
    This intelligent agent handles:
    - New user onboarding and profile creation
    - Existing user subject management and updates  
    - General teaching assistance and guidance
    
    The agent automatically detects if you're a new or existing user and provides
    appropriate assistance.
    
    Args:
        request: The agent prompt request
        current_user: The authenticated user information
        
    Returns:
        The agent's response with appropriate guidance
        
    Raises:
        HTTPException: If agent invocation fails
    """
    user_uid = current_user["uid"]
    
    try:
        logger.info(f"Invoking agent for user {user_uid} with prompt: {request.prompt[:50]}...")
        
        response_text = await agent_service.invoke_agent(
            user_uid=user_uid,
            prompt=request.prompt
        )
        
        return AgentResponse(
            response=response_text,
            session_id=f"session_{user_uid}"
        )
        
    except Exception as e:
        logger.error(f"Agent invocation failed for user {user_uid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while invoking the agent: {str(e)}"
        )

@router.get("/health", response_model=Dict[str, str], tags=["Agent Interaction"])
async def agent_health() -> Dict[str, str]:
    """
    Check the health status of the agent service.
    
    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "message": "Agent service is operational"
    }
