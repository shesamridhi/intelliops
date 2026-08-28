const path = require("path");
const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");

const PROTO_PATH = path.join(__dirname, "..", "..", "grpc_service", "notification.proto");

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const notificationProto = grpc.loadPackageDefinition(packageDefinition).notification;

const GRPC_HOST = process.env.GRPC_NOTIFICATION_HOST || "localhost";
const GRPC_PORT = process.env.GRPC_NOTIFICATION_PORT || 50051;

/**
 * Node.js consuming a Python-implemented gRPC service — demonstrates
 * cross-language, strongly-typed service-to-service communication
 * (a key JD requirement) without needing REST/JSON at that boundary.
 */
function getNotificationClient() {
  return new notificationProto.NotificationService(
    `${GRPC_HOST}:${GRPC_PORT}`,
    grpc.credentials.createInsecure()
  );
}

function sendNotification({ recipientId, channel, subject, message }) {
  return new Promise((resolve, reject) => {
    const client = getNotificationClient();
    client.SendNotification(
      { recipient_id: recipientId, channel, subject, message },
      (err, response) => {
        if (err) return reject(err);
        resolve(response);
      }
    );
  });
}

module.exports = { getNotificationClient, sendNotification };
