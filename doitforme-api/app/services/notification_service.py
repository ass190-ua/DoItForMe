from uuid import UUID
from typing import Optional

class NotificationService:
    """
    Service for sending push notifications (FCM).
    Currently implemented as a stub/blueprint for production deployment.
    """
    
    @staticmethod
    async def send_push_notification(
        user_id: UUID, 
        title: str, 
        body: str, 
        data: Optional[dict] = None,
        fcm_token: Optional[str] = None
    ):
        """
        Sends a push notification to a specific user.
        In production, this would use 'firebase-admin' SDK.
        """
        if not fcm_token:
            # In a real scenario, we'd fetch the token from the DB if not provided
            pass
            
        print(f"PUSH NOTIFICATION [User: {user_id}]: {title} - {body}")
        if data:
            print(f"PUSH DATA: {data}")
            
    @classmethod
    async def notify_new_message(cls, recipient_id: UUID, sender_name: str, message_text: str, task_id: UUID):
        await cls.send_push_notification(
            user_id=recipient_id,
            title=f"Nuevo mensaje de {sender_name}",
            body=message_text[:100] + ("..." if len(message_text) > 100 else ""),
            data={"type": "chat", "task_id": str(task_id)}
        )
        
    @classmethod
    async def notify_task_status_change(cls, user_id: UUID, task_title: str, new_status: str, task_id: UUID):
        await cls.send_push_notification(
            user_id=user_id,
            title="Actualización de tarea",
            body=f"Tu tarea '{task_title}' ha cambiado a estado {new_status}",
            data={"type": "task_update", "task_id": str(task_id)}
        )
