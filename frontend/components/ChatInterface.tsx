"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import { useChatStore } from "@/lib/store";
import { api, WS_BASE } from "@/lib/api";
import ChatMessage from "./ChatMessage";
import ModelPicker from "./ModelPicker";
import { Send, Mic, MicOff, Paperclip, Wrench, BookOpen } from "lucide-react";

export default function ChatInterface() {
  const { activeSession, messages, setMessages, appendChunk, addMessage,
          provider, model, useTools, useRag, setUseTools, setUseRag,
          isStreaming, setStreaming } = useChatStore();
  const [input, setInput] = useState("");
  const [listening, setListening] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (activeSession) {
      api.getMessages(activeSession).then(setMessages);
    }
  }, [activeSession]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = useCallback(async (text: string) => {
    if (!text.trim() || !activeSession || isStreaming) return;
    setInput("");
    addMessage({ id: Date.now().toString(), role: "user", content: text });
    setStreaming(true);

    const ws = new WebSocket(`${WS_BASE}/ws/chat/${activeSession}`);
    wsRef.current = ws;
    ws.onopen = () => ws.send(JSON.stringify({ provider, model, message: text, use_tools: useTools, use_rag: useRag }));
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "chunk") appendChunk(data.content);
      if (data.type === "done") { setStreaming(false); ws.close(); }
      if (data.type === "error") { setStreaming(false); ws.close(); }
    };
    ws.onerror = () => setStreaming(false);
  }, [activeSession, provider, model, useTools, useRag, isStreaming]);

  const toggleVoice = () => {
    if (!("webkitSpeechRecognition" in window)) return alert("Voice not supported in this browser");
    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }
    const rec = new (window as any).webkitSpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;
    rec.onresult = (e: any) => { send(e.results[0][0].transcript); setListening(false); };
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    rec.start();
    setListening(true);
  };

  const uploadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const result = await api.uploadDocument(file, activeSession || "");
    addMessage({ id: Date.now().toString(), role: "assistant", content: `📄 Uploaded **${result.filename}** — ${result.chunks} chunks indexed. You can now ask questions about it.` });
  };

  if (!activeSession) return (
    <div className="flex-1 flex items-center justify-center text-zinc-500">
      <p>Select or create a session to start chatting</p>
    </div>
  );

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center gap-3 px-4 py-2 border-b border-zinc-700 bg-zinc-900">
        <ModelPicker />
        <button onClick={() => setUseTools(!useTools)} title="Toggle tools"
          className={`p-1.5 rounded ${useTools ? "text-blue-400" : "text-zinc-500"}`}>
          <Wrench size={16} />
        </button>
        <button onClick={() => setUseRag(!useRag)} title="Toggle RAG"
          className={`p-1.5 rounded ${useRag ? "text-green-400" : "text-zinc-500"}`}>
          <BookOpen size={16} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {messages.map(m => <ChatMessage key={m.id} msg={m} />)}
        {isStreaming && <div className="text-zinc-500 text-sm animate-pulse ml-2">Thinking...</div>}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-zinc-700 bg-zinc-900">
        <div className="flex gap-2 items-end">
          <label className="cursor-pointer text-zinc-400 hover:text-white p-2">
            <Paperclip size={18} />
            <input type="file" className="hidden" onChange={uploadFile} accept=".pdf,.txt,.md,.py,.js,.ts" />
          </label>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }}
            placeholder="Message NexusAI... (Shift+Enter for newline)"
            rows={1}
            className="flex-1 bg-zinc-800 text-white rounded-xl px-4 py-2.5 text-sm resize-none outline-none border border-zinc-600 focus:border-blue-500"
          />
          <button onClick={toggleVoice} className={`p-2 rounded-xl ${listening ? "text-red-400 animate-pulse" : "text-zinc-400 hover:text-white"}`}>
            {listening ? <MicOff size={18} /> : <Mic size={18} />}
          </button>
          <button onClick={() => send(input)} disabled={isStreaming || !input.trim()}
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white p-2.5 rounded-xl">
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
