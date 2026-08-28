const jwt = require("jsonwebtoken");

const JWT_SECRET = process.env.JWT_SECRET_KEY || "CHANGE_ME_IN_PRODUCTION_USE_ENV_VAR";

/**
 * Verifies the same HS256 JWT issued by the Python backend (shared secret).
 * This lets the gateway make authorization decisions (e.g. rate-limit by
 * role, reject expired tokens early) without a round trip to the backend.
 */
function verifyToken(req, res, next) {
  const header = req.headers.authorization;
  if (!header || !header.startsWith("Bearer ")) {
    return res.status(401).json({ detail: "Missing bearer token" });
  }

  const token = header.split(" ")[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET, { algorithms: ["HS256"] });
    req.user = { id: decoded.sub, role: decoded.role };
    next();
  } catch (err) {
    return res.status(401).json({ detail: "Invalid or expired token" });
  }
}

function requireRole(...roles) {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ detail: `Role '${req.user?.role}' not permitted` });
    }
    next();
  };
}

module.exports = { verifyToken, requireRole };
