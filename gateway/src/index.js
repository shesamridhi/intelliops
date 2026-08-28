require("dotenv").config();
const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const rateLimit = require("express-rate-limit");
const { createProxyMiddleware } = require("http-proxy-middleware");

const { verifyToken, requireRole } = require("./middleware/auth");
const notificationsRouter = require("./routes/notifications");

const app = express();
const PORT = process.env.PORT || 4000;
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

app.use(helmet());
app.use(cors());
app.use(express.json());

// Basic DDoS / abuse protection at the edge, before requests reach FastAPI.
const limiter = rateLimit({ windowMs: 60 * 1000, max: 120 });
app.use(limiter);

app.get("/health", (req, res) => res.json({ status: "ok", service: "intelliops-gateway" }));

// Public auth routes pass straight through to the Python backend (no token yet to verify).
app.use(
  "/api/auth",
  createProxyMiddleware({ target: BACKEND_URL, changeOrigin: true })
);

// gRPC-bridging route: Node talks gRPC to the notification microservice directly.
app.use("/api/notifications", verifyToken, notificationsRouter);

// Example of a gateway-enforced role restriction BEFORE proxying to backend —
// demonstrates defense-in-depth RBAC (gateway + service both enforce it).
app.use(
  "/api/inventory",
  verifyToken,
  (req, res, next) => {
    // Only mutating requests are role-restricted at the gateway; GETs pass through.
    if (req.method === "GET") return next();
    return requireRole("admin", "manager")(req, res, next);
  },
  createProxyMiddleware({ target: BACKEND_URL, changeOrigin: true })
);

// All other authenticated REST traffic proxies through to FastAPI.
app.use(
  ["/api/orders", "/api/dashboard", "/api/agent"],
  verifyToken,
  createProxyMiddleware({ target: BACKEND_URL, changeOrigin: true })
);

// WebSocket upgrade requests are proxied too (ws: true), so the frontend
// only ever needs to know about the gateway's origin, not the backend's.
const wsProxy = createProxyMiddleware({
  target: BACKEND_URL.replace("http", "ws"),
  changeOrigin: true,
  ws: true,
});
app.use("/ws", wsProxy);

if (require.main === module) {
  const server = app.listen(PORT, () => {
    console.log(`IntelliOps gateway listening on port ${PORT}`);
  });
  server.on("upgrade", wsProxy.upgrade);
}

module.exports = app;
