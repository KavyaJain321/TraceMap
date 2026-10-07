"""Data contracts between pipeline stages.

Every stage reads and writes only these models, so the four sub-teams can work in
parallel against saved JSON fixtures. Bump SCHEMA_VERSION on any breaking change.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SCHEMA_VERSION = "1.0"


class _M(BaseModel):
    model_config = {"extra": "ignore"}


# --------------------------------------------------------------------------- Stage 1: crawl


class Initiator(_M):
    type: str = "other"  # parser | script | preload | redirect | other
    url: str | None = None  # document or script that caused the request
    stack_urls: list[str] = Field(default_factory=list)  # script URLs, innermost first


class Request(_M):
    request_id: str
    url: str
    method: str = "GET"
    resource_type: str = "Other"  # CDP resource type: Document, Script, XHR, Fetch, Image, Ping, ...
    page_index: int = 0  # which page of the visit (0 = landing)
    frame_url: str | None = None
    initiator: Initiator = Field(default_factory=Initiator)
    headers: dict[str, str] = Field(default_factory=dict)
    post_data: str | None = None
    t: float = 0.0  # seconds since visit start
    redirect_from: str | None = None  # request_id of the hop that redirected here
    status: int | None = None
    response_headers: dict[str, str] = Field(default_factory=dict)
    set_cookies: list[str] = Field(default_factory=list)
    remote_ip: str | None = None
    failed: str | None = None

    @property
    def initiator_script(self) -> str | None:
        return self.initiator.stack_urls[0] if self.initiator.stack_urls else None


class Script(_M):
    url: str  # external URL, or "inline:<page_url>#<n>"
    sha256: str  # body stored in the blob store under this hash
    size: int
    inline: bool = False
    page_index: int = 0


class Cookie(_M):
    name: str
    value: str
    domain: str
    path: str = "/"
    expires: float = -1  # epoch seconds, -1 = session cookie
    http_only: bool = False
    secure: bool = False
    same_site: str | None = None
    set_by: Literal["http", "js", "unknown"] = "unknown"
    setter_url: str | None = None  # response URL (http) or script URL (js)


class StorageItem(_M):
    origin: str
    key: str
    value: str
    kind: Literal["local", "session"] = "local"


class APICall(_M):
    """A JS API touched by a script (aggregated per api + script)."""

    api: str  # e.g. "HTMLCanvasElement.toDataURL"
    script_url: str  # "" when the caller could not be attributed
    count: int = 1
    sample_args: list[str] = Field(default_factory=list)
    page_index: int = 0


class PageVisit(_M):
    index: int
    url: str
    final_url: str | None = None
    status: Literal["ok", "blocked", "error", "timeout"] = "ok"
    http_status: int | None = None
    block_reason: str | None = None
    error: str | None = None
    title: str | None = None
    screenshot_sha256: str | None = None
    load_ms: int | None = None


class ConsentInfo(_M):
    mode: str = "none"
    cmp_detected: str | None = None
    popup_found: bool = False
    action_result: bool | None = None  # True if opt-in/opt-out succeeded
    errors: list[str] = Field(default_factory=list)


class Visit(_M):
    """One browser profile visiting the site's pages in order."""

    profile: str  # "A", "B" (fresh second user), "A2" (A revisiting), "L" (leak test)
    started_at: float
    finished_at: float | None = None
    pages: list[PageVisit] = Field(default_factory=list)
    requests: list[Request] = Field(default_factory=list)
    scripts: list[Script] = Field(default_factory=list)
    cookies: list[Cookie] = Field(default_factory=list)
    storage: list[StorageItem] = Field(default_factory=list)
    api_calls: list[APICall] = Field(default_factory=list)
    consent: ConsentInfo = Field(default_factory=ConsentInfo)


class CrawlRecord(_M):
    schema_version: str = SCHEMA_VERSION
    crawl_id: str
    input_url: str
    site: str  # eTLD+1 of the landing page
    started_at: float
    finished_at: float | None = None
    status: Literal["ok", "partial", "blocked", "error"] = "ok"
    config: dict = Field(default_factory=dict)  # CrawlConfig snapshot + browser version
    visits: list[Visit] = Field(default_factory=list)

    def visit(self, profile: str) -> Visit | None:
        return next((v for v in self.visits if v.profile == profile), None)


# --------------------------------------------------------------------------- Stage 2: detect

Category = Literal[
    "ad", "analytics", "social", "session_replay", "tag_manager", "fingerprinting", "functional", "unknown"
]


