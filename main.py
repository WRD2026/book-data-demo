"""Command-line sales data cleaning and summary demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = {"date", "category", "amount", "quantity"}


def load_sales_data(input_path: Path) -> pd.DataFrame:
    """Read a CSV file and normalize its column names."""
    frame = pd.read_csv(input_path)
    frame.columns = [str(column).strip().lower() for column in frame.columns]

    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"Missing required columns: {missing_text}")
    return frame


def clean_sales_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert types, remove unusable rows, and calculate derived metrics."""
    cleaned = frame.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    cleaned["category"] = cleaned["category"].astype("string").str.strip()

    valid = (
        cleaned["date"].notna()
        & cleaned["category"].notna()
        & cleaned["category"].ne("")
        & cleaned["amount"].notna()
        & cleaned["quantity"].notna()
        & cleaned["amount"].ge(0)
        & cleaned["quantity"].gt(0)
    )
    cleaned = cleaned.loc[valid].copy()
    cleaned["quantity"] = cleaned["quantity"].astype(int)
    cleaned["revenue"] = (cleaned["amount"] * cleaned["quantity"]).round(2)
    cleaned["month"] = cleaned["date"].dt.to_period("M").astype(str)
    return cleaned.sort_values("date").reset_index(drop=True)


def build_summary(cleaned: pd.DataFrame) -> dict[str, Any]:
    """Build overall, category, and monthly summary sections."""
    category_summary = (
        cleaned.groupby("category", as_index=False)
        .agg(
            order_count=("category", "size"),
            units_sold=("quantity", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )
    monthly_summary = (
        cleaned.groupby("month", as_index=False)
        .agg(order_count=("month", "size"), revenue=("revenue", "sum"))
        .sort_values("month")
    )

    return {
        "total_orders": int(len(cleaned)),
        "total_units": int(cleaned["quantity"].sum()),
        "total_revenue": round(float(cleaned["revenue"].sum()), 2),
        "average_order_value": round(float(cleaned["revenue"].mean()), 2)
        if not cleaned.empty
        else 0.0,
        "by_category": category_summary.to_dict(orient="records"),
        "by_month": monthly_summary.to_dict(orient="records"),
    }


def process_sales_file(input_path: Path, output_dir: Path) -> dict[str, Any]:
    """Process one CSV file and write cleaned data plus a JSON summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned = clean_sales_data(load_sales_data(input_path))

    cleaned_path = output_dir / "cleaned_sales.csv"
    summary_path = output_dir / "summary.json"
    export_frame = cleaned.copy()
    export_frame["date"] = export_frame["date"].dt.strftime("%Y-%m-%d")
    export_frame.to_csv(cleaned_path, index=False)

    summary = build_summary(cleaned)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Cleaned data: {cleaned_path}")
    print(f"Summary report: {summary_path}")
    print(f"Total revenue: {summary['total_revenue']:.2f}")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean sales CSV data and create summary reports.")
    parser.add_argument("--input", type=Path, required=True, help="Input sales CSV path")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    process_sales_file(args.input, args.output_dir)


if __name__ == "__main__":
    main()
