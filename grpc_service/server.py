"""
gRPC NotificationService server.

Run standalone with: python server.py
This intentionally has NO dependency on the FastAPI backend — it's a
separate microservice, callable over gRPC by both the Python backend and
the Node.js gateway, which is the point being demonstrated for the JD's
"event-driven backend architecture" and "gRPC APIs" requirements.
"""
import time
import uuid
import logging
from concurrent import futures

import grpc

import notification_pb2
import notification_pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-service")


class NotificationService(notification_pb2_grpc.NotificationServiceServicer):
    def SendNotification(self, request, context):
        notification_id = str(uuid.uuid4())
        logger.info(
            "Dispatching [%s] to %s via %s: %s",
            notification_id, request.recipient_id, request.channel, request.subject,
        )
        # In production this would call an email/SMS provider (SES, Twilio, FCM...).
        # Stubbed here so the service is runnable without external credentials.
        return notification_pb2.NotificationResponse(success=True, notification_id=notification_id)

    def StreamNotifications(self, request, context):
        """Server-streaming RPC: push a few demo events to the client."""
        for i in range(3):
            yield notification_pb2.NotificationEvent(
                notification_id=str(uuid.uuid4()),
                message=f"Demo event {i + 1} for {request.recipient_id}",
                timestamp=int(time.time()),
            )
            time.sleep(1)


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(NotificationService(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info("gRPC NotificationService listening on port %s", port)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
