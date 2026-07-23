import csv
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


form_action_delay_seconds = get_float(
    "FORM_ACTION_DELAY_SECONDS",
    default=0.75,
    minimum=0,
)

form_step_delay_seconds = get_float(
    "FORM_STEP_DELAY_SECONDS",
    default=2.0,
    minimum=0,
)



technology_mastery_file = os.getenv(
    "TECHNOLOGY_MASTERY_FILE",
    "config/technologies_mastering.csv",
).strip()


def load_technology_mastery_context() -> str:
    csv_path = Path(technology_mastery_file)

    if not csv_path.is_absolute():
        csv_path = (
            Path(__file__).resolve().parent.parent
            / csv_path
        )

    if not csv_path.exists():
        return (
            "Technology mastery file not found: "
            f"{csv_path}"
        )

    entries = []

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.reader(file))

    for row in rows:
        values = [
            value.strip()
            for value in row
        ]

        if not values or not any(values):
            continue

        technology = values[0] if len(values) >= 1 else ""
        mastery = values[1] if len(values) >= 2 else ""
        notes = values[2] if len(values) >= 3 else ""

        if not technology:
            continue

        # Ignore obvious header rows.
        normalized_name = technology.casefold()

        if normalized_name in {
            "technology",
            "technologies",
            "technology name",
            "name",
        }:
            continue

        if not mastery and not notes:
            continue

        entry = f"- {technology}"

        if mastery:
            entry += f": mastery {mastery}/10"

        if notes:
            entry += f"; {notes}"

        entries.append(entry)

    if not entries:
        return (
            "Technology mastery CSV was loaded, "
            "but no technology entries were recognized."
        )

    return "\n".join(
        [
            "Verified technology mastery profile:",
            *entries,
        ]
    )


technology_mastery_context = (
    load_technology_mastery_context()
)



language_french_level = os.getenv(
    "LANGUAGE_FRENCH_LEVEL",
    "",
).strip()

language_english_level = os.getenv(
    "LANGUAGE_ENGLISH_LEVEL",
    "",
).strip()

language_ukrainian_level = os.getenv(
    "LANGUAGE_UKRAINIAN_LEVEL",
    "",
).strip()

language_russian_level = os.getenv(
    "LANGUAGE_RUSSIAN_LEVEL",
    "",
).strip()


def build_language_profile_context() -> str:
    languages = [
        ("French", language_french_level),
        ("English", language_english_level),
        ("Ukrainian", language_ukrainian_level),
        ("Russian", language_russian_level),
    ]

    lines = [
        "Verified language proficiency:"
    ]

    for language, level in languages:
        if level:
            lines.append(
                f"- {language}: {level}"
            )

    return "\n".join(lines)


language_profile_context = (
    build_language_profile_context()
)


preferred_application_email = os.getenv(
    "PREFERRED_APPLICATION_EMAIL",
    "",
).strip()


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

    lines.extend(
        [
            "",
            language_profile_context,
            "",
            technology_mastery_context,
        ]
    )

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
