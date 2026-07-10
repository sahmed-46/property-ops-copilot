from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from src.models import ApprovalStatus, TicketPriority, TicketStatus, WorkOrder


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class Repository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_unit(self, unit_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT u.*, p.name AS property_name, p.address "
            "FROM units u JOIN properties p ON p.id = u.property_id WHERE u.id = ?",
            (unit_id,),
        ).fetchone()
        return dict(row) if row else None

    def list_units(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT u.id, u.label, p.name AS property_name FROM units u "
            "JOIN properties p ON p.id = u.property_id ORDER BY u.id"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_lease_for_unit(self, unit_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM leases WHERE unit_id = ? ORDER BY start_date DESC LIMIT 1",
            (unit_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_clauses(self, lease_id: str | None = None) -> list[dict]:
        if lease_id:
            rows = self.conn.execute(
                "SELECT * FROM lease_clauses WHERE lease_id = ? ORDER BY section",
                (lease_id,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM lease_clauses ORDER BY lease_id, section"
            ).fetchall()
        return [dict(r) for r in rows]

    def create_work_order(
        self,
        unit_id: str,
        category: str,
        priority: TicketPriority,
        description: str,
    ) -> WorkOrder:
        wo_id = f"WO-{uuid.uuid4().hex[:8].upper()}"
        created = _utcnow()
        self.conn.execute(
            "INSERT INTO work_orders (id, unit_id, category, priority, status, description, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (wo_id, unit_id, category, priority.value, TicketStatus.OPEN.value, description, created),
        )
        self.conn.commit()
        return WorkOrder(
            id=wo_id,
            unit_id=unit_id,
            category=category,
            priority=priority,
            status=TicketStatus.OPEN,
            description=description,
            created_at=datetime.fromisoformat(created),
        )

    def get_work_order(self, wo_id: str) -> WorkOrder | None:
        row = self.conn.execute("SELECT * FROM work_orders WHERE id = ?", (wo_id,)).fetchone()
        if not row:
            return None
        return WorkOrder(
            id=row["id"],
            unit_id=row["unit_id"],
            category=row["category"],
            priority=TicketPriority(row["priority"]),
            status=TicketStatus(row["status"]),
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def log_audit(
        self,
        session_id: str,
        agent: str,
        tool: str,
        payload: dict,
        result: dict,
    ) -> None:
        self.conn.execute(
            "INSERT INTO audit_logs (session_id, agent, tool, payload_json, result_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, agent, tool, json.dumps(payload), json.dumps(result), _utcnow()),
        )
        self.conn.commit()

    def create_approval(self, session_id: str, reason: str, context: dict) -> str:
        approval_id = f"APR-{uuid.uuid4().hex[:8].upper()}"
        self.conn.execute(
            "INSERT INTO approval_queue (id, session_id, reason, status, context_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                approval_id,
                session_id,
                reason,
                ApprovalStatus.PENDING.value,
                json.dumps(context),
                _utcnow(),
            ),
        )
        self.conn.commit()
        return approval_id

    def recent_audit(self, limit: int = 20) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
