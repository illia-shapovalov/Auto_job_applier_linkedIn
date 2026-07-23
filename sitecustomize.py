from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "runAiBot.py"
MARKER = "# AUTO_JOB_ROLE_ROTATION_HOTFIX_V1"


def replace_once(text: str, old: str, new: str, description: str) -> str:
    count = text.count(old)

    if count == 0:
        if new in text:
            return text

        raise RuntimeError(
            f"Unable to apply role-rotation hotfix: {description}. "
            "The local runAiBot.py no longer matches the expected structure."
        )

    if count != 1:
        raise RuntimeError(
            f"Unable to apply role-rotation hotfix: {description} matched "
            f"{count} times instead of once."
        )

    return text.replace(old, new, 1)


def patch_run_ai_bot() -> None:
    if not TARGET.exists():
        return

    source = TARGET.read_text(encoding="utf-8-sig")

    if MARKER in source:
        return

    source = replace_once(
        source,
        "randomly_answered_questions = set()\n",
        "randomly_answered_questions = set()\n\n"
        "# Add AI roles that are realistic extensions of the candidate's\n"
        "# full-stack, .NET, DevOps, automation, and LLM integration profile.\n"
        "AI_SEARCH_TERMS = [\n"
        "    'AI Application Developer',\n"
        "    'AI Software Engineer',\n"
        "    'Generative AI Developer',\n"
        "    'LLM Application Developer',\n"
        "    'AI Integration Developer',\n"
        "    'AI Automation Engineer',\n"
        "]\n\n"
        "for ai_search_term in AI_SEARCH_TERMS:\n"
        "    if not any(\n"
        "        existing.casefold() == ai_search_term.casefold()\n"
        "        for existing in search_terms\n"
        "    ):\n"
        "        search_terms.append(ai_search_term)\n\n"
        "print_lg(\n"
        "    'Configured rotating search terms: ',\n"
        "    search_terms,\n"
        ")\n",
        "AI search term extension",
    )

    source = replace_once(
        source,
        "        current_count = 0\n"
        "        try:\n"
        "            while current_count < switch_number:\n",
        "        current_count = 0\n"
        "        role_attempt_count = 0\n"
        "        try:\n"
        "            while role_attempt_count < switch_number:\n",
        "per-role attempt counter",
    )

    source = replace_once(
        source,
        "                    if current_count >= switch_number: break\n",
        "                    if role_attempt_count >= switch_number:\n"
        "                        print_lg(\n"
        "                            f'Rotating away from {searchTerm!r} after '\n"
        "                            f'{role_attempt_count} new application attempts.'\n"
        "                        )\n"
        "                        break\n",
        "role rotation break condition",
    )

    source = replace_once(
        source,
        "                    job_link = \"https://www.linkedin.com/jobs/view/\"+job_id\n",
        "                    role_attempt_count += 1\n"
        "                    print_lg(\n"
        "                        'ROLE ATTEMPT | '\n"
        "                        f'search={searchTerm!r} | '\n"
        "                        f'attempt={role_attempt_count}/{switch_number} | '\n"
        "                        f'title={title!r} | company={company!r}'\n"
        "                    )\n\n"
        "                    job_link = \"https://www.linkedin.com/jobs/view/\"+job_id\n",
        "new-application attempt increment",
    )

    source = source.replace(
        "\n\nif __name__ == \"__main__\":\n",
        f"\n\n{MARKER}\nif __name__ == \"__main__\":\n",
        1,
    )

    TARGET.write_text(source, encoding="utf-8", newline="\n")
    print(
        "Applied AI search-term and role-rotation hotfix. "
        "This run will use the updated behavior."
    )


patch_run_ai_bot()
