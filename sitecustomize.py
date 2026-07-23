from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "runAiBot.py"
MARKER = "# AUTO_JOB_RUNTIME_HOTFIX_V1"


def replace_once(text: str, old: str, new: str, description: str) -> str:
    count = text.count(old)

    if count == 0:
        if new in text:
            return text

        raise RuntimeError(
            f"Unable to apply runtime hotfix: {description}. "
            "The source no longer matches the expected version."
        )

    if count != 1:
        raise RuntimeError(
            f"Unable to apply runtime hotfix: {description} matched "
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
        "    form_step_delay_seconds,\n)",
        "    form_step_delay_seconds,\n"
        "    preferred_application_email,\n"
        ")",
        "preferred email import",
    )

    source = replace_once(
        source,
        "from modules.validator import validate_config\n",
        "from modules.validator import validate_config\n"
        "from modules.single_instance import (\n"
        "    acquire_instance_lock,\n"
        "    release_instance_lock,\n"
        ")\n",
        "single-instance imports",
    )

    email_logic_old = """            prev_answer = selected_option

            deterministic_language_answer = (
"""
    email_logic_new = """            prev_answer = selected_option

            deterministic_email_answer = None
            if (
                preferred_application_email
                and 'email' in label
            ):
                matching_email = next(
                    (
                        option
                        for option in optionsText
                        if option.strip().casefold()
                        == preferred_application_email.casefold()
                    ),
                    None,
                )

                if matching_email is not None:
                    deterministic_email_answer = matching_email
                    print_lg(
                        "DETERMINISTIC EMAIL ANSWER | "
                        f"question={label_org!r} | "
                        f"answer={matching_email!r} | "
                        f"previous={selected_option!r}"
                    )
                else:
                    raise UnresolvedApplicationQuestion(
                        label_org,
                        "single_select",
                        "Configured preferred application email was not "
                        f"available. preferred={preferred_application_email!r}; "
                        f"options={optionsText!r}",
                    )

            deterministic_language_answer = (
"""
    source = replace_once(
        source,
        email_logic_old,
        email_logic_new,
        "deterministic preferred email resolver",
    )

    source = replace_once(
        source,
        "                or deterministic_language_answer is not None\n",
        "                or deterministic_language_answer is not None\n"
        "                or deterministic_email_answer is not None\n",
        "preferred email overwrite condition",
    )

    source = replace_once(
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

    source = replace_once(
        source,
        "                            try:\n"
        "                                errored = \"\"\n"
        "                                modal = find_by_class(driver, \"jobs-easy-apply-modal\")\n",
        "                            unresolved_error = None\n"
        "                            try:\n"
        "                                errored = \"\"\n"
        "                                modal = find_by_class(driver, \"jobs-easy-apply-modal\")\n",
        "unresolved exception initialization",
    )

    source = replace_once(
        source,
        "                            except UnresolvedApplicationQuestion as unresolved_error:\n"
        "                                errored = \"unresolved\"\n",
        "                            except UnresolvedApplicationQuestion as error:\n"
        "                                unresolved_error = error\n"
        "                                errored = \"unresolved\"\n",
        "unresolved exception capture",
    )

    source = replace_once(
        source,
        "                                if errored == \"unresolved\":\n"
        "                                    raise unresolved_error\n",
        "                                if (\n"
        "                                    errored == \"unresolved\"\n"
        "                                    and unresolved_error is not None\n"
        "                                ):\n"
        "                                    raise unresolved_error\n",
        "safe unresolved exception re-raise",
    )

    source = replace_once(
        source,
        "def main() -> None:\n"
        "    # pyautogui.alert",
        "def main() -> None:\n"
        "    acquire_instance_lock()\n"
        "    # pyautogui.alert",
        "single-instance lock acquisition",
    )

    source = replace_once(
        source,
        "    finally:\n"
        "        summary = \"Total runs:",
        "    finally:\n"
        "        release_instance_lock()\n"
        "        summary = \"Total runs:",
        "single-instance lock release",
    )

    source = source.replace(
        "        msg = f\"{quotes}\\n\\n\\n{timeSavedMsg}\\nYou can also get your quote and name shown here, or prioritize your bug reports by supporting the project at:\\n\\nhttps://github.com/sponsors/GodsScion\\n\\n\\nSummary:\\n{summary}\\n\\n\\nBest regards,\\nSai Vignesh Golla\\nhttps://www.linkedin.com/in/saivigneshgolla/\\n\\nTop Sponsors:\\n{sponsors}\"\n",
        "        msg = f\"Job application run finished.\\n\\n{summary}\"\n",
        1,
    )

    source = source.replace(
        "        pyautogui.alert(msg, \"Exiting..\")\n",
        "        pyautogui.alert(msg, \"Job application run finished\")\n",
        1,
    )

    source = source.replace(
        "\n\nif __name__ == \"__main__\":\n",
        f"\n\n{MARKER}\nif __name__ == \"__main__\":\n",
        1,
    )

    TARGET.write_text(source, encoding="utf-8", newline="\n")


patch_run_ai_bot()
