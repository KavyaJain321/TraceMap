import { useState } from 'react';
import { api, CATEGORY_LABEL, Finding, ScanResult, who } from './api';
import LeakReplay from './LeakReplay';
import NetworkGraph from './NetworkGraph';
import ProofDrawer, { Proof } from './ProofDrawer';

type Tab = 'findings' | 'replay' | 'network' | 'companies';

function Verdict({ r }: { r: ScanResult }) {
  const s = r.summary;
  if (s.blocked) return <div className="stamp clear">Blocked by site<small>bot check shown — results incomplete</small></div>;
  if (s.leaks > 0) {
    return (
      <div className="stamp">
        Data left before submit
        <small>{s.leak_recipients} compan{s.leak_recipients === 1 ? 'y' : 'ies'} received your test details</small>
      </div>
    );
  }
  if (!r.leaks.tested || r.leaks.fields.length === 0) return <div className="stamp clear">Forms not tested<small>{r.leaks.tested ? 'no email/phone field found' : 'leak test switched off'}</small></div>;
  return <div className="stamp clear">No leak seen<small>test details stayed on the site</small></div>;
}

function Findings({ items, onProof }: { items: Finding[]; onProof: (f: Finding) => void }) {
  return (
    <ul className="findings">
      {items.map((f, i) => (
        <li className="finding" key={i}>
          <span className={`sev ${f.severity}`}>{f.severity === 'info' ? 'Note' : f.severity}</span>
          <div>
            <h3>{f.title}</h3>
            {f.detail && <p>{f.detail}</p>}
          </div>
          {f.request_ids.length > 0 && (
            <button className="btn ghost small" onClick={() => onProof(f)}>Show proof</button>
          )}
        </li>
      ))}
    </ul>
  );
}

function Companies({ r }: { r: ScanResult }) {
  const rows = r.parties.filter((p) => !p.first_party).sort((a, b) => Number(b.is_tracker) - Number(a.is_tracker) || b.request_count - a.request_count);
  return (
    <div className="table-wrap">
      <table className="table">
        <thead><tr><th>Domain</th><th>Company</th><th>Type</th><th>Tracker</th><th className="num">Requests</th><th>Known from</th></tr></thead>
        <tbody>
          {rows.map((p) => (
            <tr key={p.domain}>
              <td className="mono">{p.domain}</td>
              <td>{p.owner ?? <span className="faint">unknown</span>}{p.same_owner_as_site && <div className="faint" style={{ fontSize: 12 }}>same company as the site</div>}</td>
              <td>{CATEGORY_LABEL[p.category] ?? p.category}</td>
              <td>{p.is_tracker ? 'Yes' : <span className="faint">No</span>}</td>
              <td className="num">{p.request_count}</td>
              <td className="faint" style={{ fontSize: 13 }}>{p.sources.join(', ') || 'not on any list'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Result({ r }: { r: ScanResult }) {
  const [tab, setTab] = useState<Tab>('findings');
  const [proof, setProof] = useState<Proof | null>(null);
  const s = r.summary;
  const leakEvents = r.leaks.leaks.filter((e) => !e.first_party);

  const openFinding = (f: Finding) => {
    const leak = leakEvents.find((e) => f.request_ids.includes(e.request_id));
    setProof({ scanId: r.scan_id, requestIds: f.request_ids, title: f.title, leak, canaries: r.leaks.canaries });
  };

  const tabs: [Tab, string, number | null][] = [
    ['findings', 'Findings', r.findings.length],
    ['replay', 'Leak replay', leakEvents.length],
    ['network', 'ID-sharing map', r.graph.edges.filter((e) => e.kind === 'shared_id').length],
    ['companies', 'Companies', s.third_parties],
  ];

  return (
    <>
      <section className="case-head">
        <div>
          <p className="eyebrow">Case file · {new Date(r.created_at * 1000).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })} · {r.mode === 'full' ? 'thorough' : 'quick'} scan</p>
          <h1 style={{ marginTop: 10 }}>{r.site}</h1>
          <p className="url">{r.url}</p>
          <Verdict r={r} />
        </div>
        {r.screenshot_sha256 && (
          <figure className="shot" style={{ margin: 0 }}>
            <img src={api.blobUrl(r.screenshot_sha256)} alt={`What ${r.site} looked like during the scan`} />
          </figure>
        )}
      </section>
      <div className="ledger">
        <div><b>{s.third_parties}</b><span>other domains</span></div>
        <div><b>{s.trackers}</b><span>tracking domains</span></div>
        <div><b>{s.companies}</b><span>companies</span></div>
        <div className={s.leaks ? 'hot' : ''}><b>{s.leak_recipients}</b><span>received your test details</span></div>
        <div className={s.shared_id_edges ? 'hot' : ''}><b>{s.shared_id_edges}</b><span>ID exchanges between companies</span></div>
        <div><b>{s.consent_banner ? 'Yes' : 'No'}</b><span>cookie banner</span></div>
      </div>
      <p className="score-note">A 0–100 risk score is not shown yet: it will be added once its weights are validated against expert rankings.</p>

      <div className="tabs" role="tablist">
        {tabs.map(([k, label, n]) => (
          <button key={k} role="tab" aria-selected={tab === k} onClick={() => setTab(k)}>
            {label}{n !== null && <span className="count">{n}</span>}
          </button>
        ))}
      </div>

      {tab === 'findings' && <Findings items={r.findings} onProof={openFinding} />}
      {tab === 'replay' && (
        <LeakReplay r={r} onPick={(e) => setProof({ scanId: r.scan_id, requestIds: [e.request_id], leak: e, canaries: r.leaks.canaries,
          title: `Sent to ${who(e.recipient_owner, e.recipient_domain)}` })} />
      )}
      {tab === 'network' && (
        <NetworkGraph r={r} onEdgeProof={(ids, title) => setProof({ scanId: r.scan_id, requestIds: ids, title, canaries: [] })} />
      )}
      {tab === 'companies' && <Companies r={r} />}

      {proof && <ProofDrawer proof={proof} onClose={() => setProof(null)} />}
    </>
  );
}
