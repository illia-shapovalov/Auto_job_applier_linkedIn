"""
Load private credentials and AI settings from the repository's root .env file.

The .env file must remain untracked and must never be committed.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


def get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    normalized = value.strip().lower()

    if normalized in {"1", "true", "yes", "on"}:
        return True

    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        f"Environment variable {name} must be true or false; "
        f"received {value!r}"
    )


username = os.getenv("LINKEDIN_USERNAME", "")
password = os.getenv("LINKEDIN_PASSWORD", "")

use_AI = get_bool("USE_AI", False)

ai_provider = os.getenv("AI_PROVIDER", "openai")
llm_api_url = os.getenv(
    "LLM_API_URL",
    "https://api.openai.com/v1/",
)
llm_api_key = os.getenv("LLM_API_KEY", "not-needed")
llm_model = os.getenv("LLM_MODEL", "gpt-5-mini")
llm_spec = os.getenv("LLM_SPEC", "openai")

stream_output = get_bool("STREAM_OUTPUT", False)


if not username:
    raise RuntimeError(
        "LINKEDIN_USERNAME is missing from the root .env file."
    )

if not password:
    raise RuntimeError(
        "LINKEDIN_PASSWORD is missing from the root .env file."
    )
