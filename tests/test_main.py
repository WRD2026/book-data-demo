import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from main import build_summary, clean_sales_data, process_sales_file


class SalesPipelineTests(unittest.TestCase):
    def test_cleaning_removes_invalid_rows_and_calculates_revenue(self):
        frame = pd.DataFrame(
            {
                "date": ["2026-01-01", "not-a-date"],
                "category": [" Notebook ", "Pen"],
                "amount": [10, 2],
                "quantity": [3, 1],
            }
        )
        cleaned = clean_sales_data(frame)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.loc[0, "category"], "Notebook")
        self.assertEqual(cleaned.loc[0, "revenue"], 30)

    def test_summary_and_file_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_path = root / "sales.csv"
            input_path.write_text(
                "date,category,amount,quantity\n2026-01-01,Pen,2.5,4\n",
                encoding="utf-8",
            )
            output_dir = root / "output"
            summary = process_sales_file(input_path, output_dir)
            self.assertEqual(summary["total_revenue"], 10.0)
            self.assertTrue((output_dir / "cleaned_sales.csv").exists())
            saved_summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(saved_summary["total_orders"], 1)

    def test_empty_summary_is_safe(self):
        cleaned = clean_sales_data(
            pd.DataFrame(
                {"date": ["not-a-date"], "category": ["Pen"], "amount": [2], "quantity": [1]}
            )
        )
        summary = build_summary(cleaned)
        self.assertEqual(summary["average_order_value"], 0.0)


if __name__ == "__main__":
    unittest.main()
