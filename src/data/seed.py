from __future__ import annotations

import sqlite3

from src.db.connection import get_connection, init_schema


def seed_database(data: dict, conn: sqlite3.Connection | None = None) -> str:
    """Load a data bundle dict into SQLite. Returns database file path."""
    owns = conn is None
    conn = conn or get_connection()
    init_schema(conn)

    try:
        for table in (
            "work_orders",
            "audit_logs",
            "approval_queue",
            "lease_clauses",
            "leases",
            "tenants",
            "units",
            "properties",
        ):
            conn.execute(f"DELETE FROM {table}")

        for row in data["properties"]:
            conn.execute(
                "INSERT INTO properties (id, name, address) VALUES (?, ?, ?)",
                (row["id"], row["name"], row["address"]),
            )
        for row in data["units"]:
            conn.execute(
                "INSERT INTO units (id, property_id, label) VALUES (?, ?, ?)",
                (row["id"], row["property_id"], row["label"]),
            )
        for row in data.get("tenants", []):
            conn.execute(
                "INSERT INTO tenants (id, unit_id, name, email) VALUES (?, ?, ?, ?)",
                (row["id"], row["unit_id"], row["name"], row.get("email")),
            )
        for row in data["leases"]:
            conn.execute(
                "INSERT INTO leases (id, unit_id, start_date, end_date, renewal_notice_days, raw_text) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    row["id"],
                    row["unit_id"],
                    row["start_date"],
                    row["end_date"],
                    row["renewal_notice_days"],
                    row.get("raw_text"),
                ),
            )
        for row in data["lease_clauses"]:
            conn.execute(
                "INSERT INTO lease_clauses (id, lease_id, section, title, text) VALUES (?, ?, ?, ?, ?)",
                (row["id"], row["lease_id"], row["section"], row["title"], row["text"]),
            )
        for row in data.get("work_orders", []):
            conn.execute(
                "INSERT INTO work_orders (id, unit_id, category, priority, status, description, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    row["id"],
                    row["unit_id"],
                    row["category"],
                    row["priority"],
                    row["status"],
                    row["description"],
                    row["created_at"],
                ),
            )
        conn.commit()
        return conn.execute("PRAGMA database_list").fetchone()[2]
    finally:
        if owns:
            conn.close()
