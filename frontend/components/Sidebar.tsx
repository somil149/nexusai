"use client";
import { useEffect, useState } from "react";
import { useChatStore } from "@/lib/store";
import { api } from "@/lib/api";
import { Plus, Trash2, DollarSign, Bot } from "lucide-react";

export default function Sidebar() {
  const { sessions, setSessions, activeSession, setActiveSession, setMessages } = useChatStore();
  const [totalCost, setTotalCost] = useState<any[]>([]);
  const [showCost, setShowCost] = useState(false);

  const loadSessions = () => api.getSessions().then(setSessions);

  useEffect(() => { loadSessions(); }, []);

  const newSession = async () => {
    const s = await api.createSession();
    await loadSessions();
    setActiveSession(s.id);
    setMessages([]);
  };

  const deleteSession = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await api.deleteSession(id);
    if (activeSession === id) { setActiveSession(null); setMessages([]); }
    loadSessions();
  };

  const openCost = async () => {
    const data = await api.getTotalCost();
    setTotalCost(data);
    setShowCost(true);
  };

  return (
    <div className="w-64 bg-zinc-900 border-r border-zinc-700 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-zinc-700">
        <div className="flex items-center gap-2 mb-3">
          <Bot size={20} className="text-blue-400" />
          <span className="font-bold text-white">NexusAI</span>
        </div>
        <button onClick={newSession} className="w-full flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white text-sm px-3 py-2 rounded-lg">
          <Plus size={16} /> New Chat
        </button>
      </div>

      {/* Sessions */}
      <div className="flex-1 overflow-y-auto p-2">
        {sessions.map(s => (
          <div key={s.id} onClick={() => { setActiveSession(s.id); api.getMessages(s.id).then(setMessages); }}
            className={`flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer mb-1 group text-sm ${
              activeSession === s.id ? "bg-zinc-700 text-white" : "text-zinc-400 hover:bg-zinc-800 hover:text-white"
            }`}>
            <span className="truncate flex-1">{s.title || "New Chat"}</span>
            <button onClick={(e) => deleteSession(s.id, e)} className="opacity-0 group-hover:opacity-100 text-zinc-500 hover:text-red-400 ml-1">
              <Trash2 size={13} />
            </button>
          </div>
        ))}
      </div>

      {/* Cost tracker */}
      <div className="p-3 border-t border-zinc-700">
        <button onClick={openCost} className="flex items-center gap-2 text-zinc-400 hover:text-white text-sm w-full px-2 py-1.5 rounded hover:bg-zinc-800">
          <DollarSign size={15} /> Cost Tracker
        </button>
      </div>

      {/* Cost modal */}
      {showCost && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={() => setShowCost(false)}>
          <div className="bg-zinc-800 rounded-xl p-6 w-96" onClick={e => e.stopPropagation()}>
            <h2 className="text-white font-bold mb-4">💰 Total API Cost</h2>
            {totalCost.length === 0 ? <p className="text-zinc-400 text-sm">No usage yet.</p> : (
              <table className="w-full text-sm text-zinc-300">
                <thead><tr className="text-zinc-500 text-xs"><th className="text-left pb-2">Provider</th><th className="text-right pb-2">Tokens</th><th className="text-right pb-2">Cost</th></tr></thead>
                <tbody>
                  {totalCost.map((r: any) => (
                    <tr key={r.provider} className="border-t border-zinc-700">
                      <td className="py-1.5">{r.provider}</td>
                      <td className="text-right">{(r.input_tokens + r.output_tokens).toLocaleString()}</td>
                      <td className="text-right text-green-400">${r.cost_usd.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <button onClick={() => setShowCost(false)} className="mt-4 text-zinc-400 hover:text-white text-sm">Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
