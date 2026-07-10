from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode

import httpx

from src.data.paths import cache_dir, datasets_config


def _cache_path(filename: str) -> Path:
    path = cache_dir() / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def download_cuad_clauses(cfg: dict) -> Path:
    outfile = _cache_path(cfg["outfile"])
    if outfile.exists():
        return outfile

    from huggingface_hub import hf_hub_download

    csv_path = hf_hub_download(
        repo_id=cfg["repo"],
        filename=cfg["filename"],
        repo_type="dataset",
    )
    limit = int(cfg.get("limit", 80))

    rows: list[dict] = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        clause_idx = 0
        for doc_i, record in enumerate(reader):
            doc_name = (record.get("Document Name-Answer") or record.get("Filename") or f"DOC-{doc_i}").strip()
            lease_id = f"LEASE-CUAD-{doc_i + 1:03d}"
            for col, value in record.items():
                if not col.endswith("-Answer"):
                    continue
                text = (value or "").strip()
                if not text or text.upper() in {"N/A", "NONE", "[]"}:
                    continue
                title = col.removesuffix("-Answer").strip()
                clause_idx += 1
                rows.append(
                    {
                        "id": f"LC-CUAD-{clause_idx:04d}",
                        "lease_id": lease_id,
                        "section": f"CUAD-{clause_idx:04d}",
                        "title": title,
                        "text": text[:2000],
                        "source": "cuad",
                        "document": doc_name[:120],
                    }
                )
                if len(rows) >= limit:
                    break
            if len(rows) >= limit:
                break

    _write_csv(
        outfile,
        rows,
        ["id", "lease_id", "section", "title", "text", "source", "document"],
    )
    return outfile


def download_propertypilot(cfg: dict) -> Path:
    outfile = _cache_path(cfg["outfile"])
    if outfile.exists():
        return outfile

    from datasets import load_dataset

    ds = load_dataset(cfg["dataset"], split=cfg["split"])
    limit = int(cfg.get("limit", 150))
    unit_ids = ["UNIT-101", "UNIT-204"]

    rows: list[dict] = []
    for i, row in enumerate(ds):
        if i >= limit:
            break
        text = (row.get("raw_text") or row.get("description") or "").strip()
        if not text:
            continue
        category = (row.get("category") or "general").lower().replace(" ", "_")
        urgency = (row.get("urgency") or row.get("priority") or "normal").lower()
        rows.append(
            {
                "id": f"WO-HIST-PP-{i + 1:04d}",
                "unit_id": unit_ids[i % len(unit_ids)],
                "category": category,
                "priority": _map_priority(urgency),
                "status": "closed",
                "description": text[:1000],
                "created_at": row.get("created_at") or row.get("submitted_at") or "",
                "source": "propertypilot",
            }
        )

    _write_csv(
        outfile,
        rows,
        ["id", "unit_id", "category", "priority", "status", "description", "created_at", "source"],
    )
    return outfile


def download_nyc_311(cfg: dict) -> Path:
    outfile = _cache_path(cfg["outfile"])
    if outfile.exists():
        return outfile

    types = cfg.get("complaint_types") or []
    where = " OR ".join(f"complaint_type='{t}'" for t in types)
    params = {"$limit": cfg.get("limit", 200), "$order": "created_date DESC"}
    if where:
        params["$where"] = where

    url = f"{cfg['url']}?{urlencode(params)}"
    with httpx.Client(timeout=60.0) as client:
        resp = client.get(url)
        resp.raise_for_status()
        records = resp.json()

    unit_ids = ["UNIT-101", "UNIT-204"]
    rows: list[dict] = []
    for i, rec in enumerate(records):
        desc_parts = [
            rec.get("complaint_type"),
            rec.get("descriptor"),
            rec.get("descriptor_2"),
            rec.get("resolution_description"),
        ]
        description = " — ".join(p for p in desc_parts if p)
        if not description:
            continue
        rows.append(
            {
                "id": f"WO-HIST-311-{i + 1:04d}",
                "unit_id": unit_ids[i % len(unit_ids)],
                "category": _infer_category_from_311(rec.get("complaint_type", "")),
                "priority": _priority_from_311(rec.get("complaint_type", "")),
                "status": "closed",
                "description": description[:1000],
                "created_at": rec.get("created_date") or "",
                "incident_address": rec.get("incident_address") or "",
                "source": "nyc_311",
            }
        )

    _write_csv(
        outfile,
        rows,
        [
            "id",
            "unit_id",
            "category",
            "priority",
            "status",
            "description",
            "created_at",
            "incident_address",
            "source",
        ],
    )
    return outfile


def download_dataset(name: str, *, force: bool = False) -> Path:
    cfg = datasets_config()
    dl = cfg["downloads"][name]
    outfile = _cache_path(dl["outfile"])
    if force and outfile.exists():
        outfile.unlink()

    source = dl["source"]
    if source == "huggingface":
        if name == "propertypilot":
            return download_propertypilot(dl)
    if source == "huggingface_file":
        if name == "cuad_qa":
            return download_cuad_clauses(dl)
    if source == "nyc_open_data":
        return download_nyc_311(dl)

    raise ValueError(f"Unknown dataset: {name}")


def download_all(*, force: bool = False) -> list[Path]:
    cfg = datasets_config()
    paths: list[Path] = []
    for name in cfg["downloads"]:
        paths.append(download_dataset(name, force=force))
    return paths


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _map_priority(value: str) -> str:
    v = value.lower()
    if v in {"urgent", "emergency", "critical"}:
        return "urgent"
    if v in {"high", "same_day"}:
        return "high"
    if v in {"low"}:
        return "low"
    return "normal"


def _infer_category_from_311(complaint_type: str) -> str:
    ct = complaint_type.upper()
    if "HEAT" in ct or "HOT WATER" in ct:
        return "hvac"
    if "PLUMB" in ct:
        return "plumbing"
    if "ELECTRIC" in ct:
        return "electrical"
    if "PAINT" in ct or "PLASTER" in ct:
        return "general"
    return "general"


def _priority_from_311(complaint_type: str) -> str:
    ct = complaint_type.upper()
    if "HEAT" in ct or "HOT WATER" in ct or "ELECTRIC" in ct:
        return "urgent"
    return "normal"
