import { useEffect, useMemo, useState } from 'react';
import { LeakEvent, ScanResult, who } from './api';

const W = 1000, LEFT = 190, RIGHT = 30, TOP = 46, LANE = 58;

function prefersReducedMotion() {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
}

export default function LeakReplay({ r, onPick }: { r: ScanResult; onPick: (e: LeakEvent) => void }) {
  const { fields, canaries, tested, notes } = r.leaks;
  const leaks = useMemo(() => r.leaks.leaks.filter((e) => !e.first_party), [r]);

  const model = useMemo(() => {
    if (!fields.length) return null;
    const t0 = Math.min(...fields.map((f) => f.typed_at));
    const firstTyped: Record<string, number> = {};
    for (const f of fields) firstTyped[f.canary_id] = Math.min(firstTyped[f.canary_id] ?? Infinity, f.typed_at);
    const hits = leaks.map((e) => {
      const src = (e.field_typed_at ?? firstTyped[e.canary_id]) - t0;
      return { e, src, t: src + e.ms_after_typing / 1000 };
    });
    const recipients: string[] = [];
    for (const h of [...hits].sort((a, b) => a.t - b.t)) if (!recipients.includes(h.e.recipient_domain)) recipients.push(h.e.recipient_domain);
    const typed = fields.map((f) => ({ f, t: f.typed_at - t0 }));
    const tmax = Math.max(1, ...hits.map((h) => h.t), ...typed.map((x) => x.t)) * 1.08 + 0.4;
    return { hits, recipients, typed, tmax };
  }, [fields, leaks]);

  const [play, setPlay] = useState(0);
  const [running, setRunning] = useState(false);
  useEffect(() => {
    if (!model) return;
    if (prefersReducedMotion()) { setPlay(model.tmax); return; }
    setRunning(true);
  }, [model]);
  useEffect(() => {
    if (!running || !model) return;
    let raf = 0;
    const start = performance.now() - (play / model.tmax) * 5200;
    const step = (now: number) => {
      const p = Math.min(1, (now - start) / 5200);
      setPlay(p * model.tmax);
      if (p < 1) raf = requestAnimationFrame(step); else setRunning(false);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running, model]);

  const canaryLine = (
    <div className="canaries">
      {canaries.map((c) => (
        <span key={c.canary_id}>Test {c.kind}: <code>{c.value}</code></span>
      ))}
    </div>
  );

  if (!tested) return <div className="empty">The form test was switched off for this scan.</div>;
  if (!model) return <div className="empty">No email or phone field was found to type into. {notes.join(' ')}</div>;

  const { hits, recipients, typed, tmax } = model;
  const H = TOP + LANE * (recipients.length + 1) + 24;
  const x = (t: number) => LEFT + (t / tmax) * (W - LEFT - RIGHT);
  const laneY = (i: number) => TOP + LANE * i + LANE / 2;
  const step = tmax > 12 ? 2 : 1;
  const ticks = Array.from({ length: Math.floor(tmax / step) + 1 }, (_, i) => i * step);
  const firstLabel = (owner: string | null | undefined, d: string) => who(owner, d);

  return (
    <section>
      <div className="replay">
        <div className="replay-head">
          <div>
            <h2>What left the browser while we typed</h2>
            <p className="muted" style={{ margin: '4px 0 0', fontSize: 14 }}>
              Time runs left to right. Each line is your test detail travelling to another company — before Submit was ever pressed.
            </p>
          </div>
          <button className="btn ghost small" onClick={() => { setPlay(0); setRunning(true); }} disabled={running}>
            {running ? 'Replaying…' : 'Replay'}
          </button>
        </div>
        {canaryLine}
        <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Timeline of ${hits.length} leak events to ${recipients.length} companies`}>
          {ticks.map((t) => (
            <g key={t}>
              <line x1={x(t)} x2={x(t)} y1={TOP - 6} y2={H - 22} stroke="var(--rule-soft)" />
              <text className="axis" x={x(t)} y={H - 6} textAnchor="middle">{t}s</text>
            </g>
          ))}
          {/* lanes */}
          <text className="lane-label" x={0} y={laneY(0) - 2}>You typed</text>
          <text className="lane-sub" x={0} y={laneY(0) + 14}>{fields.length} field{fields.length === 1 ? '' : 's'}</text>
          <line x1={LEFT} x2={W - RIGHT} y1={laneY(0)} y2={laneY(0)} stroke="var(--ink)" strokeWidth="1.5" />
          {recipients.map((d, i) => {
            const ev = hits.find((h) => h.e.recipient_domain === d)!.e;
            return (
              <g key={d}>
                <text className="lane-label" x={0} y={laneY(i + 1) - 2}>{firstLabel(ev.recipient_owner, d).slice(0, 24)}</text>
                <text className="lane-sub" x={0} y={laneY(i + 1) + 14}>{d.slice(0, 26)}</text>
                <line x1={LEFT} x2={W - RIGHT} y1={laneY(i + 1)} y2={laneY(i + 1)} stroke="var(--rule)" strokeDasharray="2 4" />
              </g>
            );
          })}
          {/* typing marks */}
          {typed.map(({ f, t }, i) => (
            <g key={i} className="typed" opacity={play >= t ? 1 : 0.25}>
              <rect x={x(t) - 4} y={laneY(0) - 9} width={8} height={18} rx={2} />
              <text className="lane-sub" x={x(t) + 8} y={laneY(0) - 12}>{f.kind}{f.in_iframe ? ' (iframe)' : ''}</text>
            </g>
          ))}
          {/* traces + hits */}
          {hits.map(({ e, t, src }, i) => {
            const lane = recipients.indexOf(e.recipient_domain) + 1;
            const x1 = x(src), y1 = laneY(0), x2 = x(t), y2 = laneY(lane);
            const shown = play >= t;
            const label = `${e.kind} sent to ${who(e.recipient_owner, e.recipient_domain)} as ${e.encoding}, ${(e.ms_after_typing / 1000).toFixed(1)} seconds after typing`;
            return (
              <g key={i}>
                <path className="trace-line" pathLength={1} strokeDasharray="1" strokeDashoffset={shown ? 0 : 1}
                      style={{ transition: 'stroke-dashoffset 0.55s ease-out' }}
                      d={`M${x1},${y1} C${x1 + 40},${y1 + (y2 - y1) * 0.55} ${x2 - 40},${y2 - (y2 - y1) * 0.45} ${x2},${y2}`} />
                <g className="hit" tabIndex={0} role="button" aria-label={label} opacity={shown ? 1 : 0}
                   onClick={() => onPick(e)} onKeyDown={(k) => { if (k.key === 'Enter' || k.key === ' ') { k.preventDefault(); onPick(e); } }}>
                  <title>{label}</title>
                  <circle cx={x2} cy={y2} r={8} />
                  <text className="lane-sub" x={x2 + 12} y={y2 + 4}>{e.kind} · {e.encoding.split(' inside ')[0]}</text>
                </g>
              </g>
            );
          })}
          {running && <line className="playhead" x1={x(play)} x2={x(play)} y1={TOP - 10} y2={H - 22} />}
        </svg>
        <div className="legend">
          <span><i style={{ background: 'var(--ink)', borderRadius: 2 }} />Moment we typed a test detail</span>
          <span><i style={{ background: 'var(--stamp)' }} />Request carrying it to another company (click for proof)</span>
        </div>
      </div>

      {hits.length === 0 ? (
        <div className="empty" style={{ marginTop: 18 }}>
          We typed into {fields.length} field{fields.length === 1 ? '' : 's'} and none of the test details were seen going to another company.
          Data could still be shared from the site's servers after you submit, which a browser cannot observe.
        </div>
      ) : (
        <div className="table-wrap" style={{ marginTop: 22 }}>
          <table className="table">
            <thead><tr><th className="num">After</th><th>Company</th><th>What</th><th>How it was disguised</th><th>Where in the request</th><th /></tr></thead>
            <tbody>
              {[...hits].sort((a, b) => a.t - b.t).map(({ e }, i) => (
                <tr key={i}>
                  <td className="num">{(e.ms_after_typing / 1000).toFixed(1)}s</td>
                  <td>{who(e.recipient_owner, e.recipient_domain)}<div className="faint mono">{e.recipient_host}</div></td>
                  <td>{e.kind === 'email' ? 'Email' : 'Phone'}</td>
                  <td className="mono">{e.encoding}</td>
                  <td>{e.channel.replace('_', ' ')}</td>
                  <td><button className="btn ghost small" onClick={() => onPick(e)}>Proof</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
