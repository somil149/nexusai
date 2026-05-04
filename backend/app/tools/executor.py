"""Agentic tools: file, shell, web search, code interpreter."""
import subprocess, os, json
from pathlib import Path
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import httpx

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Execute a shell command and return output",
            "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web and return results",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 5}}, "required": ["query"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch and extract text content from a URL",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Execute Python code and return output",
            "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files in a directory",
            "parameters": {"type": "object", "properties": {"path": {"type": "string", "default": "."}}, "required": []},
        },
    },
]

async def execute_tool(name: str, args: dict) -> str:
    try:
        if name == "read_file":
            return Path(args["path"]).read_text(encoding="utf-8", errors="ignore")
        elif name == "write_file":
            p = Path(args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"], encoding="utf-8")
            return f"Written {len(args['content'])} chars to {args['path']}"
        elif name == "run_shell":
            result = subprocess.run(args["command"], shell=True, capture_output=True, text=True, timeout=30)
            return (result.stdout + result.stderr).strip() or "(no output)"
        elif name == "web_search":
            results = list(DDGS().text(args["query"], max_results=args.get("max_results", 5)))
            return json.dumps([{"title": r["title"], "url": r["href"], "snippet": r["body"]} for r in results], indent=2)
        elif name == "fetch_url":
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                r = await client.get(args["url"], headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(r.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()
                return soup.get_text(separator="\n", strip=True)[:8000]
        elif name == "run_python":
            result = subprocess.run(["python", "-c", args["code"]], capture_output=True, text=True, timeout=30)
            return (result.stdout + result.stderr).strip() or "(no output)"
        elif name == "list_dir":
            path = args.get("path", ".")
            entries = list(Path(path).iterdir())
            return "\n".join(f"{'[DIR]' if e.is_dir() else '[FILE]'} {e.name}" for e in sorted(entries))
        else:
            return f"Unknown tool: {name}"
    except Exception as e:
        return f"Tool error: {e}"
