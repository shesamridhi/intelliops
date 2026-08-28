const express = require("express");
const { sendNotification } = require("../grpcClient");

const router = express.Router();

// POST /api/notifications/send  -> bridges REST (from React frontend) to gRPC (notification microservice)
router.post("/send", async (req, res) => {
  const { recipientId, channel, subject, message } = req.body;
  if (!recipientId || !channel || !subject || !message) {
    return res.status(400).json({ detail: "recipientId, channel, subject, message are required" });
  }

  try {
    const result = await sendNotification({ recipientId, channel, subject, message });
    res.status(202).json({ success: result.success, notificationId: result.notification_id });
  } catch (err) {
    // The notification microservice is non-critical to the main request
    // path — a real system would queue and retry rather than fail hard.
    res.status(502).json({ detail: "Notification service unavailable", error: err.message });
  }
});

module.exports = router;
