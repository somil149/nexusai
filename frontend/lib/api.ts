const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = {
  getModels: () => fetch(`${BASE}/api/models`).then(r => r.json()),
  getSessions: () => fetch(`${BASE}/api/sessions`).then(r => r.json()),
  createSession: () => fetch(`${BASE}/api/sessions`, { method: "POST" }).then(r => r.json()),
  deleteSession: (id: string) => fetch(`${BASE}/api/sessions/${id}`, { method: "DELETE" }).then(r => r.json()),
  getMessages: (id: string) => fetch(`${BASE}/api/sessions/${id}/messages`).then(r => r.json()),
  getTotalCost: () => fetch(`${BASE}/api/cost`).then(r => r.json()),
  getSessionCost: (id: string) => fetch(`${BASE}/api/cost/${id}`).then(r => r.json()),
  getAgentConfigs: () => fetch(`${BASE}/api/agent-configs`).then(r => r.json()),
  createAgentConfig: (body: object) => fetch(`${BASE}/api/agent-configs`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }).then(r => r.json()),
  uploadDocument: (file: File, sessionId = "") => {
    const fd = new FormData();
    fd.append("file", file);
    return fetch(`${BASE}/api/documents/upload?session_id=${sessionId}`, { method: "POST", body: fd }).then(r => r.json());
  },
  tts: async (text: string, voice = "en-female"): Promise<string> => {
    const r = await fetch(`${BASE}/api/tts`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, voice }),
    });
    const blob = await r.blob();
    return URL.createObjectURL(blob);
  },
};

export const WS_BASE = BASE.replace("http", "ws");
