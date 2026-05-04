"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useChatStore } from "@/lib/store";

interface ProviderData { provider: string; models: string[]; local?: boolean; }

export default function ModelPicker() {
  const [providers, setProviders] = useState<ProviderData[]>([]);
  const { provider, model, setProvider, setModel } = useChatStore();

  useEffect(() => {
    api.getModels().then(setProviders).catch(() => {});
  }, []);

  const currentProvider = providers.find(p => p.provider === provider);

  return (
    <div className="flex gap-2 items-center flex-wrap">
      <select
        value={provider}
        onChange={e => { setProvider(e.target.value); setModel(providers.find(p => p.provider === e.target.value)?.models[0] || ""); }}
        className="bg-zinc-800 text-white text-sm rounded px-2 py-1 border border-zinc-600"
      >
        {providers.map(p => (
          <option key={p.provider} value={p.provider}>
            {p.local ? "🖥 " : "☁ "}{p.provider}
          </option>
        ))}
      </select>
      <select
        value={model}
        onChange={e => setModel(e.target.value)}
        className="bg-zinc-800 text-white text-sm rounded px-2 py-1 border border-zinc-600 max-w-xs"
      >
        {currentProvider?.models.map(m => (
          <option key={m} value={m}>{m}</option>
        ))}
      </select>
    </div>
  );
}
