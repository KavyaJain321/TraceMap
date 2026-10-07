import { useEffect, useRef, useState } from 'react';
import { api, ProgressEvent, ScanResult } from './api';
import Result from './Result';

const STAGES: { key: string; label: string }[] = [
  { key: 'crawl', label: 'Visit pages' },
  { key: 'leak', label: 'Test forms' },
  { key: 'detect', label: 'Identify companies' },
  { key: 'graph', label: 'Map ID sharing' },
  { key: 'done', label: 'Write report' },
];

function Live({ scanId, url, onDone }: { scanId: string; url?: string; onDone: () => void }) {
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const es = api.events(scanId);
    es.onmessage = (m) => setEvents((prev) => [...prev, JSON.parse(m.data)]);
    es.addEventListener('end', () => { es.close(); onDone(); });
    es.onerror = () => { /* EventSource retries automatically */ };
    return () => es.close();
  }, [scanId, onDone]);

  useEffect(() => { logRef.current?.scrollTo({ top: logRef.current.scrollHeight }); }, [events]);

  const t0 = events[0]?.t ?? 0;
  let stage = -1, pct = 2, requests = 0, third = 0, typed = 0, leaks: number | null = null;
  for (const e of events) {
    const i = STAGES.findIndex((s) => s.key === e.stage);
    if (i > stage) stage = i;
    if (typeof e.pct === 'number') pct = Math.max(pct, e.pct);
    if (typeof e.requests === 'number') requests = e.requests as number;
    if (typeof e.third_parties === 'number') third = Math.max(third, e.third_parties as number);
    if (e.stage === 'leak' && e.kind) typed += 1;
    if (typeof e.leaks === 'number') leaks = e.leaks as number;
  }
  // Rough progress between the explicit checkpoints: crawl fills 5-50%, the form test 50-78%.
  const crawlN = events.filter((e) => e.stage === 'crawl').length;
  const leakN = events.filter((e) => e.stage === 'leak').length;
  pct = Math.max(pct, Math.min(50, 5 + crawlN * 1.6), leakN ? Math.min(78, 50 + leakN * 4) : 0);
  const failed = events.some((e) => e.stage === 'error');

  return (
    <section>
      <div className="progress-head">
        <p className="eyebrow">Examination in progress</p>
        <h1 style={{ fontSize: 'clamp(26px, 4vw, 44px)', marginTop: 8, wordBreak: 'break-all' }}>{url ?? 'Starting…'}</h1>
      </div>
      <ol className="rail" aria-label="Scan stages">
        {STAGES.map((s, i) => (
          <li key={s.key} className={i < stage || (i === stage && s.key === 'done') ? 'done' : i === stage ? 'now' : ''}>
            <span className="dot" />{s.label}
          </li>
        ))}
      </ol>
      <div className="bar" role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100}>
        <i style={{ width: `${pct}%` }} />
      </div>
      <div className="counters" aria-live="polite">
        <div><b>{requests}</b><span>requests recorded</span></div>
        <div><b>{third}</b><span>other domains contacted</span></div>
        <div><b>{typed}</b><span>fields given test data</span></div>
        <div><b>{leaks ?? '…'}</b><span>leaks found</span></div>
      </div>
      <div className="log" ref={logRef} aria-label="Scan log">
        {events.map((e, i) => (
          <div key={i} className={e.stage === 'leak' && (e.kind || e.leaks) ? 'leak' : e.level === 'warn' || e.stage === 'error' ? 'warn' : ''}>
            <span className="t">{String(Math.max(0, Math.round(e.t - t0))).padStart(3, ' ')}s</span>{e.message}
          </div>
        ))}
        {events.length === 0 && <div className="t">Waiting for the browser…</div>}
      </div>
      {failed && <p className="error-box">The scan stopped with an error. The log above shows the last step that ran.</p>}
    </section>
  );
}

export default function ScanView({ scanId }: { scanId: string }) {
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    api.get(scanId).then(setResult).catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, [scanId, tick]);

  if (error) return <div className="error-box" style={{ marginTop: 40 }}>Could not open this case file: {error}</div>;
  if (!result) return <p className="muted" style={{ marginTop: 40 }}>Opening case file…</p>;
  if (result.status !== 'done' && result.status !== 'error') {
    return <Live scanId={scanId} url={result.url} onDone={() => setTick((t) => t + 1)} />;
  }
  if (result.status === 'error') {
    return (
      <div style={{ marginTop: 40 }}>
        <h1 style={{ fontSize: 34 }}>{result.site || result.url}</h1>
        <div className="error-box">The scan failed: {result.error}</div>
      </div>
    );
  }
  return <Result r={result} />;
}
