import os
import re

import anthropic


def generate_analysis_code(
    question: str,
    profile: dict,
    playbook: str,
    source: str,
    conversation_history: list = [],
) -> str:
    """Generate dashboard analysis code grounded in profile, methodology, and conversation history.

    Raises ValueError if ANTHROPIC_API_KEY is not set.
    Returns a clean Python code string with no markdown fences.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Add it to your .env file. "
            "See .env.example for the format."
        )

    prompt = _build_code_prompt(question, profile, playbook, source, conversation_history)
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text
    return _strip_fences(raw)


def generate_insight_narrative(
    question: str,
    profile: dict,
    kpi_cards: list,
    anomalies: list,
    conversation_history: list = [],
) -> str:
    """Generate a plain-English insight narrative from execution results.

    Returns empty string on any failure — never crashes the main pipeline.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return ""

    kpi_lines = "\n".join(
        f"- {k.get('label', '')}: {k.get('value', '')} ({k.get('delta', '')})"
        for k in kpi_cards
    ) or "- No metrics extracted"

    anomaly_lines = "\n".join(
        f"- {a.get('column', '')}: {a.get('finding', '')}"
        for a in anomalies
    ) or "- None detected"

    history_block = ""
    if conversation_history:
        recent = conversation_history[-6:]
        lines = []
        for msg in recent:
            role = msg.get("role", "")
            content = str(msg.get("content", ""))[:200]
            if role == "user":
                lines.append(f"Previously asked: {content}")
            elif role == "assistant":
                lines.append(f"Previous finding: {content}")
        if lines:
            history_block = "Prior conversation context:\n" + "\n".join(lines) + "\n\n"

    prompt = f"""{history_block}You are a senior data analyst presenting findings to a business stakeholder.

Question asked: {question}
Dataset: {profile.get("summary", "")}

Key metrics found:
{kpi_lines}

Anomalies detected:
{anomaly_lines}

Write 3-5 sentences in plain English that:
1. Directly answer the question asked
2. Highlight the most important finding with specific numbers
3. Call out any anomaly that needs attention
4. Suggest what this means for the business

Rules:
- Write for a non-technical stakeholder
- Use specific numbers from the metrics
- Do not mention Python, code, or technical methods
- Do not start with "Based on" or "The analysis shows"
- Be direct and confident"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception:
        return ""


def generate_follow_up_suggestions(
    question: str,
    profile: dict,
    kpi_cards: list,
) -> list:
    """Generate 3 natural follow-up questions based on the analysis performed.

    Returns safe defaults per data type on any failure.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    data_type = profile.get("data_type", "tabular")

    _defaults = {
        "tabular": [
            "Show top 10 rows by highest value",
            "Which category performs worst?",
            "Show distribution of each numeric column",
        ],
        "time_series": [
            "Show seasonal patterns across years",
            "Forecast the next 3 periods",
            "Find anomalies in the trend",
        ],
        "wide_format": [
            "Show correlation matrix between columns",
            "Which features have the most variance?",
            "Cluster similar rows together",
        ],
    }
    defaults = _defaults.get(data_type, _defaults["tabular"])

    if not api_key:
        return defaults

    kpi_summary = ", ".join(
        f"{k.get('label', '')}: {k.get('value', '')}" for k in kpi_cards
    ) or "no metrics extracted"

    col_names = [c["name"] for c in profile.get("columns", [])][:6]

    prompt = f"""Given this data analysis:
Question: {question}
Data: {profile.get("summary", "")}
Columns: {", ".join(col_names)}
Key metrics: {kpi_summary}

Generate exactly 3 follow-up questions a data analyst would naturally ask next.
Each must:
- Be under 10 words
- Be specific to this data (use actual column names where natural)
- Be different from the original question

Return ONLY a JSON array of 3 strings. No other text.
Example: ["Which month has highest sales?", "Compare Q1 vs Q2 performance", "Show outliers in revenue column"]"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        suggestions = json_parse_list(raw)
        if isinstance(suggestions, list) and len(suggestions) == 3:
            return suggestions
        return defaults
    except Exception:
        return defaults


def _build_code_prompt(
    question: str,
    profile: dict,
    playbook: str,
    source: str,
    conversation_history: list,
) -> str:
    col_lines = "\n".join(
        f"  {c['name']} | {c['dtype']} | {c['null_pct']}% null"
        for c in profile.get("columns", [])
    )
    numeric_cols = ", ".join(profile.get("numeric_columns", [])) or "none"
    datetime_cols = ", ".join(profile.get("datetime_columns", [])) or "none"

    history_section = ""
    if conversation_history:
        recent = conversation_history[-6:]
        lines = []
        for msg in recent:
            role = msg.get("role", "")
            content = str(msg.get("content", ""))[:300]
            if role == "user":
                lines.append(f"User asked: {content}")
            elif role == "assistant":
                lines.append(f"Analysis performed: {content}")
        if lines:
            history_section = "=== CONVERSATION HISTORY ===\n" + "\n".join(lines) + "\n\n"

    return f"""{history_section}=== DATA PROFILE ===
Dataset: {profile.get("summary", "")}
Rows: {profile.get("row_count")} | Columns: {profile.get("column_count")}
Type: {profile.get("data_type")}
Columns:
{col_lines}
Numeric columns: {numeric_cols}
Datetime columns: {datetime_cols}

=== METHODOLOGY ===
{playbook}

=== CURRENT REQUEST ===
{question}

=== INSTRUCTIONS ===
Write Python code that does ALL of the following:

1. Load data from: {source}
   - If URL: import requests, import io, fetch with requests.get(), then pd.read_csv(io.StringIO(response.text)) or pd.read_excel(io.BytesIO(response.content))
   - If local path: pd.read_csv() or pd.read_excel()
   - Always import io at the top.

2. Produce a DASHBOARD figure with 2-4 subplots.
   - Each subplot answers a different analytical question about the data.
   - Use matplotlib. seaborn is allowed.
   - Figure size: (14, 10) for 4 panels, (12, 6) for 2 panels.
   - Call plt.tight_layout() before saving.
   - Apply dark style: plt.style.use('dark_background')
   - Use #6366f1 as the primary accent color for the main data series.

3. Save the figure:
   plt.savefig('/tmp/output.png', dpi=150, bbox_inches='tight', facecolor='#09090b', edgecolor='none')

4. Print EXACTLY this JSON block as the LAST thing printed — nothing after it:
   import json
   summary = {{
     "kpis": [
       {{"label": "...", "value": "...", "delta": "..."}}
     ],
     "anomalies": [
       {{"column": "...", "finding": "..."}}
     ]
   }}
   print("PHOTON_SUMMARY:" + json.dumps(summary))

   Rules for KPIs:
   - Include 3-5 KPIs that are meaningful for this specific data
   - value should be a formatted string like "1,247" or "23.4%" or "$4.2M"
   - delta should be a string like "+12%" or "-3 units" or "" if not calculable
   Rules for anomalies:
   - Only include genuinely detected anomalies (outliers beyond 2 std devs, unexpected nulls, impossible values)
   - If none detected, use empty list: []

5. Return only the Python code. No markdown. No triple backticks. No explanation."""


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:python)?\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


def json_parse_list(text: str) -> list:
    """Extract a JSON array from text, tolerating surrounding whitespace."""
    try:
        start = text.index("[")
        end = text.rindex("]") + 1
        return __import__("json").loads(text[start:end])
    except Exception:
        return []
