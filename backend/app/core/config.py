from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # LLM
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qualiprompt-engine")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "120"))

    # Validador
    VALIDATION_PASS_THRESHOLD: float = 80.0
    VALIDATION_MAX_ITERATIONS: int = 3

    # Memoria
    MEMORY_EXPLORE_RATIO: float = 0.2

    # Model
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "qwen2.5:14b-q5")

    # Admin
    ADMIN_TOKEN: str = os.getenv("ADMIN_TOKEN", "qualiprompt-admin-default")

    class Config:
        env_file = ".env"


settings = Settings()
