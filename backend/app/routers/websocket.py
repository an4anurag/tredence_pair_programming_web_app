"""
WebSocket router for real-time collaborative editing.

This module handles WebSocket connections for live code synchronization
between multiple users in the same room.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.websocket_manager import WebSocketManager
from app.services.room_service import RoomService
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize WebSocket manager (singleton pattern)
ws_manager = WebSocketManager()

@router.websocket("/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time collaborative editing.
    
    This endpoint:
    1. Accepts WebSocket connections for a specific room
    2. Adds the connection to the room's connection pool
    3. Broadcasts code changes to all connected clients
    4. Handles disconnections gracefully
    
    Args:
        websocket: WebSocket connection
        room_id: Unique room identifier
        db: Database session dependency
        
    Message Format (Client -> Server):
        {
            "type": "code_update",
            "code": "print('Hello, World!')"
        }
        
    Message Format (Server -> Client):
        {
            "type": "code_update",
            "code": "print('Hello, World!')"
        }
        OR
        {
            "type": "user_count",
            "count": 2
        }
        
    Example Usage (JavaScript):
        const ws = new WebSocket('ws://localhost:8000/ws/abc123');
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'code_update') {
                editor.setValue(data.code);
            }
        };
        
        ws.send(JSON.stringify({
            type: 'code_update',
            code: editor.getValue()
        }));
    """
    # Verify room exists
    room_service = RoomService(db)
    room = room_service.get_room(room_id)
    
    if not room:
        await websocket.close(code=4004, reason="Room not found")
        logger.warning(f"Connection rejected: Room {room_id} not found")
        return
    
    # Accept WebSocket connection
    await ws_manager.connect(websocket, room_id)
    logger.info(f"Client connected to room {room_id}. Total connections: {ws_manager.get_connection_count(room_id)}")
    
    # Send current room code to the new connection
    try:
        await websocket.send_json({
            "type": "code_update",
            "code": room.code
        })
        
        # Broadcast updated user count
        await ws_manager.broadcast_user_count(room_id)
        
    except Exception as e:
        logger.error(f"Error sending initial data: {str(e)}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "code_update":
                code = message.get("code", "")
                
                # Update room code in database
                room_service.update_room_code(room_id, code)
                
                # Broadcast to all clients in the room (except sender)
                await ws_manager.broadcast(
                    room_id,
                    {
                        "type": "code_update",
                        "code": code
                    },
                    exclude=websocket
                )
                
                logger.debug(f"Code updated in room {room_id}")
            
    except WebSocketDisconnect:
        # Handle disconnection
        ws_manager.disconnect(websocket, room_id)
        logger.info(
            f"Client disconnected from room {room_id}. "
            f"Remaining connections: {ws_manager.get_connection_count(room_id)}"
        )
        
        # Broadcast updated user count
        await ws_manager.broadcast_user_count(room_id)
        
    except Exception as e:
        logger.error(f"WebSocket error in room {room_id}: {str(e)}")
        ws_manager.disconnect(websocket, room_id)
        await ws_manager.broadcast_user_count(room_id)