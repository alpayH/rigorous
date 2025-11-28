import os
from pathlib import Path

from dotenv import load_dotenv

MODULE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = MODULE_ROOT.parent

# Load env vars from the module folder first, then fall back to repo root.
load_dotenv(MODULE_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env")

class Config:
    """Holds runtime settings for the RiskHeuristicAgent."""

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("AGENT2_MODEL_NAME", "gpt-5-nano")

    @classmethod
    def require_api_key(cls) -> str:
        """Return the API key or raise a clear error if missing."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")
        return cls.OPENAI_API_KEY
