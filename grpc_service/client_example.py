"""
Standalone example showing how ANY service (Python backend, or via a
Node.js gRPC client) would call the NotificationService.
Run: python client_example.py   (after server.py is running)
"""
import grpc
import notification_pb2
import notification_pb2_grpc


def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = notification_pb2_grpc.NotificationServiceStub(channel)

        # Unary call
        resp = stub.SendNotification(notification_pb2.NotificationRequest(
            recipient_id="user-123",
            channel="email",
            subject="Order Shipped",
            message="Your order #4521 has shipped.",
        ))
        print(f"SendNotification -> success={resp.success} id={resp.notification_id}")

        # Server-streaming call
        print("Streaming notifications:")
        for event in stub.StreamNotifications(notification_pb2.StreamRequest(recipient_id="user-123")):
            print(f"  [{event.notification_id}] {event.message} @ {event.timestamp}")


if __name__ == "__main__":
    main()
