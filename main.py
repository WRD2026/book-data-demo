"""Collect public demo book data, clean it, summarize it, and draw charts.

The default source is books.toscrape.com, a site intended for scraping practice.
This demo makes low-frequency requests and does not bypass authentication or limits.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import pandas as pd

DEFAULT_URL = "https://books.toscrape.com/catalogue/page-{page}.html"
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
USER_AGENT = "book-data-demo/1.0 (portfolio example; contact: replace-with-your-email)"
# 评分文字统一映射为数值，便于后续使用 Pandas 做统计。


def fetch_html(url: str, timeout: int = 20) -> str:
    """Fetch one public page with a descriptive user agent."""
    import requests

    # 只请求公开页面，不携带登录信息，也不绕过站点限制。
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_price(text: str) -> float | None:
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text.replace(",", ""))
    return round(float(match.group(1)), 2) if match else None


def parse_book_cards(html: str, page_number: int, page_url: str) -> list[dict[str, Any]]:
    """Parse book cards; an optional data-sales attribute is accepted when supplied."""
    from bs4 import BeautifulSoup

    # 逐个读取图书卡片；缺失字段先保留为空，再交给清洗步骤处理。
    soup = BeautifulSoup(html, "html.parser")
    records: list[dict[str, Any]] = []
    for card in soup.select("article.product_pod"):
        title_link = card.select_one("h3 a")
        if title_link is None:
            continue
        rating_element = card.select_one("p.star-rating")
        rating_name = next(
            (name for name in RATING_MAP if rating_element and name in rating_element.get("class", [])),
            None,
        )
        availability = card.select_one("p.instock")
        sales_value = card.get("data-sales")
        records.append(
            {
                "title": title_link.get("title") or title_link.get_text(" ", strip=True),
                "price": parse_price(card.select_one("p.price_color").get_text())
                if card.select_one("p.price_color")
                else None,
                "rating": RATING_MAP.get(rating_name),
                "sales": sales_value,
                "availability": availability.get_text(" ", strip=True) if availability else "",
                "url": urljoin(page_url, title_link.get("href", "")),
                "page": page_number,
            }
        )
    return records


def crawl_books(url_template: str, pages: int, delay: float) -> list[dict[str, Any]]:
    """Collect at most ``pages`` pages with a non-negative delay between requests."""
    if pages < 1:
        raise ValueError("pages must be at least 1")
    if delay < 0:
        raise ValueError("delay must be non-negative")

    records: list[dict[str, Any]] = []
    for page_number in range(1, pages + 1):
        page_url = url_template.format(page=page_number)
        records.extend(parse_book_cards(fetch_html(page_url), page_number, page_url))
        if page_number < pages:
            time.sleep(delay)
    return records


def clean_books(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize types, remove unusable rows, and deduplicate by detail URL."""
    columns = ["title", "price", "rating", "sales", "availability", "url", "page"]
    # 先固定列结构，再转换数值类型，避免字符串直接参与统计。
    frame = pd.DataFrame(records, columns=columns)
    if frame.empty:
        return frame
    frame["title"] = frame["title"].astype("string").str.strip()
    frame["price"] = pd.to_numeric(frame["price"], errors="coerce")
    frame["rating"] = pd.to_numeric(frame["rating"], errors="coerce")
    frame["sales"] = pd.to_numeric(frame["sales"], errors="coerce")
    frame = frame.dropna(subset=["title", "price", "rating", "url"])
    frame = frame[frame["price"].ge(0) & frame["rating"].between(1, 5)]
    return frame.drop_duplicates(subset=["url"]).reset_index(drop=True)


def summarize_books(frame: pd.DataFrame) -> dict[str, Any]:
    """Return conservative metrics and report whether a sales field was available."""
    # 只有原始数据明确提供销量字段时才汇总，不从评分或库存推测销量。
    summary: dict[str, Any] = {
        "book_count": int(len(frame)),
        "average_price": round(float(frame["price"].mean()), 2) if not frame.empty else 0.0,
        "average_rating": round(float(frame["rating"].mean()), 2) if not frame.empty else 0.0,
        "rating_distribution": {
            str(int(rating)): int(count)
            for rating, count in frame["rating"].value_counts().sort_index().items()
        }
    }
    sales = frame["sales"].dropna() if "sales" in frame else pd.Series(dtype=float)
    summary["sales_field_available"] = bool(not sales.empty)
    if not sales.empty:
        summary["total_sales"] = int(sales.sum())
        summary["average_sales"] = round(float(sales.mean()), 2)
    return summary


def save_outputs(frame: pd.DataFrame, summary: dict[str, Any], output_dir: Path) -> None:
    """Write tabular, JSON, and PNG outputs."""
    import matplotlib

    # 使用无界面后端，确保脚本可在本地终端或 CI 环境生成 PNG。
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_dir / "books_cleaned.csv", index=False, encoding="utf-8-sig")
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    rating_counts = frame["rating"].value_counts().sort_index()
    ax = rating_counts.plot(kind="bar", title="Book Rating Distribution", color="#4f46e5")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Book count")
    ax.figure.tight_layout()
    ax.figure.savefig(output_dir / "rating_distribution.png", dpi=150)
    plt.close(ax.figure)

    ax = frame["price"].plot(kind="hist", bins=10, title="Book Price Distribution", color="#0f766e")
    ax.set_xlabel("Price")
    ax.figure.tight_layout()
    ax.figure.savefig(output_dir / "price_distribution.png", dpi=150)
    plt.close(ax.figure)

    if frame["sales"].notna().any():
        ax = frame.plot.scatter(x="rating", y="sales", title="Sales and Rating")
        ax.figure.tight_layout()
        ax.figure.savefig(output_dir / "sales_rating.png", dpi=150)
        plt.close(ax.figure)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl public demo book pages and create analysis outputs.")
    parser.add_argument("--pages", type=int, default=1, help="Number of public demo pages to fetch")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between page requests in seconds")
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--url-template", default=DEFAULT_URL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = crawl_books(args.url_template, args.pages, args.delay)
    frame = clean_books(records)
    summary = summarize_books(frame)
    save_outputs(frame, summary, args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
