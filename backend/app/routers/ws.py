from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket_manager import manager
from app.security import decode_token

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, token: str):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4401)
        return

    await manager.connect(websocket)
    try:
        while True:
            # Client can send pings; we mainly push server -> client events
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
