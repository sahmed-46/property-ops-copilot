"""Download external datasets once into data/cache/ (skipped if already present)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.download import download_all, download_dataset  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Download datasets into data/cache/")
    parser.add_argument(
        "datasets",
        nargs="*",
        choices=["cuad_qa", "propertypilot", "nyc_311"],
        help="Specific datasets to download (default: all)",
    )
    parser.add_argument("--force", action="store_true", help="Re-download even if cache exists")
    args = parser.parse_args()

    names = args.datasets or ["cuad_qa", "propertypilot", "nyc_311"]
    paths = [download_dataset(name, force=args.force) for name in names]
    for path in paths:
        print(f"OK  {path}")


if __name__ == "__main__":
    main()
