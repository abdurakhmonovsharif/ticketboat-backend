"""
Abstract interface for Persona Client implementations.

This defines the generic contract that all persona client implementations must follow,
enabling consistency across different automator systems (TicketSuite, Taciyon, etc.).
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class PersonaClientInterface(ABC):
    """
    Abstract interface for persona management clients.
    
    This is a generic interface that doesn't depend on any specific
    implementation's data structures. All methods use Dict[str, Any]
    to remain agnostic of the underlying system.
    
    Implementations:
    - TicketSuitePersonaClient (uses TicketSuite-specific DTOs internally)
    - TaciyonPersonaClient (future implementation)
    - Other automator clients...
    """
    
    @abstractmethod
    async def create_persona(self, persona_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new persona.
        
        Args:
            persona_payload: Dictionary containing persona data
            
        Returns:
            Dictionary with creation result
        """
        pass
    
    @abstractmethod
    async def get_persona(
        self, 
        persona_id: Optional[str] = None, 
        email: Optional[str] = None,
        page_number: int = 0,
        page_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get persona(s) from the system.
        
        Args:
            persona_id: Optional persona ID to fetch specific persona
            email: Optional email to search by
            page_number: Page number for pagination
            page_size: Number of results per page
            
        Returns:
            List of persona dictionaries
        """
        pass
    
    @abstractmethod
    async def update_persona(
        self, 
        persona_id: str, 
        persona_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing persona.
        
        Args:
            persona_id: ID of the persona to update
            persona_payload: Dictionary with updated persona data
            
        Returns:
            Dictionary with update result
        """
        pass
    
    @abstractmethod
    async def delete_persona(self, persona_id: str) -> Dict[str, Any]:
        """
        Delete a persona.
        
        Args:
            persona_id: ID of the persona to delete
            
        Returns:
            Dictionary with deletion result
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Clean up resources and close connections.
        """
        pass

