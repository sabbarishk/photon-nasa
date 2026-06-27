import io
import os

import pandas as pd
import requests


def load_dataframe(source: str) -> pd.DataFrame:
    """Load a CSV, Excel, or JSON dataset into a DataFrame from a local path or URL."""
    is_url = source.startswith("http://") or source.startswith("https://")

    if is_url:
        try:
            resp = requests.get(source, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL: {e}")
        content_type = resp.headers.get("Content-Type", "")
        if source.endswith(".xlsx") or "spreadsheet" in content_type or "excel" in content_type:
            return pd.read_excel(io.BytesIO(resp.content))
        if source.endswith(".json") or "json" in content_type:
            return pd.read_json(io.StringIO(resp.text))
        return pd.read_csv(io.StringIO(resp.text))

    if not os.path.exists(source):
        raise ValueError(f"File not found: {source}")
    if source.endswith(".xlsx"):
        return pd.read_excel(source)
    if source.endswith(".json"):
        return pd.read_json(source)
    if source.endswith(".csv"):
        return pd.read_csv(source)
    raise ValueError(
        f"Unsupported file format. Expected .csv, .xlsx, or .json, got: {source}"
    )


def profile(df: pd.DataFrame) -> dict:
    """Inspect a DataFrame and return structured metadata about its content."""
    row_count = len(df)
    column_count = len(df.columns)

    columns = []
    numeric_columns = []
    datetime_columns = []

    for col in df.columns:
        series = df[col]
        null_pct = round(float(series.isna().mean() * 100), 1)
        n_unique = int(series.nunique(dropna=True))
        sample_values = [str(v) for v in series.dropna().head(3).tolist()]

        if pd.api.types.is_numeric_dtype(series):
            dtype_label = "numeric"
            numeric_columns.append(col)
        elif pd.api.types.is_datetime64_any_dtype(series):
            dtype_label = "datetime"
            datetime_columns.append(col)
        elif series.dtype == object:
            # Try to infer datetime from string values.
            parsed = pd.to_datetime(series, errors="coerce", format="mixed")
            if parsed.notna().mean() > 0.8:
                dtype_label = "datetime"
                datetime_columns.append(col)
            else:
                dtype_label = "string"
        else:
            dtype_label = "string"

        columns.append(
            {
                "name": col,
                "dtype": dtype_label,
                "null_pct": null_pct,
                "n_unique": n_unique,
                "sample_values": sample_values,
            }
        )

    has_nulls = any(c["null_pct"] > 5.0 for c in columns)

    if datetime_columns and numeric_columns:
        data_type = "time_series"
    elif column_count > 20 and row_count < 100:
        data_type = "wide_format"
    else:
        data_type = "tabular"

    null_count = sum(1 for c in columns if c["null_pct"] > 5.0)
    type_label = data_type.replace("_", " ").title()
    summary = (
        f"{type_label} dataset with {row_count} rows, {column_count} columns"
    )
    type_mentions = []
    if datetime_columns:
        type_mentions.append("datetime")
    if numeric_columns:
        type_mentions.append("numeric")
    if type_mentions:
        summary += f", including {' and '.join(type_mentions)} columns"
    summary += "."
    if null_count:
        summary += (
            f" {null_count} column{'s' if null_count > 1 else ''} "
            "have significant nulls."
        )

    return {
        "row_count": row_count,
        "column_count": column_count,
        "columns": columns,
        "data_type": data_type,
        "has_nulls": has_nulls,
        "numeric_columns": numeric_columns,
        "datetime_columns": datetime_columns,
        "summary": summary,
    }
