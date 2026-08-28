import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import LiveFeed from "../components/LiveFeed";
import AgentChat from "../components/AgentChat";
import { getDashboardStats } from "../lib/api";

const GATEWAY_URL_SERVER = process.env.GATEWAY_URL_INTERNAL || process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:4000";

/**
 * True server-side rendering: this runs on the Next.js server, on every
 * request, BEFORE any HTML reaches the browser. We read the auth token
 * from the request cookie, call the gateway directly from the server,
 * and pass the result down as props — so the dashboard's first paint
 * already has real numbers (no loading spinner, better SEO/perf, and it
 * works even with JS disabled for the initial view).
 */
export async function getServerSideProps({ req }) {
  const cookieHeader = req.headers.cookie || "";
  const match = cookieHeader.match(/intelliops_token=([^;]+)/);
  const token = match ? match[1] : null;

  if (!token) {
    return { redirect: { destination: "/login", permanent: false } };
  }

  try {
    const res = await fetch(`${GATEWAY_URL_SERVER}/api/dashboard/stats`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("stats fetch failed");
    const initialStats = await res.json();
    return { props: { initialStats, token } };
  } catch {
    // Token might be expired/invalid — fall back to client-side login flow.
    return { redirect: { destination: "/login", permanent: false } };
  }
}

export default function Dashboard({ initialStats, token }) {
  const router = useRouter();
  const [stats, setStats] = useState(initialStats);
  const [clientToken, setClientToken] = useState(token);

  // Client hydration: prefer localStorage token if present (kept in sync
  // with the cookie at login time), and allow the client to refresh
  // stats independently of the SSR pass (e.g. after creating an order).
  useEffect(() => {
    const stored = localStorage.getItem("intelliops_token");
    if (stored) setClientToken(stored);
  }, []);

  async function refreshStats() {
    try {
      const fresh = await getDashboardStats(clientToken);
      setStats(fresh);
    } catch {
      router.push("/login");
    }
  }

  function logout() {
    localStorage.removeItem("intelliops_token");
    document.cookie = "intelliops_token=; path=/; max-age=0";
    router.push("/login");
  }

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>IntelliOps Dashboard</h1>
        <button onClick={logout}>Logout</button>
      </div>

      <div className="stats-grid">
        <div className="card">
          <div className="stat-value">{stats.total_orders}</div>
          <div className="stat-label">Total Orders</div>
        </div>
        <div className="card">
          <div className="stat-value">{stats.pending_orders}</div>
          <div className="stat-label">Pending Orders</div>
        </div>
        <div className="card">
          <div className="stat-value">{stats.low_stock_items}</div>
          <div className="stat-label">Low Stock Items</div>
        </div>
        <div className="card">
          <div className="stat-value">${stats.total_inventory_value.toFixed(2)}</div>
          <div className="stat-label">Inventory Value</div>
        </div>
      </div>
      <p style={{ color: "#8b8fa3", fontSize: "0.8rem" }}>
        {stats.cached ? "⚡ Served from Redis cache" : "🔄 Freshly computed"}
        {" · "}
        <a href="#" onClick={(e) => { e.preventDefault(); refreshStats(); }}>refresh</a>
      </p>

      <LiveFeed token={clientToken} />
      <AgentChat token={clientToken} />
    </div>
  );
}
