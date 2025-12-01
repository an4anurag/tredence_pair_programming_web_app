"""
WebSocket connection manager for handling multiple concurrent connections.

This manager maintains:
- Connection pools per room
- Broadcasting logic
- Connection lifecycle management
"""

from fastapi import WebSocket
from typing import Dict, List
import logging
import json

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Manages WebSocket connections for real-time collaboration.
    
    This class implements a singleton pattern to maintain a single
    connection pool across the application.
    """
    
    def __init__(self):
        """
        Initialize WebSocket manager with empty connection pools.
        
        Structure:
            {
                "room_id_1": [websocket1, websocket2, ...],
                "room_id_2": [websocket3, websocket4, ...],
                ...
            }
        """
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str):
        """
        Accept a new WebSocket connection and add it to the room pool.
        
        Args:
            websocket: WebSocket connection to add
            room_id: Room identifier
            
        Example:
            await ws_manager.connect(websocket, "abc123")
        """
        await websocket.accept()
        
        # Initialize room connection list if it doesn't exist
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        
        # Add connection to room
        self.active_connections[room_id].append(websocket)
        
        logger.info(
            f"WebSocket connected to room {room_id}. "
            f"Total connections in room: {len(self.active_connections[room_id])}"
        )
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        """
        Remove a WebSocket connection from the room pool.
        
        Args:
            websocket: WebSocket connection to remove
            room_id: Room identifier
            
        Example:
            ws_manager.disconnect(websocket, "abc123")
        """
        if room_id in self.active_connections:
            try:
                self.active_connections[room_id].remove(websocket)
                
                # Clean up empty room pools
                if len(self.active_connections[room_id]) == 0:
                    del self.active_connections[room_id]
                    logger.info(f"Room {room_id} connection pool deleted (no active connections)")
                else:
                    logger.info(
                        f"WebSocket disconnected from room {room_id}. "
                        f"Remaining connections: {len(self.active_connections[room_id])}"
                    )
            except ValueError:
                logger.warning(f"Attempted to disconnect non-existent websocket from room {room_id}")
    
    async def broadcast(
        self,
        room_id: str,
        message: dict,
        exclude: WebSocket | None = None
    ):
        """
        Broadcast a message to all connections in a room.
        
        Args:
            room_id: Room identifier
            message: Message dictionary to broadcast
            exclude: Optional WebSocket to exclude from broadcast (e.g., sender)
            
        Example:
            await ws_manager.broadcast(
                "abc123",
                {"type": "code_update", "code": "print('hello')"},
                exclude=sender_websocket
            )
        """
        if room_id not in self.active_connections:
            logger.warning(f"Attempted to broadcast to non-existent room {room_id}")
            return
        
        # Track failed connections for cleanup
        dead_connections = []
        
        # Send message to all connections except excluded one
        for connection in self.active_connections[room_id]:
            if connection == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {str(e)}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead_conn in dead_connections:
            self.disconnect(dead_conn, room_id)
    
    async def broadcast_user_count(self, room_id: str):
        """
        Broadcast the current number of connected users to all room members.
        
        Args:
            room_id: Room identifier
            
        Example:
            await ws_manager.broadcast_user_count("abc123")
        """
        count = self.get_connection_count(room_id)
        
        await self.broadcast(
            room_id,
            {
                "type": "user_count",
                "count": count
            }
        )
        
        logger.debug(f"Broadcasted user count ({count}) to room {room_id}")
    
    def get_connection_count(self, room_id: str) -> int:
        """
        Get the number of active connections in a room.
        
        Args:
            room_id: Room identifier
            
        Returns:
            int: Number of active connections
            
        Example:
            count = ws_manager.get_connection_count("abc123")
            print(f"Active users: {count}")
        """
        if room_id not in self.active_connections:
            return 0
        
        return len(self.active_connections[room_id])
    
    def get_all_rooms(self) -> List[str]:
        """
        Get list of all active room IDs.
        
        Returns:
            List[str]: List of room IDs with active connections
            
        Example:
            active_rooms = ws_manager.get_all_rooms()
            print(f"Active rooms: {active_rooms}")
        """
        return list(self.active_connections.keys())
    
    def get_total_connections(self) -> int:
        """
        Get total number of active connections across all rooms.
        
        Returns:
            int: Total active connections
            
        Example:
            total = ws_manager.get_total_connections()
            print(f"Total active connections: {total}")
        """
        return sum(len(connections) for connections in self.active_connections.values())
    
    async def send_to_user(self, websocket: WebSocket, message: dict):
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            websocket: Target WebSocket connection
            message: Message dictionary to send
            
        Example:
            await ws_manager.send_to_user(
                websocket,
                {"type": "error", "message": "Invalid operation"}
            )
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to user: {str(e)}")