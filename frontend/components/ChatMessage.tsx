"use client";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Message } from "@/lib/store";
import { api } from "@/lib/api";
import { Volume2 } from "lucide-react";

export default function ChatMessage({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";

  const speak = async () => {
    const url = await api.tts(msg.content);
    new Audio(url).play();
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4 group`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm relative ${
        isUser ? "bg-blue-600 text-white" : "bg-zinc-800 text-zinc-100"
      }`}>
        {isUser ? (
          <p className="whitespace-pre-wrap">{msg.content}</p>
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ className, children }) {
                const isBlock = className?.includes("language-");
                return isBlock ? (
                  <pre className="bg-zinc-900 rounded p-3 overflow-x-auto my-2 text-xs">
                    <code>{children}</code>
                  </pre>
                ) : (
                  <code className="bg-zinc-700 px-1 rounded text-xs">{children}</code>
                );
              },
            }}
          >
            {msg.content}
          </ReactMarkdown>
        )}
        {!isUser && (
          <button onClick={speak} className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-zinc-400 hover:text-white transition-opacity">
            <Volume2 size={14} />
          </button>
        )}
      </div>
    </div>
  );
}
