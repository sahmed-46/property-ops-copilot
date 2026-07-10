from __future__ import annotations

import csv
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from src.data.paths import SAMPLE_SEED_PATH, cache_dir, datasets_config


def build_data_bundle(*, use_cache: bool = True) -> dict:
    """Merge committed sample seed with optional cached external datasets."""
    data = deepcopy(json.loads(SAMPLE_SEED_PATH.read_text(encoding="utf-8")))
    data.setdefault("work_orders", [])

    if not use_cache:
        return data

    cfg = datasets_config()
    cache = cache_dir()

    _merge_cuad_clauses(data, cache / cfg["downloads"]["cuad_qa"]["outfile"])
    _merge_historical_tickets(data, cache / cfg["downloads"]["propertypilot"]["outfile"])
    _merge_historical_tickets(data, cache / cfg["downloads"]["nyc_311"]["outfile"])

    return data


def _merge_cuad_clauses(data: dict, path: Path) -> None:
    if not path.exists():
        return

    lease_ids = [l["id"] for l in data["leases"]]
    if not lease_ids:
        return

    existing_ids = {c["id"] for c in data["lease_clauses"]}
    with path.open(encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if row["id"] in existing_ids:
                continue
            data["lease_clauses"].append(
                {
                    "id": row["id"],
                    "lease_id": lease_ids[i % len(lease_ids)],
                    "section": row["section"],
                    "title": row["title"],
                    "text": row["text"],
                }
            )


def _merge_historical_tickets(data: dict, path: Path) -> None:
    if not path.exists():
        return

    existing_ids = {w["id"] for w in data["work_orders"]}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["id"] in existing_ids:
                continue
            created = row.get("created_at") or datetime.now(timezone.utc).isoformat()
            data["work_orders"].append(
                {
                    "id": row["id"],
                    "unit_id": row["unit_id"],
                    "category": row["category"],
                    "priority": row["priority"],
                    "status": row.get("status") or "closed",
                    "description": row["description"],
                    "created_at": created,
                }
            )
