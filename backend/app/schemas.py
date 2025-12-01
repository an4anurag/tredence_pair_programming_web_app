"""
Pydantic schemas for request/response validation.

These schemas define the structure of data exchanged between
client and server, providing automatic validation and serialization.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RoomCreate(BaseModel):
    """Schema for creating a new room (no input needed)"""
    language: Optional[str] = Field(default="python", description="Programming language")

class RoomResponse(BaseModel):
    """
    Schema for room creation response.
    
    Attributes:
        roomId: Unique identifier for the created room
        code: Initial code content
        language: Programming language
        created_at: Timestamp when room was created
    """
    roomId: str = Field(..., description="Unique room identifier")
    code: str = Field(..., description="Initial code content")
    language: str = Field(..., description="Programming language")
    created_at: datetime = Field(..., description="Room creation timestamp")
    
    class Config:
        from_attributes = True


class AutocompleteRequest(BaseModel):
    """
    Schema for autocomplete request.
    
    Attributes:
        code: Current code content
        cursorPosition: Current cursor position in the code
        language: Programming language for context
    """
    code: str = Field(..., description="Current code content")
    cursorPosition: int = Field(..., ge=0, description="Cursor position in code")
    language: str = Field(default="python", description="Programming language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "def hello():\n    print(",
                "cursorPosition": 25,
                "language": "python"
            }
        }


class AutocompleteResponse(BaseModel):
    """
    Schema for autocomplete response.
    
    Attributes:
        suggestion: AI-generated code suggestion
        confidence: Confidence score (0.0 to 1.0)
        type: Type of suggestion (completion, import, etc.)
    """
    suggestion: str = Field(..., description="Code suggestion")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence score")
    type: str = Field(default="completion", description="Suggestion type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "suggestion": "\"Hello, World!\")",
                "confidence": 0.85,
                "type": "completion"
            }
        }


class WebSocketMessage(BaseModel):
    """
    Schema for WebSocket messages.
    
    Attributes:
        type: Message type (code_update, user_join, user_leave, etc.)
        code: Code content (for code_update messages)
        user_id: User identifier (optional)
        timestamp: Message timestamp
    """
    type: str = Field(..., description="Message type")
    code: Optional[str] = Field(None, description="Code content")
    user_id: Optional[str] = Field(None, description="User identifier")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "code_update",
                "code": "print('Hello, World!')",
                "timestamp": "2025-01-15T10:30:00Z"
            }
        }