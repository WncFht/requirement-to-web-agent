"""Bounded JSON edit -> fixed acceptance check -> repair loop."""

import re

from infrastructure.shared.agent.files import FileWorkspace
from infrastructure.shared.agent.protocol import FILE_EDIT_RULES

ANSI_SEQUENCES = re.compile(
    r"\x1b\[[0-9;]*[A-Za-z]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[@-Z\\-_]"
)


def compact_feedback(value, limit=4000, width=8):
    """Strip terminal control sequences and cap oversized strings in check feedback."""
    if isinstance(value, str):
        cleaned = ANSI_SEQUENCES.sub("", value)
        if len(cleaned) <= limit:
            return cleaned
        return (
            cleaned[:limit]
            + f"\n…[truncated; {len(cleaned) - limit} more characters omitted]"
        )
    if isinstance(value, list):
        return [compact_feedback(item, limit, width) for item in value[:width]]
    if isinstance(value, dict):
        return {
            key: compact_feedback(item, limit, width) for key, item in value.items()
        }
    return value


def run_file_agent(
    model,
    instructions: str,
    task: dict,
    files: FileWorkspace,
    gate,
    max_turns: int,
    console,
    label: str,
    feedback=None,
) -> dict:
    """Refresh task paths and files each round; accept edits only after the gate passes."""
    if max_turns < 1:
        raise ValueError("--max-turns must be positive")
    feedback = [] if feedback is None else [compact_feedback(item) for item in feedback]
    for turn in range(1, max_turns + 1):
        console.show(
            f"{label} | Edit round {turn}/{max_turns}",
            "Generate file edits, then run the stage's compilation and test acceptance checks.",
        )
        try:
            response = model.generate_json(
                instructions + "\n\n" + FILE_EDIT_RULES,
                {
                    # Cache-friendly key order: files are the most stable section
                    # (wiring + pages), task changes per target selection, feedback
                    # changes every round. DeepSeek prefix caching follows the
                    # serialized order, so volatile content must come last.
                    "files": files.state(),
                    "task": files.task_state(task),
                    "feedback": feedback,
                },
            )
            files.apply(response)
            if files.new_file is not None:
                raise ValueError(
                    "Create the target file in the first edit before running acceptance checks"
                )
            console.show(
                f"{label} | Edit round {turn}/{max_turns}",
                str([edit["path"] for edit in response["edits"]]),
            )
            return {"turns": turn, "checks": gate()}
        except (ValueError, OSError) as error:
            message = str(error)
            console.show(f"{label} | Repair feedback", message)
            feedback = [compact_feedback({"error": message}, limit=6000)]
    raise ValueError(f"Agent exhausted {max_turns} rounds for {label}")
