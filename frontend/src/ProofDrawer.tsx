import { Fragment, ReactNode, useEffect, useRef, useState } from 'react';
import { api, CapturedRequest, Canary, LeakEvent } from './api';

export interface Proof { scanId: string; requestIds: string[]; title: string; leak?: LeakEvent; canaries: Canary[] }

function highlight(text: string, needle?: string | null): ReactNode {
  if (!needle || !text.includes(needle)) return text;
  const parts = text.split(needle);
  return parts.map((p, i) => (
    <Fragment key={i}>{p}{i < parts.length - 1 && <mark>{needle}</mark>}</Fragment>
  ));
}

function safeDecode(s: string): string {
  try { return decodeURIComponent(s.replace(/\+/g, ' ')); } catch { return s; }
}

const CHANNEL: Record<string, string> = {
  url: 'in the web address of the request', post_body: 'in the body of the request', cookie: 'in a cookie',
  referer: 'in the Referer header (the page address)',
};

export default function ProofDrawer({ proof, onClose }: { proof: Proof; onClose: () => void }) {
  const [i, setI] = useState(0);
  const [req, setReq] = useState<CapturedRequest | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const rid = proof.requestIds[i];
  const leak = proof.leak && proof.leak.request_id === rid ? proof.leak : undefined;
  const needle = leak?.where === 'raw' ? leak.matched : undefined;

  useEffect(() => { closeRef.current?.focus(); }, []);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);
  useEffect(() => {
    setReq(null); setErr(null);
    api.request(proof.scanId, rid).then(setReq).catch((e) => setErr(e instanceof Error ? e.message : String(e)));
  }, [proof.scanId, rid]);

  const canary = leak ? proof.canaries.find((c) => c.canary_id === leak.canary_id) : undefined;
  const headers = req ? Object.entries(req.headers).filter(([k]) => !k.startsWith(':')) : [];

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <aside className="drawer" role="dialog" aria-modal="true" aria-label="Proof">
        <header>
          <div>
            <p className="eyebrow">Proof · captured request</p>
            <h2 style={{ marginTop: 6 }}>{proof.title}</h2>
          </div>
          <button ref={closeRef} className="btn ghost small" onClick={onClose}>Close</button>
        </header>

        {proof.requestIds.length > 1 && (
          <p className="muted" style={{ fontSize: 14 }}>
            Request {i + 1} of {proof.requestIds.length}{' '}
            <button className="btn ghost small" disabled={i === 0} onClick={() => setI(i - 1)}>Previous</button>{' '}
            <button className="btn ghost small" disabled={i === proof.requestIds.length - 1} onClick={() => setI(i + 1)}>Next</button>
          </p>
        )}

        {leak && (
          <dl className="kv">
            <dt>We typed</dt><dd><code className="mono">{canary?.value ?? leak.kind}</code> into “{leak.field}”</dd>
            <dt>It left as</dt><dd>{leak.encoding} {CHANNEL[leak.channel] ?? `in ${leak.channel}`}</dd>
            <dt>Sent to</dt><dd>{leak.recipient_owner ? `${leak.recipient_owner} · ` : ''}<span className="mono">{leak.recipient_host}</span></dd>
            <dt>Timing</dt><dd>{(leak.ms_after_typing / 1000).toFixed(1)}s after typing, before any Submit</dd>
          </dl>
        )}

        {err && <div className="error-box">Could not load this request: {err}</div>}
        {!req && !err && <p className="muted">Loading request…</p>}
        {req && (
          <>
            <dl className="kv">
              <dt>Method</dt><dd className="mono">{req.method} · {req.resource_type}{req.status ? ` · HTTP ${req.status}` : ''}</dd>
              <dt>Sent by</dt><dd className="mono">{req.initiator.stack_urls[0] ?? req.initiator.url ?? req.initiator.type}</dd>
              <dt>On page</dt><dd className="mono">{req.page_url}</dd>
              <dt>Browser profile</dt><dd>{req.profile === 'L' ? 'Leak test visitor' : `Visitor ${req.profile}`}</dd>
              <dt>Captured at</dt><dd>{new Date(req.absolute_time * 1000).toLocaleString('en-IN')}</dd>
            </dl>
            <h3>Request address</h3>
            <div className="evidence">{highlight(req.url, needle)}</div>
            {req.post_data && (
              <>
                <h3>Request body</h3>
                <div className="evidence">{highlight(req.post_data, needle)}</div>
                {leak && leak.where !== 'raw' && leak.matched && (
                  <>
                    <h3>Body after {leak.where.replace('-decoded', ' decoding')}</h3>
                    <div className="evidence">{highlight(safeDecode(req.post_data), leak.matched)}</div>
                  </>
                )}
              </>
            )}
            {leak && leak.where !== 'raw' && !req.post_data && leak.matched && (
              <>
                <h3>Address after decoding</h3>
                <div className="evidence">{highlight(safeDecode(req.url), leak.matched)}</div>
              </>
            )}
            <details>
              <summary>Request headers ({headers.length})</summary>
              <div className="evidence">
                {headers.map(([k, v]) => <div key={k}><b>{k}:</b> {highlight(v, needle)}</div>)}
              </div>
            </details>
          </>
        )}
      </aside>
    </>
  );
}
