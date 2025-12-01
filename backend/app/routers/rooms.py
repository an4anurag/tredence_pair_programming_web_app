"""
Rooms router for handling room creation and management.

This module provides endpoints for:
- Creating new coding rooms
- Retrieving room information
- Managing room state
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Room
from app.schemas import RoomCreate, RoomResponse
from app.services.room_service import RoomService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate = RoomCreate(),
    db: Session = Depends(get_db)
):
    """
    Create a new collaborative coding room.
    
    Args:
        room_data: Optional room configuration (language)
        db: Database session dependency
        
    Returns:
        RoomResponse: Created room details including roomId
        
    Example:
        POST /rooms
        {
            "language": "python"
        }
        
        Response:
        {
            "roomId": "abc123-def456",
            "code": "# Write your Python code here\\n\\n",
            "language": "python",
            "created_at": "2025-01-15T10:30:00Z"
        }
    """
    try:
        room_service = RoomService(db)
        room = room_service.create_room(language=room_data.language)
        
        logger.info(f"Room created successfully: {room.id}")
        
        return RoomResponse(
            roomId=room.id,
            code=room.code,
            language=room.language,
            created_at=room.created_at
        )
    except Exception as e:
        logger.error(f"Error creating room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create room"
        )


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve room information by room ID.
    
    Args:
        room_id: Unique room identifier
        db: Database session dependency
        
    Returns:
        RoomResponse: Room details
        
    Raises:
        HTTPException: 404 if room not found
        
    Example:
        GET /rooms/abc123-def456
        
        Response:
        {
            "roomId": "abc123-def456",
            "code": "print('Hello')",
            "language": "python",
            "created_at": "2025-01-15T10:30:00Z"
        }
    """
    try:
        room_service = RoomService(db)
        room = room_service.get_room(room_id)
        
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        
        return RoomResponse(
            roomId=room.id,
            code=room.code,
            language=room.language,
            created_at=room.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve room"
        )


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a room and all its associated data.
    
    Args:
        room_id: Unique room identifier
        db: Database session dependency
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: 404 if room not found
    """
    try:
        room_service = RoomService(db)
        success = room_service.delete_room(room_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        
        logger.info(f"Room deleted successfully: {room_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete room"
        )