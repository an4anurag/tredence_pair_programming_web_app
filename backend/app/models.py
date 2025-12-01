"""
Database models for the Pair Programming application.

This module defines SQLAlchemy ORM models for rooms and code snapshots.
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import uuid

class Room(Base):
    """
    Room model representing a collaborative coding session.
    
    Attributes:
        id: Unique room identifier (UUID)
        code: Current code content in the room
        language: Programming language (default: python)
        created_at: Timestamp when room was created
        updated_at: Timestamp when room was last updated
        snapshots: Relationship to code snapshots
    """
    __tablename__ = "rooms"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(Text, default="# Write your Python code here\n\n")
    language = Column(String, default="python")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to snapshots (for history tracking if needed)
    snapshots = relationship("CodeSnapshot", back_populates="room", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Room(id={self.id}, language={self.language})>"


class CodeSnapshot(Base):
    """
    Code snapshot model for tracking code history.
    
    This allows us to implement features like:
    - Undo/Redo
    - History viewing
    - Time-travel debugging
    
    Attributes:
        id: Unique snapshot identifier
        room_id: Foreign key to room
        code: Code content at this snapshot
        timestamp: When this snapshot was created
        user_identifier: Optional identifier for who made the change
        room: Relationship back to room
    """
    __tablename__ = "code_snapshots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False)
    code = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_identifier = Column(String, nullable=True)  # Optional: track which user made change
    
    # Relationship to room
    room = relationship("Room", back_populates="snapshots")
    
    def __repr__(self):
        return f"<CodeSnapshot(id={self.id}, room_id={self.room_id}, timestamp={self.timestamp})>"