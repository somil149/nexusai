#!/usr/bin/env python3
"""NexusAI CLI - chat, run tasks, and manage agents from the terminal."""
import asyncio, sys, json, os
import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich import print as rprint

console = Console()
BASE = os.getenv("NEXUS_API", "http://localhost:8000")

async def get_providers():
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/api/models")
        return r.json()

async def pick_model():
    providers = await get_providers()
    table = Table(title="Available Models", show_lines=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Provider", style="green")
    table.add_column("Model", style="white")
    table.add_column("Type", style="yellow")

    options = []
    for p in providers:
        for m in p["models"]:
            options.append((p["provider"], m))
            table.add_row(str(len(options)), p["provider"], m, "local" if p.get("local") else "cloud")

    console.print(table)
    choice = Prompt.ask("Select model #", default="1")
    idx = int(choice) - 1
    if 0 <= idx < len(options):
        return options[idx]
    return options[0]

async def stream_chat_ws(session_id: str, provider: str, model: str, message: str, use_tools: bool = True):
    import websockets
    uri = f"ws://localhost:8000/ws/chat/{session_id}"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"provider": provider, "model": model, "message": message, "use_tools": use_tools}))
        full = ""
        async for msg in ws:
            data = json.loads(msg)
            if data["type"] == "chunk":
                console.print(data["content"], end="", markup=False)
                full += data["content"]
            elif data["type"] == "done":
                break
            elif data["type"] == "error":
                console.print(f"\n[red]Error: {data['content']}[/red]")
                break
        console.print()
        return full

async def create_session():
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{BASE}/api/sessions")
        return r.json()["id"]

async def cmd_chat(args):
    """Interactive chat session."""
    provider, model = await pick_model()
    console.print(f"\n[green]Using {provider}/{model}[/green] — type 'exit' to quit, '/tools off' to disable tools\n")

    session_id = await create_session()
    use_tools = True

    while True:
        try:
            user_input = Prompt.ask("[blue]You[/blue]")
        except (KeyboardInterrupt, EOFError):
            break

        if user_input.lower() in ("exit", "quit", "q"):
            break
        if user_input == "/tools off":
            use_tools = False
            console.print("[yellow]Tools disabled[/yellow]")
            continue
        if user_input == "/tools on":
            use_tools = True
            console.print("[green]Tools enabled[/green]")
            continue
        if user_input.startswith("/model"):
            provider, model = await pick_model()
            continue

        console.print("[dim cyan]NexusAI:[/dim cyan] ", end="")
        await stream_chat_ws(session_id, provider, model, user_input, use_tools)

async def cmd_run(args):
    """One-shot agentic task."""
    task = " ".join(args) if args else Prompt.ask("Task")
    provider, model = await pick_model()
    session_id = await create_session()
    console.print(f"\n[dim]Running task with {provider}/{model}...[/dim]\n")
    result = await stream_chat_ws(session_id, provider, model, task, use_tools=True)
    console.print(Markdown(result))

async def cmd_models(args):
    """List all available models."""
    providers = await get_providers()
    for p in providers:
        icon = "🖥" if p.get("local") else "☁"
        console.print(f"\n{icon} [bold green]{p['provider']}[/bold green]")
        for m in p["models"]:
            console.print(f"   • {m}")

async def cmd_cost(args):
    """Show API cost breakdown."""
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/api/cost")
        data = r.json()
    if not data:
        console.print("[yellow]No usage recorded yet.[/yellow]")
        return
    table = Table(title="💰 API Cost Tracker")
    table.add_column("Provider", style="green")
    table.add_column("Input Tokens", justify="right")
    table.add_column("Output Tokens", justify="right")
    table.add_column("Cost (USD)", justify="right", style="yellow")
    total = 0
    for r in data:
        table.add_row(r["provider"], str(r["input_tokens"]), str(r["output_tokens"]), f"${r['cost_usd']:.4f}")
        total += r["cost_usd"]
    table.add_row("[bold]TOTAL[/bold]", "", "", f"[bold]${total:.4f}[/bold]")
    console.print(table)

COMMANDS = {"chat": cmd_chat, "run": cmd_run, "models": cmd_models, "cost": cmd_cost}

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "chat"
    rest = args[1:]

    if cmd not in COMMANDS:
        console.print(f"[red]Unknown command: {cmd}[/red]")
        console.print("Commands: " + ", ".join(COMMANDS.keys()))
        sys.exit(1)

    asyncio.run(COMMANDS[cmd](rest))

if __name__ == "__main__":
    main()
