const request = require("supertest");
const jwt = require("jsonwebtoken");

process.env.JWT_SECRET_KEY = "test-secret";
const app = require("../src/index");

const SECRET = "test-secret";

function makeToken(role = "staff", sub = "user-1") {
  return jwt.sign({ sub, role, type: "access" }, SECRET, { algorithm: "HS256", expiresIn: "10m" });
}

describe("gateway health", () => {
  it("responds 200 on /health", async () => {
    const res = await request(app).get("/health");
    expect(res.statusCode).toBe(200);
    expect(res.body.status).toBe("ok");
  });
});

describe("auth middleware", () => {
  it("rejects requests with no token on protected routes", async () => {
    const res = await request(app).get("/api/dashboard/stats");
    expect(res.statusCode).toBe(401);
  });

  it("rejects requests with a malformed token", async () => {
    const res = await request(app)
      .get("/api/dashboard/stats")
      .set("Authorization", "Bearer not-a-real-token");
    expect(res.statusCode).toBe(401);
  });

  it("blocks staff role from mutating inventory at the gateway layer", async () => {
    const token = makeToken("staff");
    const res = await request(app)
      .post("/api/inventory")
      .set("Authorization", `Bearer ${token}`)
      .send({ sku: "X", name: "Y", quantity: 1 });
    expect(res.statusCode).toBe(403);
  });
});

describe("notifications route validation", () => {
  it("requires all fields before attempting gRPC call", async () => {
    const token = makeToken("admin");
    const res = await request(app)
      .post("/api/notifications/send")
      .set("Authorization", `Bearer ${token}`)
      .send({ recipientId: "u1" }); // missing fields
    expect(res.statusCode).toBe(400);
  });
});
