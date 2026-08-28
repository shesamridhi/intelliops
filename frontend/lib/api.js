// Central place for talking to the gateway. Keeping this separate from
// components makes it trivial to unit test and to swap the base URL
// between local dev, Docker Compose, and the deployed Render URL.
export const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:4000";

export async function apiFetch(path, { method = "GET", token, body } = {}) {
  const res = await fetch(`${GATEWAY_URL}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export function login(email, password) {
  return apiFetch("/api/auth/login", { method: "POST", body: { email, password } });
}

export function register(email, password, fullName, role = "staff") {
  return apiFetch("/api/auth/register", {
    method: "POST",
    body: { email, password, full_name: fullName, role },
  });
}

export function getDashboardStats(token) {
  return apiFetch("/api/dashboard/stats", { token });
}

export function getOrders(token) {
  return apiFetch("/api/orders", { token });
}

export function queryAgent(token, prompt) {
  return apiFetch("/api/agent/query", { method: "POST", token, body: { prompt } });
}
