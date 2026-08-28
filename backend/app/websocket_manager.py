from fastapi import WebSocket
import json


class ConnectionManager:
    """
    Tracks active WebSocket connections and broadcasts events to all of them.
    In a multi-instance deployment this would be backed by Redis Pub/Sub
    (see notes in README) so that broadcasts fan out across replicas —
    this in-memory version is intentionally simple for a single-instance demo.
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event: str, payload: dict):
        message = json.dumps({"event": event, "payload": payload})
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)
        for dead in dead_connections:
            self.disconnect(dead)


manager = ConnectionManager()
