from __future__ import annotations

import csv
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

APP_DIR = Path.home() / ".altamimi_report"
DB_PATH = APP_DIR / "reports.db"


@dataclass(slots=True)
class ReportRecord:
    id: int
    created_at: str
    platform: str
    target_url: str
    reason: str
    notes: str
    status: str


def _connect() -> sqlite3.Connection:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with _connect() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                platform TEXT NOT NULL,
                target_url TEXT NOT NULL,
                reason TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'مسودة'
            )
            """
        )


def add_report(platform: str, target_url: str, reason: str, notes: str, status: str) -> int:
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    with _connect() as con:
        cur = con.execute(
            "INSERT INTO reports(created_at, platform, target_url, reason, notes, status) VALUES(?,?,?,?,?,?)",
            (now, platform, target_url, reason, notes, status),
        )
        return int(cur.lastrowid)


def list_reports() -> list[ReportRecord]:
    with _connect() as con:
        rows = con.execute(
            "SELECT id, created_at, platform, target_url, reason, notes, status FROM reports ORDER BY id DESC"
        ).fetchall()
    return [ReportRecord(**dict(row)) for row in rows]


def update_status(report_id: int, status: str) -> None:
    with _connect() as con:
        con.execute("UPDATE reports SET status=? WHERE id=?", (status, report_id))


def delete_report(report_id: int) -> None:
    with _connect() as con:
        con.execute("DELETE FROM reports WHERE id=?", (report_id,))


def export_csv(path: Path) -> None:
    records = list_reports()
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Created At", "Platform", "Target URL", "Reason", "Notes", "Status"])
        for r in records:
            writer.writerow([r.id, r.created_at, r.platform, r.target_url, r.reason, r.notes, r.status])
