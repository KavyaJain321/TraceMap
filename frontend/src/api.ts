// Types mirror tracemap/contracts.py (only the fields the UI uses).

export type Severity = 'high' | 'medium' | 'low' | 'info';

export interface Finding { severity: Severity; code: string; title: string; detail?: string | null; request_ids: string[] }
export interface Party {
  domain: string; owner?: string | null; category: string; is_tracker: boolean; first_party: boolean;
  cloaked: boolean; same_owner_as_site?: boolean; request_count: number; hosts: string[]; sources: string[]; evidence: string[];
}
export interface RiskyScript { src: string; domain: string; flags: string[]; evidence: Record<string, string[]> }
export interface GraphNode { id: string; owner?: string | null; category: string; is_tracker: boolean; first_party: boolean; degree: number; betweenness: number }
export interface GraphEdge {
  a: string; b: string; kind: 'loads' | 'redirect' | 'shared_id'; evidence_type?: string | null;
  confidence: number; same_entity: boolean; count: number; request_ids: string[];
}
export interface Canary { canary_id: string; kind: 'email' | 'phone'; value: string }
export interface FieldFilled { canary_id: string; kind: string; page_url: string; frame_url: string; descriptor: string; typed_at: number; in_iframe: boolean }
export interface LeakEvent {
  canary_id: string; kind: 'email' | 'phone'; field: string; field_typed_at?: number | null; recipient_domain: string; recipient_host: string;
  recipient_owner?: string | null; channel: string; encoding: string; matched?: string | null; where: string;
  request_id: string; request_url: string; ms_after_typing: number; before_submit: boolean; first_party: boolean; confidence: number;
}
export interface Summary {
  pages_visited: number; requests: number; third_parties: number; trackers: number; companies: number;
  tracking_cookies: number; leaks: number; leak_recipients: number; shared_id_edges: number; risky_scripts: number;
  blocked: boolean; consent_banner: boolean;
}
export interface ScanResult {
  scan_id: string; url: string; site: string; mode: string; status: 'running' | 'queued' | 'done' | 'error';
  error?: string | null; created_at: number; finished_at?: number | null; summary: Summary; findings: Finding[];
  parties: Party[]; risky_scripts: RiskyScript[];
  leaks: { tested: boolean; pages_tried: string[]; fields: FieldFilled[]; canaries: Canary[]; leaks: LeakEvent[]; notes: string[] };
  graph: { nodes: GraphNode[]; edges: GraphEdge[]; notes: string[] };
  screenshot_sha256?: string | null;
}
export interface ScanRow { scan_id: string; url: string; site?: string; mode?: string; status: string; created_at: number; summary?: Summary | null }
export interface ProgressEvent { stage: string; message: string; t: number; pct?: number; level?: string; [k: string]: unknown }
export interface CapturedRequest {
  request_id: string; url: string; method: string; resource_type: string; profile: string; page_url?: string | null;
  initiator: { type: string; url?: string | null; stack_urls: string[] }; headers: Record<string, string>;
  post_data?: string | null; status?: number | null; t: number; absolute_time: number; redirect_from?: string | null;
}
export interface StartScan { url: string; mode: 'quick' | 'full'; leak_test: boolean; consent: 'none' | 'optIn' | 'optOut'; device: 'mobile' | 'desktop' }

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try { const b = await res.json(); if (b?.detail) msg = typeof b.detail === 'string' ? b.detail : JSON.stringify(b.detail); } catch { /* not json */ }
    throw new Error(msg);
  }
  return res.json() as Promise<T>;
}

export const api = {
  start: (body: StartScan) =>
    fetch('/api/scans', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then((r) => json<{ scan_id: string }>(r)),
  list: () => fetch('/api/scans?limit=30').then((r) => json<ScanRow[]>(r)),
  get: (id: string) => fetch(`/api/scans/${encodeURIComponent(id)}`).then((r) => json<ScanResult>(r)),
  request: (id: string, rid: string) =>
    fetch(`/api/scans/${encodeURIComponent(id)}/requests/${encodeURIComponent(rid)}`).then((r) => json<CapturedRequest>(r)),
  events: (id: string) => new EventSource(`/api/scans/${encodeURIComponent(id)}/events`),
  blobUrl: (sha: string) => `/api/blobs/${sha}`,
};

export const CATEGORY_LABEL: Record<string, string> = {
  ad: 'Advertising', analytics: 'Analytics', social: 'Social', session_replay: 'Session recording',
  tag_manager: 'Tag manager', fingerprinting: 'Fingerprinting', functional: 'Functional', unknown: 'Unclassified',
};

export function who(owner: string | null | undefined, domain: string): string {
  return owner && !domain.toLowerCase().includes(owner.toLowerCase()) ? owner : domain;
}
