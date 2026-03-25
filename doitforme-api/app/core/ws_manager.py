"""WebSocket Connection Manager — singleton that groups connections by task_id."""
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections grouped by task_id (rooms)."""

    def __init__(self) -> None:
        # {task_id: {user_id: WebSocket}}
        self.active_connections: dict[UUID, dict[UUID, WebSocket]] = {}

    async def connect(self, task_id: UUID, user_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = {}
        self.active_connections[task_id][user_id] = websocket

    def disconnect(self, task_id: UUID, user_id: UUID) -> None:
        if task_id in self.active_connections:
            self.active_connections[task_id].pop(user_id, None)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def broadcast_to_task(
        self,
        task_id: UUID,
        message_json: dict,
        *,
        exclude_sender: UUID | None = None,
    ) -> None:
        """Send a message to all users connected to a task room."""
        if task_id not in self.active_connections:
            return
        for uid, ws in list(self.active_connections[task_id].items()):
            if uid == exclude_sender:
                continue
            try:
                await ws.send_json(message_json)
            except Exception:
                # Connection broken — remove silently
                self.active_connections[task_id].pop(uid, None)


# Singleton instance shared across the application
ws_manager = ConnectionManager()
