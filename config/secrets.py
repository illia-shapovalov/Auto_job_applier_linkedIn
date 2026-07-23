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



def get_int(
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    raw_value = os.getenv(name)

    if raw_value is None or not raw_value.strip():
        return default

    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValueError(
            f"{name} must be an integer."
        ) from error

    if not minimum <= value <= maximum:
        raise ValueError(
            f"{name} must be between {minimum} and {maximum}."
        )

    return value


def get_float(
    name: str,
    default: float,
    minimum: float = 0,
) -> float:
    raw_value = os.getenv(name)

    if raw_value is None or not raw_value.strip():
        return default

    try:
        value = float(raw_value)
    except ValueError as error:
        raise ValueError(
            f"{name} must be numeric."
        ) from error

    if value < minimum:
        raise ValueError(
            f"{name} must be at least {minimum}."
        )

    return value


def get_csv(name: str) -> list[str]:
    raw_value = os.getenv(name, "")

    return [
        value.strip()
        for value in raw_value.split(",")
        if value.strip()
    ]


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



ai_assertiveness = get_int(
    "AI_ASSERTIVENESS",
    default=1,
    minimum=0,
    maximum=3,
)

total_relevant_experience_years = get_float(
    "TOTAL_RELEVANT_EXPERIENCE_YEARS",
    default=0,
)

canadian_citizen = get_bool(
    "CANADIAN_CITIZEN",
    False,
)

ukrainian_citizen = get_bool(
    "UKRAINIAN_CITIZEN",
    False,
)

authorized_to_work_in_canada = get_bool(
    "AUTHORIZED_TO_WORK_IN_CANADA",
    False,
)

requires_canada_sponsorship = get_bool(
    "REQUIRES_CANADA_SPONSORSHIP",
    True,
)

degree_level = os.getenv(
    "DEGREE_LEVEL",
    "",
).strip()

degree_status = os.getenv(
    "DEGREE_STATUS",
    "",
).strip()

degree_field = os.getenv(
    "DEGREE_FIELD",
    "",
).strip()

formal_security_clearance = os.getenv(
    "FORMAL_SECURITY_CLEARANCE",
    "none",
).strip()

handled_confidential_information = get_bool(
    "HANDLED_CONFIDENTIAL_INFORMATION",
    False,
)

criminal_record = get_bool(
    "CRIMINAL_RECORD",
    False,
)

available_immediately = get_bool(
    "AVAILABLE_IMMEDIATELY",
    False,
)

salary_strategy = os.getenv(
    "SALARY_STRATEGY",
    "configured",
).strip()

salary_premium_percent = get_float(
    "SALARY_PREMIUM_PERCENT",
    default=0,
)

salary_round_to = get_int(
    "SALARY_ROUND_TO",
    default=1000,
    minimum=1,
    maximum=100000,
)

certifications_held = get_csv(
    "CERTIFICATIONS_HELD"
)

certifications_in_progress = get_csv(
    "CERTIFICATIONS_IN_PROGRESS"
)

certifications_willing_to_obtain = get_csv(
    "CERTIFICATIONS_WILLING_TO_OBTAIN"
)


def build_application_profile_context() -> str:
    citizenships = []

    if canadian_citizen:
        citizenships.append("Canadian")

    if ukrainian_citizen:
        citizenships.append("Ukrainian")

    lines = [
        (
            "Total broad relevant technical experience: "
            f"{total_relevant_experience_years:g} years."
        ),
        (
            "Citizenship: "
            + (
                ", ".join(citizenships)
                if citizenships
                else "Not specified"
            )
            + "."
        ),
        (
            "Authorized to work in Canada: "
            f"{authorized_to_work_in_canada}."
        ),
        (
            "Requires employer sponsorship in Canada: "
            f"{requires_canada_sponsorship}."
        ),
        (
            "Education level: "
            f"{degree_level or 'Not specified'}."
        ),
        (
            "Degree status: "
            f"{degree_status or 'Not specified'}."
        ),
        (
            "Degree field: "
            f"{degree_field or 'Not specified'}."
        ),
        (
            "Formal security clearance: "
            f"{formal_security_clearance or 'none'}."
        ),
        (
            "Has handled confidential information: "
            f"{handled_confidential_information}."
        ),
        (
            "Has a criminal record: "
            f"{criminal_record}."
        ),
        (
            "Available immediately: "
            f"{available_immediately}."
        ),
        (
            "Certifications currently held: "
            + (
                ", ".join(certifications_held)
                if certifications_held
                else "None specified"
            )
            + "."
        ),
        (
            "Certifications in progress: "
            + (
                ", ".join(certifications_in_progress)
                if certifications_in_progress
                else "None specified"
            )
            + "."
        ),
        (
            "Certifications willing to obtain: "
            + (
                ", ".join(
                    certifications_willing_to_obtain
                )
                if certifications_willing_to_obtain
                else "None specified"
            )
            + "."
        ),
    ]

    return "\n".join(lines)


application_profile_context = (
    build_application_profile_context()
)


if not username:
    raise RuntimeError(
        "LINKEDIN_USERNAME is missing from the root .env file."
    )

if not password:
    raise RuntimeError(
        "LINKEDIN_PASSWORD is missing from the root .env file."
    )
