"""
Room service for business logic related to room management.

This service handles:
- Room creation with unique IDs
- Room retrieval
- Code updates
- Room deletion
- Snapshot management (for future undo/redo features)
"""

from sqlalchemy.orm import Session
from app.models import Room, CodeSnapshot
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class RoomService:
    """Service class for managing collaborative coding rooms."""
    
    def __init__(self, db: Session):
        """
        Initialize room service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_room(self, language: str = "python") -> Room:
        """
        Create a new collaborative coding room.
        
        Args:
            language: Programming language for the room (default: python)
            
        Returns:
            Room: Created room instance
            
        Example:
            room_service = RoomService(db)
            room = room_service.create_room(language="javascript")
        """
        # Generate unique room ID
        room_id = str(uuid.uuid4())[:8]  # Use shorter ID for easier sharing
        
        # Create default code template based on language
        default_code = self._get_default_code(language)
        
        # Create room instance
        room = Room(
            id=room_id,
            code=default_code,
            language=language,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        
        logger.info(f"Created room {room_id} with language {language}")
        return room
    
    def get_room(self, room_id: str) -> Room | None:
        """
        Retrieve room by ID.
        
        Args:
            room_id: Unique room identifier
            
        Returns:
            Room: Room instance if found, None otherwise
            
        Example:
            room = room_service.get_room("abc123")
            if room:
                print(room.code)
        """
        room = self.db.query(Room).filter(Room.id == room_id).first()
        return room
    
    def update_room_code(self, room_id: str, code: str, user_identifier: str | None = None) -> Room | None:
        """
        Update code content in a room.
        
        Args:
            room_id: Unique room identifier
            code: New code content
            user_identifier: Optional user who made the change
            
        Returns:
            Room: Updated room instance if found, None otherwise
            
        Example:
            updated_room = room_service.update_room_code(
                "abc123",
                "print('Hello World')",
                user_identifier="user_456"
            )
        """
        room = self.get_room(room_id)
        
        if not room:
            logger.warning(f"Attempted to update non-existent room {room_id}")
            return None
        
        # Create snapshot before updating (for history/undo feature)
        self._create_snapshot(room_id, room.code, user_identifier)
        
        # Update room code
        room.code = code
        room.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(room)
        
        logger.debug(f"Updated code in room {room_id}")
        return room
    
    def delete_room(self, room_id: str) -> bool:
        """
        Delete a room and all associated data.
        
        Args:
            room_id: Unique room identifier
            
        Returns:
            bool: True if deleted, False if not found
            
        Example:
            success = room_service.delete_room("abc123")
        """
        room = self.get_room(room_id)
        
        if not room:
            return False
        
        self.db.delete(room)
        self.db.commit()
        
        logger.info(f"Deleted room {room_id}")
        return True
    
    def _create_snapshot(self, room_id: str, code: str, user_identifier: str | None = None):
        """
        Create a snapshot of the current code state.
        
        This enables features like:
        - Undo/Redo
        - History viewing
        - Time-travel debugging
        
        Args:
            room_id: Room identifier
            code: Code content to snapshot
            user_identifier: Optional user who made the change
        """
        snapshot = CodeSnapshot(
            room_id=room_id,
            code=code,
            timestamp=datetime.utcnow(),
            user_identifier=user_identifier
        )
        
        self.db.add(snapshot)
        self.db.commit()
        
        logger.debug(f"Created snapshot for room {room_id}")
    
    def _get_default_code(self, language: str) -> str:
        """
        Get default starter code based on programming language.
        
        Args:
            language: Programming language
            
        Returns:
            str: Default code template
        """
        templates = {
            "python": "# Write your Python code here\n\n",
            "javascript": "// Write your JavaScript code here\n\n",
            "typescript": "// Write your TypeScript code here\n\n",
            "java": "// Write your Java code here\n\npublic class Main {\n    public static void main(String[] args) {\n        \n    }\n}\n",
            "cpp": "// Write your C++ code here\n\n#include <iostream>\n\nint main() {\n    \n    return 0;\n}\n",
            "go": "// Write your Go code here\n\npackage main\n\nimport \"fmt\"\n\nfunc main() {\n    \n}\n"
        }
        
        return templates.get(language, f"// Write your {language} code here\n\n")