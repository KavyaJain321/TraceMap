import { useEffect, useMemo, useState } from 'react';

interface Site { url: string; name: string; sector: string; scan_id: string; status: string; third_parties: number; trackers: number; companies: number; shared_id_edges: number; consent_banner: boolean; seconds: number }
interface SectorRow { sector: string; sites: number; completed: number; blocked: number; errors: number; median_trackers: number | null; median_third_parties: number | null; max_trackers: number | null; sites_with_id_sharing: number; banner_rate: number | null }
interface Report {
  name: string;
  totals: { sites: number; completed: number; blocked: number; errors: number; median_trackers: number | null; sites_with_trackers: number; sites_with_id_sharing: number; banner_rate: number | null; third_party_observations: number; unlisted_observations: number; unlisted_share: number | null; median_seconds: number | null };
  sectors: SectorRow[]; companies: { company: string; sites: number; by_sector: Record<string, number> }[];
  unlisted: { domain: string; sites: number }[]; sites: Site[];
}

const SECTOR_LABEL: Record<string, string> = { government: 'Government', banking: 'Banking', health: 'Health', ecommerce: 'E-commerce', edtech: 'Education' };
const pct = (x: number | null | undefined) => (x == null ? '–' : `${Math.round(x * 100)}%`);

type Tip = { x: number; y: number; text: string } | null;

