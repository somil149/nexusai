from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    mistral_api_key: str = ""
    cohere_api_key: str = ""
    together_api_key: str = ""
    fireworks_api_key: str = ""
    openrouter_api_key: str = ""
    xai_api_key: str = ""
    deepseek_api_key: str = ""
    huggingface_api_key: str = ""

    # App
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/db/nexusai.db"
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    chroma_dir: str = str(BASE_DIR / "data" / "chroma")

    class Config:
        env_file = str(Path.home() / ".ai-keys" / ".env")
        extra = "ignore"

settings = Settings()
