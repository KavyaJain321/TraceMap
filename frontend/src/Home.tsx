import { FormEvent, useEffect, useState } from 'react';
import { api, ScanRow, StartScan } from './api';

function Seg<T extends string>({ name, value, options, onChange }: {
  name: string; value: T; options: [T, string][]; onChange: (v: T) => void;
}) {
  return (
    <div className="seg" role="radiogroup">
      {options.map(([v, label]) => (
        <label key={v}>
          <input type="radio" name={name} value={v} checked={value === v} onChange={() => onChange(v)} />
          <span>{label}</span>
        </label>
      ))}
    </div>
  );
}

export function CaseFiles({ rows }: { rows: ScanRow[] | null }) {
  if (rows === null) return <p className="muted">Loading case files…</p>;
  if (rows.length === 0) return <div className="empty">No sites examined yet. Enter a website above to open the first case file.</div>;
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr><th>Site</th><th>When</th><th>Depth</th><th className="num">Trackers</th><th className="num">Leaks</th><th>Status</th></tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.scan_id} className="clickable" onClick={() => { window.location.hash = `#/scan/${r.scan_id}`; }}>
              <td><a href={`#/scan/${r.scan_id}`} onClick={(e) => e.stopPropagation()}>{r.site || r.url}</a></td>
              <td className="muted">{new Date(r.created_at * 1000).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}</td>
              <td className="muted">{r.mode === 'full' ? 'Thorough' : 'Quick'}</td>
              <td className="num">{r.summary?.trackers ?? '–'}</td>
              <td className="num">{r.summary ? r.summary.leaks : '–'}</td>
              <td>{r.status === 'done' ? (r.summary?.blocked ? 'Blocked by site' : 'Complete') : r.status === 'error' ? 'Failed' : 'In progress'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Home({ casesOnly }: { casesOnly: boolean }) {
  const [url, setUrl] = useState('');
  const [opts, setOpts] = useState<Omit<StartScan, 'url'>>({ mode: 'quick', leak_test: true, consent: 'none', device: 'mobile' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rows, setRows] = useState<ScanRow[] | null>(null);

  useEffect(() => { api.list().then(setRows).catch(() => setRows([])); }, []);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!url.trim()) { setError('Enter a website address, for example www.irctc.co.in'); return; }
    setBusy(true); setError(null);
    try {
      const { scan_id } = await api.start({ url: url.trim(), ...opts });
      window.location.hash = `#/scan/${scan_id}`;
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setBusy(false);
    }
  }

  if (casesOnly) {
    return (
      <section className="cases">
        <p className="eyebrow">Case files</p>
        <h1 style={{ margin: '8px 0 24px' }}>Sites examined</h1>
        <CaseFiles rows={rows} />
      </section>
    );
  }

  return (
    <>
      <section className="intake">
        <p className="eyebrow">Open a case file</p>
        <h1>Which website should we examine?</h1>
        <p className="lede">
          TraceMap visits the site like a phone user would, records every company it quietly talks to,
          and types a fake email and phone number into its forms — without ever pressing Submit — to see who receives them.
        </p>
        <form onSubmit={submit} noValidate>
          <div className="url-row">
            <label className="url-field">
              <span className="sr-only">Website address</span>
              <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="www.example.in"
                     inputMode="url" autoComplete="off" spellCheck={false} autoFocus />
            </label>
            <button className="btn" type="submit" disabled={busy}>{busy ? 'Opening case…' : 'Examine site'}</button>
          </div>
          <div className="options">
            <fieldset className="option-group">
              <legend>Depth</legend>
              <Seg name="mode" value={opts.mode} onChange={(mode) => setOpts({ ...opts, mode })}
                   options={[['quick', 'Quick · ~1 min'], ['full', 'Thorough · ~4 min']]} />
              <p className="hint">Thorough compares two separate visitors, which confirms ID sharing between companies.</p>
            </fieldset>
            <fieldset className="option-group">
              <legend>Cookie banner</legend>
              <Seg name="consent" value={opts.consent} onChange={(consent) => setOpts({ ...opts, consent })}
                   options={[['none', 'Leave untouched'], ['optIn', 'Accept all'], ['optOut', 'Reject all']]} />
              <p className="hint">“Leave untouched” shows what happens before you make any choice.</p>
            </fieldset>
            <fieldset className="option-group">
              <legend>Device</legend>
              <Seg name="device" value={opts.device} onChange={(device) => setOpts({ ...opts, device })}
                   options={[['mobile', 'Phone'], ['desktop', 'Laptop']]} />
              <label className="check" style={{ marginTop: 14 }}>
                <input type="checkbox" checked={opts.leak_test} onChange={(e) => setOpts({ ...opts, leak_test: e.target.checked })} />
                <span>Test forms with a fake email and phone number</span>
              </label>
            </fieldset>
          </div>
          {error && <div className="error-box" role="alert">{error}</div>}
        </form>
        <div className="method">
          <div><strong>Nothing real is sent</strong><p>The email and phone number are made up for this scan. Forms are never submitted.</p></div>
          <div><strong>Every claim has proof</strong><p>Each finding links to the exact request that left the browser.</p></div>
          <div><strong>What it cannot see</strong><p>Data shared later between company servers is invisible from the browser, so results are a minimum.</p></div>
        </div>
      </section>
      <section className="cases">
        <h2>Recent case files</h2>
        <CaseFiles rows={rows} />
      </section>
    </>
  );
}
