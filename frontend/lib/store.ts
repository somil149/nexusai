import { create } from "zustand";

export interface Message {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  model?: string;
  provider?: string;
}

export interface Session {
  id: string;
  title: string;
  model: string;
  provider: string;
  updated_at: string;
}

interface ChatStore {
  sessions: Session[];
  activeSession: string | null;
  messages: Message[];
  provider: string;
  model: string;
  useTools: boolean;
  useRag: boolean;
  isStreaming: boolean;
  setSessions: (s: Session[]) => void;
  setActiveSession: (id: string | null) => void;
  setMessages: (m: Message[]) => void;
  appendChunk: (chunk: string) => void;
  addMessage: (m: Message) => void;
  setProvider: (p: string) => void;
  setModel: (m: string) => void;
  setUseTools: (v: boolean) => void;
  setUseRag: (v: boolean) => void;
  setStreaming: (v: boolean) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  sessions: [],
  activeSession: null,
  messages: [],
  provider: "openai",
  model: "gpt-4o-mini",
  useTools: true,
  useRag: false,
  isStreaming: false,
  setSessions: (sessions) => set({ sessions }),
  setActiveSession: (activeSession) => set({ activeSession }),
  setMessages: (messages) => set({ messages }),
  appendChunk: (chunk) => set((s) => {
    const msgs = [...s.messages];
    const last = msgs[msgs.length - 1];
    if (last?.role === "assistant") {
      msgs[msgs.length - 1] = { ...last, content: last.content + chunk };
    } else {
      msgs.push({ id: Date.now().toString(), role: "assistant", content: chunk });
    }
    return { messages: msgs };
  }),
  addMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  setProvider: (provider) => set({ provider }),
  setModel: (model) => set({ model }),
  setUseTools: (useTools) => set({ useTools }),
  setUseRag: (useRag) => set({ useRag }),
  setStreaming: (isStreaming) => set({ isStreaming }),
}));
