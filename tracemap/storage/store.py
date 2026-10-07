"""Persistence: JSON documents per scan, content-addressed blobs, SQLite index.

Layout under settings.data_dir:
    scans/<scan_id>/crawl.json     CrawlRecord (raw facts)
    scans/<scan_id>/result.json    ScanResult (interpreted)
    scans/<scan_id>/events.jsonl   progress log (for replaying the live view)
    blobs/<ab>/<sha256>            script bodies, screenshots (deduplicated across sites)
    index.sqlite                   one row per scan for listing/search

SQLite keeps the MVP dependency-free; the interface is small enough to swap for
Postgres later without touching the pipeline.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import time
import uuid
from pathlib import Path

from pydantic import BaseModel

_SCHEMA = """
CREATE TABLE IF NOT EXISTS scans (
    scan_id     TEXT PRIMARY KEY,
    url         TEXT NOT NULL,
    site        TEXT,
    mode        TEXT,
    status      TEXT NOT NULL,
    created_at  REAL NOT NULL,
    finished_at REAL,
    summary     TEXT
);
CREATE INDEX IF NOT EXISTS scans_site ON scans(site);
"""


class Store:
    def __init__(self, root: Path | str):
        self.root = Path(root)
        (self.root / "scans").mkdir(parents=True, exist_ok=True)
        (self.root / "blobs").mkdir(parents=True, exist_ok=True)
        self._db_path = self.root / "index.sqlite"
        self._lock = threading.Lock()
        with self._connect() as db:
            db.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path, timeout=30)

    # ------------------------------------------------------------------ blobs

    def put_blob(self, data: bytes) -> str:
        sha = hashlib.sha256(data).hexdigest()
        path = self.root / "blobs" / sha[:2] / sha
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(data)
            tmp.replace(path)
        return sha

    def get_blob(self, sha: str) -> bytes | None:
        if not sha or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            return None
        path = self.root / "blobs" / sha[:2] / sha
        return path.read_bytes() if path.exists() else None

    # ------------------------------------------------------------------ scan documents

    @staticmethod
    def new_scan_id() -> str:
        return time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]

    def scan_dir(self, scan_id: str) -> Path:
        if not scan_id or "/" in scan_id or "\\" in scan_id or ".." in scan_id:
            raise ValueError(f"bad scan id: {scan_id!r}")
        d = self.root / "scans" / scan_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save_doc(self, scan_id: str, name: str, model: BaseModel | dict) -> Path:
        path = self.scan_dir(scan_id) / f"{name}.json"
        text = model.model_dump_json() if isinstance(model, BaseModel) else json.dumps(model)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
        return path

    def load_doc(self, scan_id: str, name: str, model: type[BaseModel] | None = None):
        path = self.scan_dir(scan_id) / f"{name}.json"
        if not path.exists():
            return None
        text = path.read_text(encoding="utf-8")
        return model.model_validate_json(text) if model else json.loads(text)

    def append_event(self, scan_id: str, event: dict) -> None:
        with self._lock, open(self.scan_dir(scan_id) / "events.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def load_events(self, scan_id: str) -> list[dict]:
        path = self.scan_dir(scan_id) / "events.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    # ------------------------------------------------------------------ index

    def upsert_scan(self, scan_id: str, *, url: str, status: str, created_at: float, site: str | None = None,
                    mode: str | None = None, finished_at: float | None = None, summary: dict | None = None) -> None:
        with self._lock, self._connect() as db:
            db.execute(
                """INSERT INTO scans (scan_id, url, site, mode, status, created_at, finished_at, summary)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(scan_id) DO UPDATE SET
                     site=COALESCE(excluded.site, site), mode=COALESCE(excluded.mode, mode),
                     status=excluded.status, finished_at=excluded.finished_at,
                     summary=COALESCE(excluded.summary, summary)""",
                (scan_id, url, site, mode, status, created_at, finished_at,
                 json.dumps(summary) if summary is not None else None),
            )

    def list_scans(self, limit: int = 50) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM scans ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["summary"] = json.loads(d["summary"]) if d["summary"] else None
            out.append(d)
        return out
