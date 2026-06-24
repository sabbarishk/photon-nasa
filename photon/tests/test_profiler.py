import io
import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from app.services.profiler import load_dataframe, profile


def test_tabular_detection():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "score": [0.9, 0.8, 0.7, 0.6, 0.5],
            "label": ["a", "b", "a", "b", "a"],
        }
    )
    result = profile(df)
    assert result["data_type"] == "tabular"
    assert result["row_count"] == 5
    assert result["column_count"] == 3
    assert "score" in result["numeric_columns"]
    assert result["datetime_columns"] == []
    assert result["has_nulls"] is False


def test_time_series_detection():
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2020-01-03"],
            "temperature": [15.2, 16.1, 14.8],
        }
    )
    result = profile(df)
    assert result["data_type"] == "time_series"
    assert "date" in result["datetime_columns"]
    assert "temperature" in result["numeric_columns"]
    assert "time series" in result["summary"].lower()


def test_null_detection():
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "value": [np.nan, np.nan, np.nan, np.nan, 1.0],
        }
    )
    result = profile(df)
    assert result["has_nulls"] is True
    value_col = next(c for c in result["columns"] if c["name"] == "value")
    assert value_col["null_pct"] == 80.0


def test_load_csv():
    data = "a,b,c\n1,2,3\n4,5,6\n"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        f.write(data)
        tmp_path = f.name
    try:
        df = load_dataframe(tmp_path)
        assert df.shape == (2, 3)
        assert list(df.columns) == ["a", "b", "c"]
    finally:
        os.unlink(tmp_path)
