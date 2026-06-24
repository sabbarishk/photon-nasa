"""
Tests for llm.py — the LLM code generation service.

These tests mock the Anthropic client entirely. We are not testing whether
the Anthropic API works (that's Anthropic's job). We are testing:
- that our function reads ANTHROPIC_API_KEY correctly
- that it raises ValueError with a clear message when the key is missing
- that it calls the client, extracts the text, strips markdown fences,
  and returns a non-empty string
"""
from unittest.mock import MagicMock, patch

import pytest

from app.services.llm import generate_analysis_code

_FAKE_PROFILE = {
    "row_count": 10,
    "column_count": 2,
    "columns": [
        {
            "name": "date",
            "dtype": "datetime",
            "null_pct": 0.0,
            "n_unique": 10,
            "sample_values": ["2020-01-01"],
        },
        {
            "name": "temp",
            "dtype": "numeric",
            "null_pct": 0.0,
            "n_unique": 10,
            "sample_values": ["15.2"],
        },
    ],
    "data_type": "time_series",
    "has_nulls": False,
    "numeric_columns": ["temp"],
    "datetime_columns": ["date"],
    "summary": "Time series dataset with 10 rows, 2 columns.",
}


def test_generate_returns_code(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    fake_text = "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())"
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text=fake_text)]

    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_response

    with patch("app.services.llm.anthropic.Anthropic", return_value=fake_client):
        result = generate_analysis_code(
            question="Show temperature trends",
            profile=_FAKE_PROFILE,
            playbook="Check stationarity before trending.",
            source="data.csv",
        )

    assert isinstance(result, str)
    assert len(result) > 0
    assert "import pandas" in result


def test_strips_markdown_fences(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    fenced = "```python\nimport pandas as pd\ndf = pd.read_csv('data.csv')\n```"
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text=fenced)]

    fake_client = MagicMock()
    fake_client.messages.create.return_value = fake_response

    with patch("app.services.llm.anthropic.Anthropic", return_value=fake_client):
        result = generate_analysis_code(
            question="Any question",
            profile=_FAKE_PROFILE,
            playbook="",
            source="data.csv",
        )

    assert not result.startswith("```")
    assert not result.endswith("```")
    assert "import pandas" in result


def test_raises_when_key_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not set"):
        generate_analysis_code(
            question="Any question",
            profile=_FAKE_PROFILE,
            playbook="",
            source="data.csv",
        )
