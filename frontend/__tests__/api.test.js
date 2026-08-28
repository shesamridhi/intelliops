/**
 * Unit tests for the API client helper — the piece most worth unit
 * testing since it's pure logic (no DOM), unlike the page components.
 */
import { apiFetch } from "../lib/api";

describe("apiFetch", () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  it("attaches Authorization header when a token is provided", async () => {
    global.fetch.mockResolvedValue({ ok: true, json: async () => ({ ok: true }) });
    await apiFetch("/api/dashboard/stats", { token: "abc123" });

    const [, options] = global.fetch.mock.calls[0];
    expect(options.headers.Authorization).toBe("Bearer abc123");
  });

  it("throws with the backend's detail message on failure", async () => {
    global.fetch.mockResolvedValue({
      ok: false,
      statusText: "Unauthorized",
      json: async () => ({ detail: "Invalid credentials" }),
    });
    await expect(apiFetch("/api/auth/login")).rejects.toThrow("Invalid credentials");
  });

  it("serializes the request body as JSON", async () => {
    global.fetch.mockResolvedValue({ ok: true, json: async () => ({}) });
    await apiFetch("/api/auth/login", { method: "POST", body: { email: "a@b.com" } });

    const [, options] = global.fetch.mock.calls[0];
    expect(options.body).toBe(JSON.stringify({ email: "a@b.com" }));
  });
});
