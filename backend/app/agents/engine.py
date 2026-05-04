"""Multi-agent engine - run parallel/sequential agent pipelines."""
from app.providers.client import stream_chat
from app.tools.executor import execute_tool, TOOLS_SCHEMA
from typing import AsyncGenerator
import json, asyncio

async def run_agent(role: str, goal: str, task: str, provider: str, model: str,
                    context: str = "", use_tools: bool = True) -> AsyncGenerator[str, None]:
    """Run a single agent with a role, goal and task."""
    system = f"You are a {role}. Your goal: {goal}\nBe concise and focused on your specific role."
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"{context}\n\nTask: {task}" if context else task},
    ]
    tools = TOOLS_SCHEMA if use_tools else None
    full_response = ""

    async for chunk in stream_chat(provider, model, messages, tools):
        # Handle tool calls
        if chunk.startswith('{"tool_calls"'):
            try:
                data = json.loads(chunk)
                for tc in data["tool_calls"]:
                    fn = tc["function"]["name"]
                    args = json.loads(tc["function"]["arguments"])
                    yield f"\n🔧 **{fn}**({json.dumps(args, ensure_ascii=False)[:100]})\n"
                    result = await execute_tool(fn, args)
                    yield f"```\n{result[:500]}\n```\n"
                    messages.append({"role": "assistant", "content": chunk})
                    messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
                    # Continue after tool use
                    async for c in stream_chat(provider, model, messages):
                        yield c
            except Exception as e:
                yield f"Tool error: {e}"
        else:
            full_response += chunk
            yield chunk

async def run_crew(agents: list[dict], task: str) -> AsyncGenerator[str, None]:
    """
    Run a multi-agent crew sequentially, passing output as context to next agent.
    agents: [{"role": str, "goal": str, "provider": str, "model": str}]
    """
    context = ""
    for i, agent in enumerate(agents):
        yield f"\n\n---\n### 🤖 Agent {i+1}: {agent['role']}\n"
        agent_output = ""
        async for chunk in run_agent(
            role=agent["role"],
            goal=agent["goal"],
            task=task,
            provider=agent["provider"],
            model=agent["model"],
            context=context,
        ):
            agent_output += chunk
            yield chunk
        context = f"Previous agent ({agent['role']}) output:\n{agent_output}\n"

    yield "\n\n---\n✅ **Crew task complete.**\n"
