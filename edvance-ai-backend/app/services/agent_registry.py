# FILE: app/services/agent_registry.py

from typing import Dict, List, Optional, Any, Type
from abc import ABC, abstractmethod
import logging

from google.adk.agents import Agent
from app.core.config import settings

logger = logging.getLogger(__name__)

class BaseAgentHandler(ABC):
    """Abstract base class for agent handlers."""
    
    @property
    @abstractmethod
    def agent_name(self) -> str:
        """Return the unique name of this agent."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what this agent does."""
        pass
    
    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Return a list of capabilities this agent provides."""
        pass
    
    @abstractmethod
    def create_agent(self) -> Agent:
        """Create and return the agent instance."""
        pass
    
    @abstractmethod
    def matches_request(self, prompt: str, context: Dict[str, Any] = None) -> float:
        """
        Return a confidence score (0.0 to 1.0) for how well this agent matches the request.
        
        Args:
            prompt: The user's prompt
            context: Additional context about the user/session
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass

class AgentRegistry:
    """Registry for managing available agents and their capabilities."""
    
    def __init__(self):
        self._handlers: Dict[str, BaseAgentHandler] = {}
        self._agent_cache: Dict[str, Agent] = {}
    
    def register_handler(self, handler: BaseAgentHandler) -> None:
        """Register an agent handler."""
        self._handlers[handler.agent_name] = handler
        logger.info(f"Registered agent handler: {handler.agent_name}")
    
    def get_handler(self, agent_name: str) -> Optional[BaseAgentHandler]:
        """Get a specific agent handler by name."""
        return self._handlers.get(agent_name)
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get or create an agent by name."""
        if agent_name not in self._agent_cache:
            handler = self.get_handler(agent_name)
            if handler:
                self._agent_cache[agent_name] = handler.create_agent()
            else:
                return None
        return self._agent_cache.get(agent_name)
    
    def find_best_agent(self, prompt: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Find the best agent for handling the given prompt.
        
        Args:
            prompt: The user's prompt
            context: Additional context
            
        Returns:
            The name of the best matching agent, or None if no good match
        """
        if not self._handlers:
            return None
        
        best_score = 0.0
        best_agent = None
        
        for handler in self._handlers.values():
            score = handler.matches_request(prompt, context)
            logger.debug(f"Agent {handler.agent_name} scored {score} for prompt: {prompt[:50]}")
            
            if score > best_score:
                best_score = score
                best_agent = handler.agent_name
        
        # Only return an agent if the confidence is reasonably high
        if best_score >= 0.3:
            logger.info(f"Selected agent {best_agent} with confidence {best_score}")
            return best_agent
        
        logger.warning(f"No agent found with sufficient confidence for prompt: {prompt[:50]}")
        return None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents and their information."""
        return [
            {
                "name": handler.agent_name,
                "description": handler.description,
                "capabilities": handler.capabilities
            }
            for handler in self._handlers.values()
        ]

# Global registry instance
agent_registry = AgentRegistry()