class DetectedParty(_M):
    domain: str  # eTLD+1
    owner: str | None = None  # entity / company
    category: Category = "unknown"
    is_tracker: bool = False
    first_party: bool = False
    cloaked: bool = False  # first-party subdomain CNAME'd to a tracker
    same_owner_as_site: bool = False  # e.g. a site's own CDN domain (flixcart.com for flipkart.com)
    request_count: int = 0
    hosts: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)  # which lists said so
    evidence: list[str] = Field(default_factory=list)  # e.g. matched filter rules


class RiskyScript(_M):
    src: str
    domain: str
    flags: list[str] = Field(default_factory=list)  # canvas_fp, audio_fp, webgl_fp, reads_form, keylogger, ...
    evidence: dict[str, list[str]] = Field(default_factory=dict)  # flag -> APIs that triggered it


# --------------------------------------------------------------------------- Stage 3: ID-flow graph


class GraphNode(_M):
    id: str  # eTLD+1
    owner: str | None = None
    category: str = "unknown"
    is_tracker: bool = False
    first_party: bool = False
    degree: int = 0
    betweenness: float = 0.0


class CollusionEdge(_M):
    """Edge in the identifier-flow network. Evidence, not proof of intent."""

    a: str
    b: str
    kind: Literal["loads", "redirect", "shared_id"]
    evidence_type: str | None = None  # url_param | path | cookie | post_body | redirect | referer
    shared_value_hash: str | None = None  # never the raw identifier
    confidence: float = 1.0
    same_entity: bool = False
    count: int = 1
    request_ids: list[str] = Field(default_factory=list)


class SiteGraph(_M):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[CollusionEdge] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- Stage 4: leak trace


class Canary(_M):
    canary_id: str
    kind: Literal["email", "phone"]
    value: str
    site: str
    created_at: float


class FieldFilled(_M):
    canary_id: str
    kind: Literal["email", "phone"]
    page_url: str
    frame_url: str
    descriptor: str  # human readable: name/id/placeholder of the field
    typed_at: float  # epoch seconds when typing started
    in_iframe: bool = False


class LeakEvent(_M):
    canary_id: str
    kind: Literal["email", "phone"]
    field: str  # descriptor of the field that was filled
    field_typed_at: float | None = None  # epoch seconds typing started in that field
    recipient_domain: str
    recipient_host: str
    recipient_owner: str | None = None
    channel: str  # url | post_body | cookie | referer | header:<name>
    encoding: str  # e.g. "plain", "sha256(lower)", "base64(+91 variant)"
    matched: str | None = None  # the exact string found (for highlighting in the proof view)
    where: str = "raw"  # "raw" or how the payload was decoded before the match
    request_id: str
    request_url: str
    ms_after_typing: int
    before_submit: bool = True  # TraceMap never submits forms
    first_party: bool = False
    confidence: float = 0.99


class LeakReport(_M):
    tested: bool = False
    pages_tried: list[str] = Field(default_factory=list)
    fields: list[FieldFilled] = Field(default_factory=list)
    canaries: list[Canary] = Field(default_factory=list)
    leaks: list[LeakEvent] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- Stage 5: results


class Finding(_M):
    severity: Literal["high", "medium", "low", "info"]
    code: str  # stable reason code, e.g. LEAK_BEFORE_SUBMIT
    title: str  # plain-English one-liner
    detail: str | None = None
    request_ids: list[str] = Field(default_factory=list)  # links to proof


class ScanSummary(_M):
    pages_visited: int = 0
    requests: int = 0
    third_parties: int = 0
    trackers: int = 0
    companies: int = 0
    tracking_cookies: int = 0
    leaks: int = 0
    leak_recipients: int = 0
    shared_id_edges: int = 0
    risky_scripts: int = 0
    blocked: bool = False
    consent_banner: bool = False


class RiskResult(_M):
    """Validated scorecard arrives in Phase 9; until then score stays None."""

    url: str
    score: float | None = None
    subscores: dict[str, float] = Field(default_factory=dict)
    reasons: list[str] = Field(default_factory=list)


class ScanResult(_M):
    schema_version: str = SCHEMA_VERSION
    scan_id: str
    url: str
    site: str
    mode: str
    status: Literal["running", "done", "error"] = "running"
    error: str | None = None
    created_at: float
    finished_at: float | None = None
    summary: ScanSummary = Field(default_factory=ScanSummary)
    findings: list[Finding] = Field(default_factory=list)
    parties: list[DetectedParty] = Field(default_factory=list)
    risky_scripts: list[RiskyScript] = Field(default_factory=list)
    leaks: LeakReport = Field(default_factory=LeakReport)
    graph: SiteGraph = Field(default_factory=SiteGraph)
    risk: RiskResult | None = None
    screenshot_sha256: str | None = None
