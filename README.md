# NexusAI — Personal Agentic AI Platform

## Features
- 🌐 **12 AI providers** — OpenAI, Anthropic, Google, Groq, Mistral, Cohere, Together, Fireworks, OpenRouter, xAI, DeepSeek + local Ollama/LM Studio
- 🔄 **Dynamic model switching** — change provider/model mid-conversation
- 🛠 **Agentic tools** — file read/write, shell execution, web search, Python interpreter
- 📄 **RAG** — upload PDFs/docs and chat with them
- 🤖 **Multi-agent crews** — assign roles to different models, run pipelines
- 🎙 **Voice** — mic input + TTS output
- 💰 **Cost tracker** — token usage and cost per provider
- 🖥 **Web UI** + **CLI**

## Quick Start

```powershell
# Install backend
cd C:\shared\projects\nexusai\backend
conda activate aitools
pip install -r requirements.txt

# Start everything
C:\shared\projects\nexusai\start.ps1
```

## URLs
- Web UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## CLI
```powershell
python cli/nexus.py chat              # interactive chat
python cli/nexus.py run "your task"   # one-shot agentic task
python cli/nexus.py models            # list all models
python cli/nexus.py cost              # show cost breakdown
```

## Add `nexus` as a global command
Add to your PowerShell profile:
```powershell
function nexus { conda run -n aitools python C:\shared\projects\nexusai\cli\nexus.py @args }
```
