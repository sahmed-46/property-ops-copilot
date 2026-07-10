# Data layout

| Path | Committed? | Purpose |
|------|------------|---------|
| `data/sample/seed.json` | Yes | Minimal demo seed (works offline, no download) |
| `data/cache/` | No (gitignored) | Downloaded CSVs, reused on every `init_data.py` run |
| `data/runtime/` | No (gitignored) | SQLite database built from sample + cache |

## One-time download

```bash
pip install -r requirements.txt
python scripts/download_datasets.py
```

Downloads (if missing) into `data/cache/`:
- `cuad_clauses.csv` — from [CUAD master clauses](https://huggingface.co/datasets/theatticusproject/cuad)
- `propertypilot_tickets.csv` — from [PropertyPilot tickets](https://huggingface.co/datasets/Matanech/property-pilot-tickets)
- `nyc_311_housing_sample.csv` — filtered NYC 311 housing complaints

Re-download: `python scripts/download_datasets.py --force`

## Build database

```bash
python scripts/init_data.py          # sample + cache (cache optional)
python scripts/init_data.py --sample-only   # seed.json only
```

The app reads **only** `data/runtime/property_ops.db` at runtime — never Hugging Face or NYC APIs.