/** One row per sector; one dot per completed site at its tracker count; ink tick = median. */
function DotStrip({ sites, sectors, onPick }: { sites: Site[]; sectors: SectorRow[]; onPick: (s: Site) => void }) {
  const [tip, setTip] = useState<Tip>(null);
  const done = sites.filter((s) => s.status === 'done');
  const max = Math.max(5, ...done.map((s) => s.trackers));
  const W = 760, L = 120, R = 24, ROW = 46, T = 10;
  const H = T + ROW * sectors.length + 30;
  const x = (v: number) => L + (v / max) * (W - L - R);
  const step = max > 40 ? 10 : max > 16 ? 5 : 2;
  const ticks = Array.from({ length: Math.floor(max / step) + 1 }, (_, i) => i * step);
  return (
    <div className="chart" onMouseLeave={() => setTip(null)}>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Tracking domains per site, by sector">
        {ticks.map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={T} y2={H - 24} className="grid" />
            <text x={x(t)} y={H - 8} className="axis" textAnchor="middle">{t}</text>
          </g>
        ))}
        {sectors.map((sec, i) => {
          const cy = T + ROW * i + ROW / 2;
          const pts = done.filter((s) => s.sector === sec.sector).sort((a, b) => a.trackers - b.trackers);
          const seen: Record<number, number> = {};
          return (
            <g key={sec.sector}>
              <text x={0} y={cy + 4} className="row-label">{SECTOR_LABEL[sec.sector] ?? sec.sector}</text>
              {sec.median_trackers != null && (
                <line x1={x(sec.median_trackers)} x2={x(sec.median_trackers)} y1={cy - 14} y2={cy + 14} className="median" />
              )}
              {pts.map((s) => {
                const k = (seen[s.trackers] = (seen[s.trackers] ?? 0) + 1) - 1;
                const dy = (k % 2 ? 1 : -1) * Math.ceil(k / 2) * 7; // jitter identical values
                const label = `${s.name || s.url}: ${s.trackers} tracking domains`;
                return (
                  <g key={s.url} className="dot" tabIndex={0} role="button" aria-label={label}
                     onMouseEnter={() => setTip({ x: x(s.trackers) / W * 100, y: cy + dy, text: label })}
                     onFocus={() => setTip({ x: x(s.trackers) / W * 100, y: cy + dy, text: label })}
                     onClick={() => onPick(s)} onKeyDown={(e) => { if (e.key === 'Enter') onPick(s); }}>
                    <circle cx={x(s.trackers)} cy={cy + dy} r={12} className="hit-area" />
                    <circle cx={x(s.trackers)} cy={cy + dy} r={5} />
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>
      {tip && <div className="tip" style={{ left: `${tip.x}%`, top: tip.y - 8 }}>{tip.text}</div>}
      <p className="chart-note">Each dot is one site; the dark tick is the sector median. Blocked sites are left out. Click a dot to open its case file.</p>
    </div>
  );
}

function CompanyBars({ rows, total }: { rows: Report['companies']; total: number }) {
  const [tip, setTip] = useState<Tip>(null);
  const top = rows.slice(0, 12);
  const W = 760, L = 190, R = 60, ROW = 30, T = 4;
  const H = T + ROW * top.length;
  const x = (v: number) => (v / Math.max(1, total)) * (W - L - R);
  return (
    <div className="chart" onMouseLeave={() => setTip(null)}>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Companies tracking on the most sites">
        {top.map((c, i) => {
          const y = T + ROW * i;
          const w = Math.max(4, x(c.sites));
          const label = `${c.company}: on ${c.sites} of ${total} sites (${Object.entries(c.by_sector).map(([s, n]) => `${SECTOR_LABEL[s] ?? s} ${n}`).join(', ')})`;
          return (
            <g key={c.company} tabIndex={0} aria-label={label}
               onMouseEnter={() => setTip({ x: (L + w) / W * 100, y: y + 6, text: label })}
               onFocus={() => setTip({ x: (L + w) / W * 100, y: y + 6, text: label })}>
              <text x={L - 10} y={y + 17} textAnchor="end" className="row-label">{c.company.slice(0, 26)}</text>
              <rect x={L} y={y + 6} width={W - L - R} height={16} className="hit-area" />
              <path className="bar" d={`M${L},${y + 6} h${w - 4} a4,4 0 0 1 4,4 v8 a4,4 0 0 1 -4,4 h${-(w - 4)} z`} />
              <text x={L + w + 8} y={y + 18} className="value">{c.sites}</text>
            </g>
          );
        })}
      </svg>
      {tip && <div className="tip" style={{ left: `${Math.min(tip.x, 70)}%`, top: tip.y - 8 }}>{tip.text}</div>}
    </div>
  );
}

export default function Pilot() {
  const [names, setNames] = useState<string[] | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [showTable, setShowTable] = useState(false);

  useEffect(() => { fetch('/api/pilots').then((r) => r.json()).then(setNames).catch(() => setNames([])); }, []);
  useEffect(() => {
    if (!names?.length) return;
    const load = () => fetch(`/api/pilots/${names[0]}`).then((r) => r.json()).then(setReport).catch((e) => setErr(String(e)));
    load();
    const t = window.setInterval(load, 15000); // the pilot may still be running
    return () => window.clearInterval(t);
  }, [names]);

  const open = (s: Site) => { window.location.hash = `#/scan/${s.scan_id}`; };
  const t = report?.totals;
  const running = useMemo(() => report && report.sites.length < 50, [report]);

  if (names && names.length === 0) return <div className="empty" style={{ marginTop: 40 }}>No pilot has been run yet. Run <code className="mono">python -m tracemap pilot data/corpus/pilot_50.csv</code>.</div>;
  if (err) return <div className="error-box" style={{ marginTop: 40 }}>{err}</div>;
  if (!report || !t) return <p className="muted" style={{ marginTop: 40 }}>Loading pilot…</p>;

  return (
    <section>
      <div className="progress-head">
        <p className="eyebrow">Pilot study · {report.name.replace(/_/g, ' ')} · passive scan, forms not tested</p>
        <h1 style={{ fontSize: 'clamp(28px, 4.4vw, 48px)', marginTop: 8 }}>What Indian websites load before you click anything</h1>
        <p className="muted" style={{ maxWidth: '70ch' }}>
          {t.sites} public landing pages, 10 per sector, visited once as a phone user with no cookie choice made.
          A convenience sample to test the pipeline — not yet the stratified study.
          {running && ' The pilot is still running; this page refreshes itself.'}
        </p>
      </div>
      <div className="ledger">
        <div><b>{t.completed}<small className="faint"> / {t.sites}</small></b><span>sites scanned</span></div>
        <div><b>{t.sites_with_trackers}</b><span>loaded trackers</span></div>
        <div><b>{t.median_trackers ?? '–'}</b><span>median tracking domains</span></div>
        <div><b>{t.sites_with_id_sharing}</b><span>possible ID sharing*</span></div>
        <div><b>{pct(t.banner_rate)}</b><span>showed a cookie banner</span></div>
        <div><b>{t.blocked}</b><span>blocked our browser</span></div>
      </div>

      <h2 style={{ margin: '34px 0 10px' }}>Tracking domains per site, by sector</h2>
      <DotStrip sites={report.sites} sectors={report.sectors} onPick={open} />

      <h2 style={{ margin: '34px 0 10px' }}>Who is present across these sites</h2>
      <CompanyBars rows={report.companies} total={t.completed} />

      <h2 style={{ margin: '34px 0 6px' }}>Third parties no global list recognises</h2>
      <p className="muted" style={{ marginTop: 0, maxWidth: '70ch' }}>
        {t.unlisted_observations} of {t.third_party_observations} third-party appearances ({pct(t.unlisted_share)}) were on none of the
        DuckDuckGo, Ghostery, Disconnect, third-party-web or filter lists. These feed the India tracker list (research question 1);
        each needs checking by two people before it is labelled.
      </p>
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Domain</th><th className="num">Sites</th></tr></thead>
          <tbody>{report.unlisted.slice(0, 15).map((u) => <tr key={u.domain}><td className="mono">{u.domain}</td><td className="num">{u.sites}</td></tr>)}</tbody>
        </table>
      </div>

      <h2 style={{ margin: '34px 0 10px' }}>By sector</h2>
      <div className="table-wrap">
        <table className="table">
          <thead><tr><th>Sector</th><th className="num">Scanned</th><th className="num">Blocked</th><th className="num">Median trackers</th><th className="num">Most</th><th className="num">Possible ID sharing*</th><th className="num">Banner</th></tr></thead>
          <tbody>
            {report.sectors.map((s) => (
              <tr key={s.sector}>
                <td>{SECTOR_LABEL[s.sector] ?? s.sector}</td><td className="num">{s.completed}/{s.sites}</td><td className="num">{s.blocked}</td>
                <td className="num">{s.median_trackers ?? '–'}</td><td className="num">{s.max_trackers ?? '–'}</td>
                <td className="num">{s.sites_with_id_sharing}</td><td className="num">{pct(s.banner_rate)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button className="btn ghost small" style={{ marginTop: 22 }} onClick={() => setShowTable(!showTable)}>
        {showTable ? 'Hide' : 'Show'} all {report.sites.length} sites
      </button>
      {showTable && (
        <div className="table-wrap" style={{ marginTop: 12 }}>
          <table className="table">
            <thead><tr><th>Site</th><th>Sector</th><th className="num">Trackers</th><th className="num">Third parties</th><th className="num">Possible ID links*</th><th>Banner</th><th>Status</th></tr></thead>
            <tbody>
              {report.sites.map((s) => (
                <tr key={s.url} className="clickable" onClick={() => open(s)}>
                  <td>{s.name || s.url}<div className="faint mono">{s.url}</div></td><td>{SECTOR_LABEL[s.sector] ?? s.sector}</td>
                  <td className="num">{s.trackers}</td><td className="num">{s.third_parties}</td><td className="num">{s.shared_id_edges}</td>
                  <td>{s.consent_banner ? 'Yes' : 'No'}</td><td>{s.status === 'blocked' ? 'Blocked' : s.status === 'done' ? 'Done' : 'Error'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="score-note" style={{ marginTop: 26 }}>
        * Quick scans use one visitor, so identifier sharing is a candidate until a thorough scan (two separate visitors) confirms it.
        Limits: one visit per site, landing pages only, from one Indian connection; trackers loaded later or server-side are not counted.
        Form leak tests on real sites wait for ethics approval.
      </p>
    </section>
  );
}
