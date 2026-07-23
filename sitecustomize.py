from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "runAiBot.py"
MARKER = "# AUTO_JOB_ROLE_ROTATION_HOTFIX_V2"


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

    # Fresh checkout: add the realistic AI-oriented search terms.
    if "AI_SEARCH_TERMS = [" not in source:
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

    # Upgrade the V1 attempt-based counter if it is already present locally.
    if "role_attempt_count = 0" in source:
        source = replace_once(
            source,
            "        current_count = 0\n"
            "        role_attempt_count = 0\n"
            "        try:\n"
            "            while role_attempt_count < switch_number:\n",
            "        current_count = 0\n"
            "        role_attempt_count = 0\n"
            "        role_failed_total = 0\n"
            "        role_failed_consecutive = 0\n"
            "        previous_attempt_pending = False\n"
            "        try:\n"
            "            while True:\n",
            "success-driven role counters",
        )

        source = replace_once(
            source,
            "                    if role_attempt_count >= switch_number:\n"
            "                        print_lg(\n"
            "                            f'Rotating away from {searchTerm!r} after '\n"
            "                            f'{role_attempt_count} new application attempts.'\n"
            "                        )\n"
            "                        break\n",
            "                    if previous_attempt_pending:\n"
            "                        role_failed_total += 1\n"
            "                        role_failed_consecutive += 1\n"
            "                        previous_attempt_pending = False\n"
            "                        print_lg(\n"
            "                            'ROLE FAILURE | '\n"
            "                            f'search={searchTerm!r} | '\n"
            "                            f'consecutive={role_failed_consecutive}/6 | '\n"
            "                            f'total={role_failed_total}/20 | '\n"
            "                            f'successes={current_count}/{switch_number}'\n"
            "                        )\n"
            "\n"
            "                    rotation_reason = None\n"
            "                    if current_count >= switch_number:\n"
            "                        rotation_reason = (\n"
            "                            f'{current_count} successful applications '\n"
            "                            f'(target={switch_number})'\n"
            "                        )\n"
            "                    elif role_failed_consecutive >= 6:\n"
            "                        rotation_reason = (\n"
            "                            '6 consecutive unsuccessful applications'\n"
            "                        )\n"
            "                    elif role_failed_total >= 20:\n"
            "                        rotation_reason = (\n"
            "                            '20 total unsuccessful applications'\n"
            "                        )\n"
            "\n"
            "                    if rotation_reason is not None:\n"
            "                        print_lg(\n"
            "                            f'ROTATING SEARCH ROLE | '\n"
            "                            f'search={searchTerm!r} | '\n"
            "                            f'reason={rotation_reason!r} | '\n"
            "                            f'successes={current_count} | '\n"
            "                            f'failures={role_failed_total}'\n"
            "                        )\n"
            "                        break\n",
            "success and failure rotation conditions",
        )

        source = replace_once(
            source,
            "                    role_attempt_count += 1\n"
            "                    print_lg(\n"
            "                        'ROLE ATTEMPT | '\n"
            "                        f'search={searchTerm!r} | '\n"
            "                        f'attempt={role_attempt_count}/{switch_number} | '\n"
            "                        f'title={title!r} | company={company!r}'\n"
            "                    )\n\n",
            "                    role_attempt_count += 1\n"
            "                    previous_attempt_pending = True\n"
            "                    print_lg(\n"
            "                        'ROLE ATTEMPT | '\n"
            "                        f'search={searchTerm!r} | '\n"
            "                        f'attempt={role_attempt_count} | '\n"
            "                        f'successes={current_count}/{switch_number} | '\n"
            "                        f'consecutive_failures={role_failed_consecutive}/6 | '\n"
            "                        f'total_failures={role_failed_total}/20 | '\n"
            "                        f'title={title!r} | company={company!r}'\n"
            "                    )\n\n",
            "pending attempt tracking",
        )
    else:
        # Fresh checkout without V1: patch the original loop directly.
        source = replace_once(
            source,
            "        current_count = 0\n"
            "        try:\n"
            "            while current_count < switch_number:\n",
            "        current_count = 0\n"
            "        role_attempt_count = 0\n"
            "        role_failed_total = 0\n"
            "        role_failed_consecutive = 0\n"
            "        previous_attempt_pending = False\n"
            "        try:\n"
            "            while True:\n",
            "fresh success-driven role counters",
        )

        source = replace_once(
            source,
            "                    if current_count >= switch_number: break\n",
            "                    if previous_attempt_pending:\n"
            "                        role_failed_total += 1\n"
            "                        role_failed_consecutive += 1\n"
            "                        previous_attempt_pending = False\n"
            "\n"
            "                    if (\n"
            "                        current_count >= switch_number\n"
            "                        or role_failed_consecutive >= 6\n"
            "                        or role_failed_total >= 20\n"
            "                    ):\n"
            "                        break\n",
            "fresh rotation conditions",
        )

        source = replace_once(
            source,
            "                    job_link = \"https://www.linkedin.com/jobs/view/\"+job_id\n",
            "                    role_attempt_count += 1\n"
            "                    previous_attempt_pending = True\n"
            "                    job_link = \"https://www.linkedin.com/jobs/view/\"+job_id\n",
            "fresh pending attempt tracking",
        )

    # A successful submission clears the pending failure and resets the streak.
    source = replace_once(
        source,
        "                    current_count += 1\n"
        "                    if application_link == \"Easy Applied\": easy_applied_count += 1\n",
        "                    current_count += 1\n"
        "                    previous_attempt_pending = False\n"
        "                    role_failed_consecutive = 0\n"
        "                    print_lg(\n"
        "                        'ROLE SUCCESS | '\n"
        "                        f'search={searchTerm!r} | '\n"
        "                        f'successes={current_count}/{switch_number} | '\n"
        "                        f'total_failures={role_failed_total}/20'\n"
        "                    )\n"
        "                    if application_link == \"Easy Applied\": easy_applied_count += 1\n",
        "successful application accounting",
    )

    source = source.replace(
        "# AUTO_JOB_ROLE_ROTATION_HOTFIX_V1\n",
        "",
        1,
    )

    source = source.replace(
        "\n\nif __name__ == \"__main__\":\n",
        f"\n\n{MARKER}\nif __name__ == \"__main__\":\n",
        1,
    )

    TARGET.write_text(source, encoding="utf-8", newline="\n")
    print(
        "Applied success-based role rotation: target successful applications, "
        "6 consecutive failures, or 20 total failures per search."
    )


patch_run_ai_bot()
