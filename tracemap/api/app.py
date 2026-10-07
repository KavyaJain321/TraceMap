"""TraceMap HTTP API (+ serves the built React UI from frontend/dist)."""

from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

from ..config import REPO_ROOT, settings
from ..contracts import CrawlRecord, ScanResult
from ..storage import Store
from .scans import ScanManager, TargetRejected

FRONTEND = REPO_ROOT / "frontend" / "dist"


class ScanRequest(BaseModel):
    url: str
    mode: Literal["quick", "full"] = "quick"
    leak_test: bool = True
    consent: Literal["none", "optIn", "optOut"] = "none"
    device: Literal["mobile", "desktop"] = "mobile"


def create_app(store: Store | None = None) -> FastAPI:
    store = store or Store(settings.data_dir)
    manager = ScanManager(store)
    app = FastAPI(title="TraceMap", version="0.1.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.state.store, app.state.manager = store, manager

    @lru_cache(maxsize=4)
    def crawl_doc(scan_id: str) -> CrawlRecord | None:
        return store.load_doc(scan_id, "crawl", CrawlRecord)

    def scan_dir_or_404(scan_id: str):
        try:
            return store.scan_dir(scan_id)
        except ValueError:
            raise HTTPException(404, "unknown scan")

    @app.get("/api/health")
    def health():
        return {"ok": True, "allow_local": settings.allow_local_targets}

    @app.post("/api/scans")
    def create_scan(req: ScanRequest):
        try:
            scan_id = manager.submit(req.url, req.mode, req.leak_test, req.consent, req.device)
        except TargetRejected as e:
            raise HTTPException(400, str(e))
        return {"scan_id": scan_id}

    @app.get("/api/scans")
    def list_scans(limit: int = 30):
        return store.list_scans(min(max(limit, 1), 200))

    @app.get("/api/scans/{scan_id}")
    def get_scan(scan_id: str):
        scan_dir_or_404(scan_id)
        res = store.load_doc(scan_id, "result", ScanResult)
        if res is None:
            row = next((r for r in store.list_scans(500) if r["scan_id"] == scan_id), None)
            if row is None:
                raise HTTPException(404, "unknown scan")
            return JSONResponse({"scan_id": scan_id, "status": row["status"], "url": row["url"]})
        return JSONResponse(json.loads(res.model_dump_json()))

    @app.get("/api/scans/{scan_id}/events")
    async def stream_events(scan_id: str):
        scan_dir_or_404(scan_id)

        async def gen():
            n = 0
            idle = 0
            while True:
                events, done = manager.events_since(scan_id, n)
                for ev in events:
                    n += 1
                    yield f"data: {json.dumps(ev)}\n\n"
                if done and not events:
                    yield "event: end\ndata: {}\n\n"
                    return
                idle = 0 if events else idle + 1
                if idle and idle % 50 == 0:
                    yield ": keep-alive\n\n"
                await asyncio.sleep(0.3)

        return StreamingResponse(gen(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.get("/api/scans/{scan_id}/requests/{request_id}")
    def get_request(scan_id: str, request_id: str):
        """The raw captured request behind a finding ('show proof')."""
        scan_dir_or_404(scan_id)
        rec = crawl_doc(scan_id)
        if rec is None:
            raise HTTPException(404, "crawl not stored")
        for v in rec.visits:
            for r in v.requests:
                if r.request_id == request_id:
                    d = json.loads(r.model_dump_json())
                    d["profile"] = v.profile
                    d["page_url"] = v.pages[r.page_index].url if r.page_index < len(v.pages) else None
                    d["absolute_time"] = v.started_at + r.t
                    return d
        raise HTTPException(404, "request not found")

    @app.get("/api/blobs/{sha}")
    def get_blob(sha: str, kind: Literal["image", "text"] = "image"):
        data = store.get_blob(sha)
        if data is None:
            raise HTTPException(404, "not found")
        return Response(data, media_type="image/jpeg" if kind == "image" else "text/plain; charset=utf-8",
                        headers={"Cache-Control": "public, max-age=31536000, immutable"})

    # ------------------------------------------------------------------ built UI (single-page app)
    if FRONTEND.exists():
        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str):
            if path == "api" or path.startswith("api/"):
                raise HTTPException(404, "unknown API path")
            f = (FRONTEND / path).resolve()
            if path and f.is_file() and FRONTEND.resolve() in f.parents:
                return FileResponse(f)
            return FileResponse(FRONTEND / "index.html")

    return app
