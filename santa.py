"""Core secret santa assignment logic."""

import random
from typing import List, Dict, Tuple


class SantaAssigner:
    """Handles secret santa assignments with restrictions."""
    
    def __init__(self, people: List[Dict[str, str]]):
        """
        Initialize with a list of people.
        
        Args:
            people: List of dicts with 'id', 'name', 'surname' keys
        """
        self.people = people
        self.assignments: Dict[str, str] = {}  # {giver_id: recipient_id}
    
    def can_assign(self, giver_id: str, recipient_id: str) -> bool:
        """Check if assignment is valid."""
        if giver_id == recipient_id:
            return False
        
        giver = next(p for p in self.people if p['id'] == giver_id)
        recipient = next(p for p in self.people if p['id'] == recipient_id)
        
        # Same surname = spouse, not allowed
        if giver['surname'] == recipient['surname']:
            return False
        
        return True
    
    def assign(self) -> bool:
        """
        Attempt to create valid assignments for all people.
        Uses backtracking to find a valid solution.
        
        Returns:
            True if successful, False if no valid assignment exists
        """
        self.assignments = {}
        people_ids = [p['id'] for p in self.people]
        
        return self._backtrack(people_ids, 0)
    
    def _backtrack(self, people_ids: List[str], index: int) -> bool:
        """Backtracking helper for assignment."""
        if index == len(people_ids):
            return True
        
        giver_id = people_ids[index]
        available = [p for p in people_ids if p not in self.assignments.values()]
        
        random.shuffle(available)
        
        for recipient_id in available:
            if self.can_assign(giver_id, recipient_id):
                self.assignments[giver_id] = recipient_id
                
                if self._backtrack(people_ids, index + 1):
                    return True
                
                del self.assignments[giver_id]
        
        return False
    
    def get_recipient(self, giver_id: str) -> str:
        """Get who a person should buy a gift for."""
        return self.assignments.get(giver_id)
    
    def get_assignments(self) -> Dict[str, str]:
        """Get all assignments (for admin view)."""
        return self.assignments.copy()


def get_person_name(people: List[Dict[str, str]], person_id: str) -> str:
    """Get person's name by ID."""
    person = next((p for p in people if p['id'] == person_id), None)
    return person['name'] if person else None
