import { useState } from "react";
import { queryAgent } from "../lib/api";

export default function AgentChat({ token }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await queryAgent(token, userMsg.text);
      setMessages((prev) => [
        ...prev,
        { role: "agent", text: res.answer, provider: res.provider_used, actions: res.actions_taken },
      ]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "agent", text: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h3>Ask the ops agent</h3>
      <div className="chat-log">
        {messages.map((m, i) => (
          <div key={i} className={`chat-msg ${m.role}`}>
            <strong>{m.role === "user" ? "You" : `Agent (${m.provider || "…"})`}:</strong> {m.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleSend} style={{ display: "flex", gap: "0.5rem" }}>
        <input
          placeholder='Try: "which items are low on stock?"'
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ marginBottom: 0 }}
        />
        <button type="submit" disabled={loading}>{loading ? "…" : "Send"}</button>
      </form>
    </div>
  );
}
