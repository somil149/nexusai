"""Unified LLM client - routes to any provider with streaming support."""
from app.core.config import settings
from typing import AsyncGenerator
import httpx, json

async def stream_chat(provider: str, model: str, messages: list[dict], tools: list = None) -> AsyncGenerator[str, None]:
    """Stream chat completion from any provider. Yields text chunks."""
    if provider == "openai":
        yield from await _openai_stream(model, messages, settings.openai_api_key, "https://api.openai.com/v1", tools)
    elif provider == "anthropic":
        yield from await _anthropic_stream(model, messages, tools)
    elif provider == "google":
        yield from await _google_stream(model, messages)
    elif provider == "groq":
        yield from await _openai_stream(model, messages, settings.groq_api_key, "https://api.groq.com/openai/v1", tools)
    elif provider == "mistral":
        yield from await _openai_stream(model, messages, settings.mistral_api_key, "https://api.mistral.ai/v1", tools)
    elif provider == "together":
        yield from await _openai_stream(model, messages, settings.together_api_key, "https://api.together.xyz/v1", tools)
    elif provider == "fireworks":
        yield from await _openai_stream(model, messages, settings.fireworks_api_key, "https://api.fireworks.ai/inference/v1", tools)
    elif provider == "openrouter":
        yield from await _openai_stream(model, messages, settings.openrouter_api_key, "https://openrouter.ai/api/v1", tools)
    elif provider == "xai":
        yield from await _openai_stream(model, messages, settings.xai_api_key, "https://api.x.ai/v1", tools)
    elif provider == "deepseek":
        yield from await _openai_stream(model, messages, settings.deepseek_api_key, "https://api.deepseek.com/v1", tools)
    elif provider == "cohere":
        yield from await _cohere_stream(model, messages)
    elif provider in ("ollama", "lmstudio"):
        base = "http://localhost:11434/v1" if provider == "ollama" else "http://localhost:1234/v1"
        yield from await _openai_stream(model, messages, "local", base, tools)
    else:
        yield f"Unknown provider: {provider}"

async def _openai_stream(model, messages, api_key, base_url, tools=None) -> AsyncGenerator[str, None]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": model, "messages": messages, "stream": True}
    if tools:
        body["tools"] = tools
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", f"{base_url}/chat/completions", headers=headers, json=body) as r:
            async for line in r.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    try:
                        chunk = json.loads(line[6:])
                        delta = chunk["choices"][0]["delta"]
                        if "content" in delta and delta["content"]:
                            yield delta["content"]
                        # tool calls
                        if "tool_calls" in delta:
                            yield json.dumps({"tool_calls": delta["tool_calls"]})
                    except Exception:
                        pass

async def _anthropic_stream(model, messages, tools=None) -> AsyncGenerator[str, None]:
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    msgs = [m for m in messages if m["role"] != "system"]
    headers = {"x-api-key": settings.anthropic_api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
    body = {"model": model, "messages": msgs, "max_tokens": 8096, "stream": True}
    if system:
        body["system"] = system
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", "https://api.anthropic.com/v1/messages", headers=headers, json=body) as r:
            async for line in r.aiter_lines():
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:])
                        if data.get("type") == "content_block_delta":
                            yield data["delta"].get("text", "")
                    except Exception:
                        pass

async def _google_stream(model, messages) -> AsyncGenerator[str, None]:
    contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
                for m in messages if m["role"] != "system"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={settings.gemini_api_key}&alt=sse"
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", url, json={"contents": contents}) as r:
            async for line in r.aiter_lines():
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:])
                        yield data["candidates"][0]["content"]["parts"][0]["text"]
                    except Exception:
                        pass

async def _cohere_stream(model, messages) -> AsyncGenerator[str, None]:
    chat_history = [{"role": "USER" if m["role"] == "user" else "CHATBOT", "message": m["content"]}
                    for m in messages[:-1] if m["role"] != "system"]
    last = messages[-1]["content"]
    headers = {"Authorization": f"Bearer {settings.cohere_api_key}", "Content-Type": "application/json"}
    body = {"model": model, "message": last, "chat_history": chat_history, "stream": True}
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", "https://api.cohere.com/v1/chat", headers=headers, json=body) as r:
            async for line in r.aiter_lines():
                try:
                    data = json.loads(line)
                    if data.get("event_type") == "text-generation":
                        yield data.get("text", "")
                except Exception:
                    pass
