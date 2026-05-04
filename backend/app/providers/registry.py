"""Dynamic provider registry - discovers available models from all configured providers."""
from app.core.config import settings
from typing import Any
import httpx

PROVIDER_MODELS = {
    "openai": {
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1", "o1-mini", "o3-mini"],
        "cost_per_1k": {"gpt-4o": (0.0025, 0.01), "gpt-4o-mini": (0.00015, 0.0006), "o1": (0.015, 0.06), "o3-mini": (0.0011, 0.0044)},
    },
    "anthropic": {
        "models": ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-3-5"],
        "cost_per_1k": {"claude-opus-4-5": (0.015, 0.075), "claude-sonnet-4-5": (0.003, 0.015), "claude-haiku-3-5": (0.0008, 0.004)},
    },
    "google": {
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "cost_per_1k": {"gemini-2.0-flash": (0.0001, 0.0004), "gemini-1.5-pro": (0.00125, 0.005), "gemini-1.5-flash": (0.000075, 0.0003)},
    },
    "groq": {
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
        "cost_per_1k": {"llama-3.3-70b-versatile": (0.00059, 0.00079), "llama-3.1-8b-instant": (0.00005, 0.00008)},
    },
    "mistral": {
        "models": ["mistral-large-latest", "mistral-small-latest", "codestral-latest", "open-mistral-nemo"],
        "cost_per_1k": {"mistral-large-latest": (0.002, 0.006), "mistral-small-latest": (0.0002, 0.0006)},
    },
    "cohere": {
        "models": ["command-r-plus", "command-r", "command-light"],
        "cost_per_1k": {"command-r-plus": (0.003, 0.015), "command-r": (0.00015, 0.0006)},
    },
    "together": {
        "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "meta-llama/Llama-3.2-3B-Instruct-Turbo", "Qwen/Qwen2.5-72B-Instruct-Turbo"],
        "cost_per_1k": {"meta-llama/Llama-3.3-70B-Instruct-Turbo": (0.00088, 0.00088)},
    },
    "fireworks": {
        "models": ["accounts/fireworks/models/llama-v3p3-70b-instruct", "accounts/fireworks/models/qwen2p5-72b-instruct"],
        "cost_per_1k": {"accounts/fireworks/models/llama-v3p3-70b-instruct": (0.0009, 0.0009)},
    },
    "openrouter": {
        "models": ["openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-2.0-flash", "meta-llama/llama-3.3-70b-instruct", "deepseek/deepseek-r1"],
        "cost_per_1k": {},
    },
    "xai": {
        "models": ["grok-2-latest", "grok-2-vision-latest"],
        "cost_per_1k": {"grok-2-latest": (0.002, 0.01)},
    },
    "deepseek": {
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "cost_per_1k": {"deepseek-chat": (0.00014, 0.00028), "deepseek-reasoner": (0.00055, 0.00219)},
    },
    "ollama": {
        "models": [],  # discovered dynamically
        "cost_per_1k": {},
    },
}

KEY_MAP = {
    "openai": settings.openai_api_key,
    "anthropic": settings.anthropic_api_key,
    "google": settings.gemini_api_key,
    "groq": settings.groq_api_key,
    "mistral": settings.mistral_api_key,
    "cohere": settings.cohere_api_key,
    "together": settings.together_api_key,
    "fireworks": settings.fireworks_api_key,
    "openrouter": settings.openrouter_api_key,
    "xai": settings.xai_api_key,
    "deepseek": settings.deepseek_api_key,
    "ollama": "local",
}

async def get_ollama_models() -> list[str]:
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get("http://localhost:11434/api/tags")
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []

async def get_lmstudio_models() -> list[str]:
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get("http://localhost:1234/v1/models")
            return [m["id"] for m in r.json().get("data", [])]
    except Exception:
        return []

async def discover_providers() -> list[dict]:
    """Return all available providers with their models."""
    result = []

    # Ollama local
    ollama_models = await get_ollama_models()
    if ollama_models:
        result.append({"provider": "ollama", "models": ollama_models, "local": True})

    # LM Studio local
    lmstudio_models = await get_lmstudio_models()
    if lmstudio_models:
        result.append({"provider": "lmstudio", "models": lmstudio_models, "local": True})

    # Cloud providers
    for provider, info in PROVIDER_MODELS.items():
        if provider == "ollama":
            continue
        key = KEY_MAP.get(provider, "")
        if key:
            result.append({
                "provider": provider,
                "models": info["models"],
                "local": False,
                "cost_per_1k": info.get("cost_per_1k", {}),
            })

    return result

def get_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    costs = PROVIDER_MODELS.get(provider, {}).get("cost_per_1k", {})
    if model in costs:
        in_cost, out_cost = costs[model]
        return (input_tokens / 1000 * in_cost) + (output_tokens / 1000 * out_cost)
    return 0.0
