"use client";
import { useEffect, useState, useRef } from "react";
import { api, WS_BASE } from "@/lib/api";
import { Plus, Trash2, Play } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Agent { role: string; goal: string; provider: string; model: string; }

export default function AgentBuilder() {
  const [agents, setAgents] = useState<Agent[]>([
    { role: "Researcher", goal: "Find relevant information", provider: "openai", model: "gpt-4o-mini" },
    { role: "Writer", goal: "Write clear, structured content", provider: "anthropic", model: "claude-haiku-3-5" },
  ]);
  const [task, setTask] = useState("");
  const [output, setOutput] = useState("");
  const [running, setRunning] = useState(false);
  const [providers, setProviders] = useState<any[]>([]);

  useEffect(() => { api.getModels().then(setProviders); }, []);

  const addAgent = () => setAgents([...agents, { role: "", goal: "", provider: "openai", model: "gpt-4o-mini" }]);
  const removeAgent = (i: number) => setAgents(agents.filter((_, idx) => idx !== i));
  const updateAgent = (i: number, field: keyof Agent, value: string) => {
    const updated = [...agents];
    updated[i] = { ...updated[i], [field]: value };
    setAgents(updated);
  };

  const runCrew = () => {
    if (!task || running) return;
    setOutput("");
    setRunning(true);
    const ws = new WebSocket(`${WS_BASE}/ws/crew/crew-${Date.now()}`);
    ws.onopen = () => ws.send(JSON.stringify({ agents, task }));
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "chunk") setOutput(o => o + data.content);
      if (data.type === "done" || data.type === "error") { setRunning(false); ws.close(); }
    };
    ws.onerror = () => setRunning(false);
  };

  return (
    <div className="flex-1 flex gap-4 p-6 overflow-auto bg-zinc-950">
      {/* Left: config */}
      <div className="w-96 flex flex-col gap-4">
        <h2 className="text-white font-bold text-lg">🤖 Agent Builder</h2>

        {agents.map((a, i) => (
          <div key={i} className="bg-zinc-800 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex justify-between items-center">
              <span className="text-zinc-400 text-xs font-mono">Agent {i + 1}</span>
              <button onClick={() => removeAgent(i)} className="text-zinc-500 hover:text-red-400"><Trash2 size={13} /></button>
            </div>
            <input value={a.role} onChange={e => updateAgent(i, "role", e.target.value)} placeholder="Role (e.g. Researcher)"
              className="bg-zinc-700 text-white text-sm rounded px-3 py-1.5 outline-none" />
            <input value={a.goal} onChange={e => updateAgent(i, "goal", e.target.value)} placeholder="Goal"
              className="bg-zinc-700 text-white text-sm rounded px-3 py-1.5 outline-none" />
            <div className="flex gap-2">
              <select value={a.provider} onChange={e => updateAgent(i, "provider", e.target.value)}
                className="bg-zinc-700 text-white text-xs rounded px-2 py-1 flex-1">
                {providers.map(p => <option key={p.provider} value={p.provider}>{p.provider}</option>)}
              </select>
              <select value={a.model} onChange={e => updateAgent(i, "model", e.target.value)}
                className="bg-zinc-700 text-white text-xs rounded px-2 py-1 flex-1">
                {providers.find(p => p.provider === a.provider)?.models.map((m: string) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>
        ))}

        <button onClick={addAgent} className="flex items-center gap-2 text-zinc-400 hover:text-white text-sm border border-zinc-700 rounded-xl px-4 py-2 hover:border-zinc-500">
          <Plus size={15} /> Add Agent
        </button>

        <textarea value={task} onChange={e => setTask(e.target.value)} placeholder="Describe the task for the crew..."
          rows={4} className="bg-zinc-800 text-white text-sm rounded-xl px-4 py-3 outline-none border border-zinc-700 focus:border-blue-500 resize-none" />

        <button onClick={runCrew} disabled={running || !task}
          className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded-xl px-4 py-2.5 font-medium">
          <Play size={16} /> {running ? "Running..." : "Run Crew"}
        </button>
      </div>

      {/* Right: output */}
      <div className="flex-1 bg-zinc-900 rounded-xl p-6 overflow-auto">
        {output ? (
          <div className="text-zinc-200 text-sm prose prose-invert max-w-none">
            <ReactMarkdown>{output}</ReactMarkdown>
          </div>
        ) : (
          <p className="text-zinc-600 text-sm">Crew output will appear here...</p>
        )}
        {running && <div className="text-blue-400 text-sm animate-pulse mt-2">Agents working...</div>}
      </div>
    </div>
  );
}
