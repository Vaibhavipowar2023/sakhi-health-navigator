const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function sendChat(conversation, sessionId = "") {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation, session_id: sessionId }),
  });

  if (!res.ok) {
    throw new Error(`Server error: ${res.status}`);
  }

  return res.json();
}
