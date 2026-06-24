import asyncio
import json
import logging
from typing import List, Dict
from fastapi import WebSocket

from app.db.redis import get_redis_client

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.redis_task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Start redis listener if not running
        if self.redis_task is None or self.redis_task.done():
            self.redis_task = asyncio.create_task(self._listen_to_redis())

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logging.error(f"WebSocket broadcast error: {e}")
                
    async def _listen_to_redis(self):
        try:
            redis_client = await get_redis_client()
            pubsub = redis_client.pubsub()
            await pubsub.subscribe("nginx_realtime_events")
            
            logging.info("WebSocket Manager subscribed to Redis pubsub")
            
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await self.broadcast(message["data"])
                    
        except Exception as e:
            logging.error(f"Redis pubsub error: {e}")
        finally:
            self.redis_task = None

manager = ConnectionManager()
