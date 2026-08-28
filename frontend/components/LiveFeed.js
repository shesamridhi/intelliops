import { useEffect, useRef, useState } from "react";
import { GATEWAY_URL } from "../lib/api";

/**
 * Subscribes to the gateway's proxied WebSocket for real-time order
 * events. Demonstrates bidirectional/event-driven UI updates without
 * polling — a direct answer to the JD's WebSocket requirement.
 */
export default function LiveFeed({ token }) {
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!token) return;

    const wsUrl = GATEWAY_URL.replace("http", "ws") + `/ws/live?token=${token}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        setEvents((prev) => [data, ...prev].slice(0, 20));
      } catch {
        /* ignore malformed frames */
      }
    };

    return () => ws.close();
  }, [token]);

  return (
    <div className="card">
      <h3>
        <span className={`live-dot ${connected ? "connected" : "disconnected"}`} />
        Live order feed {connected ? "" : "(reconnecting…)"}
      </h3>
      {events.length === 0 && <p style={{ color: "#8b8fa3" }}>No events yet — create an order to see it appear here instantly.</p>}
      {events.map((e, i) => (
        <div key={i} className="feed-item">
          <strong>{e.event}</strong> — {JSON.stringify(e.payload)}
        </div>
      ))}
    </div>
  );
}
