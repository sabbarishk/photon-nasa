import os
import re

import anthropic


def generate_analysis_code(
    question: str,
    profile: dict,
    playbook: str,
    source: str,
) -> str:
    """Build a structured prompt and call Claude to generate analysis code.

    Raises ValueError if ANTHROPIC_API_KEY is not set.
    Returns a clean Python code string with no markdown fences.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Add it to your .env file. "
            "See .env.example for the format."
        )

    prompt = _build_prompt(question, profile, playbook, source)
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text
    return _strip_fences(raw)


def _build_prompt(question: str, profile: dict, playbook: str, source: str) -> str:
    col_lines = "\n".join(
        f"  - {c['name']} ({c['dtype']}, {c['null_pct']}% null,"
        f" {c['n_unique']} unique values)"
        for c in profile.get("columns", [])
    )
    return f"""QUESTION:
{question}

DATA PROFILE:
{profile.get("summary", "")}
Rows: {profile.get("row_count")}
Columns: {profile.get("column_count")}
Data type: {profile.get("data_type")}
Column details:
{col_lines}

METHODOLOGY:
{playbook}

INSTRUCTIONS:
Write executable Python using pandas and matplotlib.
Load the data from: {source}
The code must run without any editing.
End with plt.savefig('/tmp/output.png').
Return only the code. No explanation. No markdown fences."""


def _strip_fences(text: str) -> str:
    """Remove accidental markdown code fences from LLM output."""
    text = text.strip()
    text = re.sub(r"^```(?:python)?\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()
