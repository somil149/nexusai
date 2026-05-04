"use client";
import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import ChatInterface from "@/components/ChatInterface";
import AgentBuilder from "@/components/AgentBuilder";
import { MessageSquare, Bot } from "lucide-react";

export default function Home() {
  const [tab, setTab] = useState<"chat" | "agents">("chat");

  return (
    <div className="flex h-screen bg-zinc-950 text-white overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        {/* Tab bar */}
        <div className="flex border-b border-zinc-700 bg-zinc-900 px-4">
          {[
            { id: "chat", label: "Chat", icon: <MessageSquare size={15} /> },
            { id: "agents", label: "Agent Builder", icon: <Bot size={15} /> },
          ].map(t => (
            <button key={t.id} onClick={() => setTab(t.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-sm border-b-2 transition-colors ${
                tab === t.id ? "border-blue-500 text-white" : "border-transparent text-zinc-500 hover:text-zinc-300"
              }`}>
              {t.icon}{t.label}
            </button>
          ))}
        </div>
        {tab === "chat" ? <ChatInterface /> : <AgentBuilder />}
      </div>
    </div>
  );
}
