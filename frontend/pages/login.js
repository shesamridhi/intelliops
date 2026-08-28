import { useState } from "react";
import { useRouter } from "next/router";
import { login, register } from "../lib/api";

export default function Login() {
  const router = useRouter();
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("staff");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await register(email, password, fullName, role);
      }
      const { access_token } = await login(email, password);
      // NOTE: for a production app, prefer an httpOnly cookie set by the
      // server over localStorage to reduce XSS token-theft risk. Kept
      // simple here for the demo; this trade-off is worth naming out loud
      // in an interview. We also mirror the token into a (non-httpOnly)
      // cookie purely so the dashboard's getServerSideProps can read it
      // and pre-fetch data server-side — a real SSR use case.
      localStorage.setItem("intelliops_token", access_token);
      document.cookie = `intelliops_token=${access_token}; path=/; max-age=1800; samesite=lax`;
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container" style={{ maxWidth: 420 }}>
      <h1>IntelliOps</h1>
      <p style={{ color: "#8b8fa3" }}>AI-augmented mini ERP — sign {mode === "login" ? "in" : "up"}</p>

      <form className="card" onSubmit={handleSubmit}>
        {error && <div className="error">{error}</div>}

        {mode === "register" && (
          <>
            <input placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              style={{ width: "100%", padding: "0.6rem", marginBottom: "0.75rem", borderRadius: 6, background: "#0f1117", color: "#e6e8ee", border: "1px solid #2a2e3a" }}
            >
              <option value="staff">Staff</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
            </select>
          </>
        )}

        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password (min 8 chars)" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />

        <button type="submit" disabled={loading} style={{ width: "100%" }}>
          {loading ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
        </button>
      </form>

      <p style={{ textAlign: "center", color: "#8b8fa3" }}>
        {mode === "login" ? "New here? " : "Already have an account? "}
        <a href="#" onClick={(e) => { e.preventDefault(); setMode(mode === "login" ? "register" : "login"); }}>
          {mode === "login" ? "Create an account" : "Sign in"}
        </a>
      </p>
    </div>
  );
}
