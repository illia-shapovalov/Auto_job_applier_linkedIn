from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "runAiBot.py"
MARKER = "# AUTO_JOB_RUNTIME_HOTFIX_V2"


def _replace_once(
    text: str,
    old: str,
    new: str,
    description: str,
) -> str:
    count = text.count(old)

    if count == 0:
        if new in text:
            return text

        raise RuntimeError(
            f"Runtime patch target not found: {description}"
        )

    if count != 1:
        raise RuntimeError(
            f"Runtime patch target {description!r} matched "
            f"{count} times instead of once."
        )

    return text.replace(old, new, 1)


def apply_runtime_hotfix() -> bool:
    """Patch runAiBot.py once and return True when a restart is required."""
    if not TARGET.exists():
        raise RuntimeError(f"Could not find {TARGET}")

    source = TARGET.read_text(encoding="utf-8-sig")

    if MARKER in source:
        return False

    source = _replace_once(
        source,
        "    form_step_delay_seconds,\n)",
        "    form_step_delay_seconds,\n"
        "    preferred_application_email,\n"
        ")",
        "preferred application email import",
    )

    source = _replace_once(
        source,
        "from modules.validator import validate_config\n",
        "from modules.validator import validate_config\n"
        "from modules.single_instance import (\n"
        "    acquire_instance_lock,\n"
        "    release_instance_lock,\n"
        ")\n",
        "single-instance imports",
    )

    source = _replace_once(
        source,
        "def wait_after_form_action(\n",
        "def resolve_adjacent_technology_years(\n"
        "    question: str,\n"
        ") -> str | None:\n"
        "    \"\"\"Return a conservative configured-years estimate for close stack relatives.\"\"\"\n"
        "    normalized = question.casefold()\n"
        "    year_terms = (\n"
        "        'year',\n"
        "        'years',\n"
        "        'année',\n"
        "        'années',\n"
        "        ' ans',\n"
        "    )\n"
        "\n"
        "    if not any(term in normalized for term in year_terms):\n"
        "        return None\n"
        "\n"
        "    adjacent_factors = {\n"
        "        'blazor': 0.60,\n"
        "        '.net maui': 0.50,\n"
        "        'maui': 0.50,\n"
        "    }\n"
        "\n"
        "    matched_technology = next(\n"
        "        (\n"
        "            technology\n"
        "            for technology in adjacent_factors\n"
        "            if technology in normalized\n"
        "        ),\n"
        "        None,\n"
        "    )\n"
        "\n"
        "    if matched_technology is None:\n"
        "        return None\n"
        "\n"
        "    try:\n"
        "        configured_years = max(\n"
        "            0,\n"
        "            int(float(years_of_experience)),\n"
        "        )\n"
        "    except (TypeError, ValueError):\n"
        "        return None\n"
        "\n"
        "    if configured_years <= 0:\n"
        "        return '0'\n"
        "\n"
        "    derived_years = max(\n"
        "        1,\n"
        "        min(\n"
        "            configured_years,\n"
        "            int(configured_years * adjacent_factors[matched_technology]),\n"
        "        ),\n"
        "    )\n"
        "\n"
        "    print_lg(\n"
        "        'DETERMINISTIC ADJACENT YEARS ANSWER | '\n"
        "        f'question={question!r} | '\n"
        "        f'technology={matched_technology!r} | '\n"
        "        f'configured_years={configured_years!r} | '\n"
        "        f'answer={derived_years!r} | '\n"
        "        \"reason='Conservative estimate from the configured C#/.NET stack experience'\"\n"
        "    )\n"
        "\n"
        "    return str(derived_years)\n"
        "\n"
        "\n"
        "def wait_after_form_action(\n",
        "adjacent technology years resolver",
    )

    source = _replace_once(
        source,
        "            prev_answer = selected_option\n\n"
        "            deterministic_language_answer = (\n",
        "            prev_answer = selected_option\n\n"
        "            deterministic_email_answer = None\n"
        "            email_terms = (\n"
        "                'email',\n"
        "                'e-mail',\n"
        "                'courriel',\n"
        "            )\n"
        "\n"
        "            if (\n"
        "                preferred_application_email\n"
        "                and any(term in label for term in email_terms)\n"
        "            ):\n"
        "                deterministic_email_answer = next(\n"
        "                    (\n"
        "                        option\n"
        "                        for option in optionsText\n"
        "                        if option.strip().casefold()\n"
        "                        == preferred_application_email.casefold()\n"
        "                    ),\n"
        "                    None,\n"
        "                )\n"
        "\n"
        "                if deterministic_email_answer is None:\n"
        "                    raise UnresolvedApplicationQuestion(\n"
        "                        label_org,\n"
        "                        'single_select',\n"
        "                        'Configured preferred application email was not available. '\n"
        "                        f'preferred={preferred_application_email!r}; '\n"
        "                        f'options={optionsText!r}',\n"
        "                    )\n"
        "\n"
        "                print_lg(\n"
        "                    'DETERMINISTIC EMAIL ANSWER | '\n"
        "                    f'question={label_org!r} | '\n"
        "                    f'answer={deterministic_email_answer!r} | '\n"
        "                    f'previous={selected_option!r}'\n"
        "                )\n"
        "\n"
        "            deterministic_language_answer = (\n",
        "deterministic preferred email resolver",
    )

    source = _replace_once(
        source,
        "                or deterministic_language_answer is not None\n"
        "            )",
        "                or deterministic_language_answer is not None\n"
        "                or deterministic_email_answer is not None\n"
        "            )",
        "preferred email overwrite condition",
    )

    source = _replace_once(
        source,
        "                if deterministic_language_answer is not None:\n"
        "                    answer = deterministic_language_answer\n"
        "                elif 'email' in label or 'phone' in label:\n"
        "                    answer = prev_answer\n",
        "                if deterministic_email_answer is not None:\n"
        "                    answer = deterministic_email_answer\n"
        "                elif deterministic_language_answer is not None:\n"
        "                    answer = deterministic_language_answer\n"
        "                elif 'email' in label or 'phone' in label:\n"
        "                    answer = prev_answer\n",
        "preferred email selection priority",
    )

    source = _replace_once(
        source,
        "            if not prev_answer or overwrite_previous_answers:\n"
        "                if 'experience' in label or 'years' in label: answer = years_of_experience\n",
        "            if not prev_answer or overwrite_previous_answers:\n"
        "                adjacent_years_answer = (\n"
        "                    resolve_adjacent_technology_years(label_org)\n"
        "                )\n"
        "\n"
        "                if adjacent_years_answer is not None:\n"
        "                    answer = adjacent_years_answer\n"
        "                elif 'experience' in label or 'years' in label: answer = years_of_experience\n",
        "adjacent technology years before AI",
    )

    source = _replace_once(
        source,
        "# Function to discard the job application\n"
        "def discard_job() -> None:\n"
        "    actions.send_keys(Keys.ESCAPE).perform()\n"
        "    wait_span_click(driver, 'Discard', 2)\n",
        "# Function to discard the job application\n"
        "def discard_job() -> None:\n"
        "    \"\"\"Close the active Easy Apply modal and confirm discard.\"\"\"\n"
        "    close_button = try_xp(\n"
        "        driver,\n"
        "        (\n"
        "            '//div[contains(@class, \\\"jobs-easy-apply-modal\\\")]'\n"
        "            '//button['\n"
        "            'contains(@class, \\\"artdeco-modal__dismiss\\\") '\n"
        "            'or @aria-label=\\\"Dismiss\\\" '\n"
        "            'or @aria-label=\\\"Close\\\" '\n"
        "            'or @aria-label=\\\"Fermer\\\"]'\n"
        "        ),\n"
        "        False,\n"
        "    )\n"
        "\n"
        "    if close_button:\n"
        "        driver.execute_script(\n"
        "            'arguments[0].click();',\n"
        "            close_button,\n"
        "        )\n"
        "    else:\n"
        "        actions.send_keys(Keys.ESCAPE).perform()\n"
        "\n"
        "    sleep(0.5)\n"
        "\n"
        "    discard_button = try_xp(\n"
        "        driver,\n"
        "        (\n"
        "            '//button['\n"
        "            './/span[normalize-space()=\\\"Discard\\\"] '\n"
        "            'or .//span[normalize-space()=\\\"Abandonner\\\"] '\n"
        "            'or normalize-space()=\\\"Discard\\\" '\n"
        "            'or normalize-space()=\\\"Abandonner\\\"]'\n"
        "        ),\n"
        "        False,\n"
        "    )\n"
        "\n"
        "    if discard_button:\n"
        "        driver.execute_script(\n"
        "            'arguments[0].click();',\n"
        "            discard_button,\n"
        "        )\n"
        "\n"
        "    try:\n"
        "        WebDriverWait(driver, 4).until(\n"
        "            EC.invisibility_of_element_located(\n"
        "                (By.CLASS_NAME, 'jobs-easy-apply-modal')\n"
        "            )\n"
        "        )\n"
        "    except Exception:\n"
        "        pass\n",
        "robust Easy Apply modal discard",
    )

    source = _replace_once(
        source,
        "                    if is_easy_apply:\n"
        "                        try: \n"
        "                            try:\n"
        "                                errored = \"\"\n",
        "                    if is_easy_apply:\n"
        "                        try: \n"
        "                            unresolved_error = None\n"
        "                            try:\n"
        "                                errored = \"\"\n",
        "unresolved error initialization",
    )

    source = _replace_once(
        source,
        "                            except UnresolvedApplicationQuestion as unresolved_error:\n"
        "                                errored = \"unresolved\"\n",
        "                            except UnresolvedApplicationQuestion as error:\n"
        "                                unresolved_error = error\n"
        "                                errored = \"unresolved\"\n",
        "unresolved error capture",
    )

    source = _replace_once(
        source,
        "                                if errored == \"unresolved\":\n"
        "                                    raise unresolved_error\n",
        "                                if (\n"
        "                                    errored == \"unresolved\"\n"
        "                                    and unresolved_error is not None\n"
        "                                ):\n"
        "                                    raise unresolved_error\n",
        "safe unresolved error re-raise",
    )

    source = _replace_once(
        source,
        "def main() -> None:\n"
        "    # pyautogui.alert",
        "def main() -> None:\n"
        "    acquire_instance_lock()\n"
        "    # pyautogui.alert",
        "single-instance lock acquisition",
    )

    source = _replace_once(
        source,
        "    finally:\n"
        "        summary = \"Total runs:",
        "    finally:\n"
        "        release_instance_lock()\n"
        "        summary = \"Total runs:",
        "single-instance lock release",
    )

    source = _replace_once(
        source,
        "        msg = f\"{quotes}\\n\\n\\n{timeSavedMsg}\\nYou can also get your quote and name shown here, or prioritize your bug reports by supporting the project at:\\n\\nhttps://github.com/sponsors/GodsScion\\n\\n\\nSummary:\\n{summary}\\n\\n\\nBest regards,\\nSai Vignesh Golla\\nhttps://www.linkedin.com/in/saivigneshgolla/\\n\\nTop Sponsors:\\n{sponsors}\"\n",
        "        msg = f\"Job application run finished.\\n\\n{summary}\"\n",
        "clean exit summary",
    )

    source = _replace_once(
        source,
        "        pyautogui.alert(msg, \"Exiting..\")\n",
        "        pyautogui.alert(\n"
        "            msg,\n"
        "            \"Job application run finished\",\n"
        "        )\n",
        "clean exit dialog title",
    )

    source = source.replace(
        "\n\nif __name__ == \"__main__\":\n",
        f"\n\n{MARKER}\nif __name__ == \"__main__\":\n",
        1,
    )

    TARGET.write_text(
        source,
        encoding="utf-8",
        newline="\n",
    )

    return True
