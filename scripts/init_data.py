"""Build SQLite from sample seed + optional cached external datasets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.bundle import build_data_bundle  # noqa: E402
from src.data.seed import seed_database  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize SQLite from seed + cache")
    parser.add_argument(
        "--sample-only",
        action="store_true",
        help="Ignore data/cache and load only data/sample/seed.json",
    )
    args = parser.parse_args()

    bundle = build_data_bundle(use_cache=not args.sample_only)
    db_path = seed_database(bundle)

    clause_count = len(bundle["lease_clauses"])
    ticket_count = len(bundle.get("work_orders", []))
    source = "sample only" if args.sample_only else "sample + cache"
    print(f"Seeded {db_path}")
    print(f"  source: {source}")
    print(f"  lease clauses: {clause_count}")
    print(f"  historical work orders: {ticket_count}")


if __name__ == "__main__":
    main()
