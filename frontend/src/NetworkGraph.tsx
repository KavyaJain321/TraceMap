import { useEffect, useMemo, useRef, useState } from 'react';
import cytoscape, { Core } from 'cytoscape';
import fcose from 'cytoscape-fcose';
import { CATEGORY_LABEL, GraphEdge, GraphNode, ScanResult, who } from './api';

cytoscape.use(fcose);

const CAT_COLOR: Record<string, string> = {
  ad: '#b86e00', analytics: '#0b7a83', social: '#2f5da8', session_replay: '#5a2d82',
  tag_manager: '#6b7787', fingerprinting: '#8a3b2b', functional: '#a9b4c2', unknown: '#c8d0da',
};

type Sel = { kind: 'node'; n: GraphNode } | { kind: 'edge'; e: GraphEdge } | null;

export default function NetworkGraph({ r, onEdgeProof }: { r: ScanResult; onEdgeProof: (ids: string[], title: string) => void }) {
  const box = useRef<HTMLDivElement>(null);
  const cy = useRef<Core | null>(null);
  const [onlyIds, setOnlyIds] = useState(false);
  const [sel, setSel] = useState<Sel>(null);
  const nodeById = useMemo(() => Object.fromEntries(r.graph.nodes.map((n) => [n.id, n])), [r]);
  const sharedCount = r.graph.edges.filter((e) => e.kind === 'shared_id').length;

  useEffect(() => {
    if (!box.current) return;
    const edges = r.graph.edges.filter((e) => !onlyIds || e.kind === 'shared_id');
    const used = new Set(edges.flatMap((e) => [e.a, e.b]));
    const nodes = r.graph.nodes.filter((n) => !onlyIds || used.has(n.id) || n.first_party);
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    const inst = cytoscape({
      container: box.current,
      elements: [
        ...nodes.map((n) => ({
          data: { id: n.id, label: who(n.owner, n.id), cat: n.category, fp: n.first_party ? 1 : 0, tracker: n.is_tracker ? 1 : 0,
                  size: n.first_party ? 46 : 18 + Math.min(26, n.degree * 4) },
        })),
        ...edges.map((e, i) => ({
          data: { id: `e${i}`, source: e.a, target: e.b, kind: e.kind, conf: e.confidence, idx: r.graph.edges.indexOf(e) },
        })),
      ],
      style: [
        { selector: 'node', style: {
          'background-color': (el: cytoscape.NodeSingular) => CAT_COLOR[el.data('cat')] ?? CAT_COLOR.unknown,
          width: 'data(size)', height: 'data(size)', label: 'data(label)', 'font-family': 'Public Sans, sans-serif',
          'font-size': 11, color: '#18202c', 'text-valign': 'bottom', 'text-margin-y': 5, 'text-wrap': 'ellipsis',
          'text-max-width': '120px', 'border-width': 2, 'border-color': '#f8f9fb',
        } },
        { selector: 'node[tracker = 1]', style: { 'border-color': '#5a2d82', 'border-width': 2.5 } },
        { selector: 'node[fp = 1]', style: { 'background-color': '#18202c', shape: 'round-rectangle', 'font-weight': 700, 'font-size': 13 } },
        { selector: 'edge', style: { width: 1.2, 'line-color': '#c8d0da', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle',
                                     'target-arrow-color': '#c8d0da', 'arrow-scale': 0.7 } },
        { selector: 'edge[kind = "redirect"]', style: { 'line-color': '#0b7a83', 'target-arrow-color': '#0b7a83', 'line-style': 'dashed', width: 1.8 } },
        { selector: 'edge[kind = "shared_id"]', style: {
          'line-color': '#5a2d82', 'target-arrow-shape': 'none', width: (el: cytoscape.EdgeSingular) => 2 + 4 * el.data('conf'),
          'line-style': (el: cytoscape.EdgeSingular) => (el.data('conf') < 0.6 ? 'dashed' : 'solid'),
        } },
        { selector: ':selected', style: { 'overlay-color': '#0b7a83', 'overlay-opacity': 0.18, 'overlay-padding': 6 } },
      ],
      layout: { name: 'fcose', animate: !reduce, animationDuration: 600, nodeRepulsion: 9000, idealEdgeLength: 90, randomize: true } as cytoscape.LayoutOptions,
      wheelSensitivity: 0.3,
      minZoom: 0.3,
      maxZoom: 3,
    });
    inst.on('tap', 'node', (ev) => setSel({ kind: 'node', n: nodeById[ev.target.id()] }));
    inst.on('tap', 'edge', (ev) => setSel({ kind: 'edge', e: r.graph.edges[ev.target.data('idx')] }));
    inst.on('tap', (ev) => { if (ev.target === inst) setSel(null); });
    cy.current = inst;
    return () => { inst.destroy(); cy.current = null; };
  }, [r, onlyIds, nodeById]);

  const party = sel?.kind === 'node' ? r.parties.find((p) => p.domain === sel.n.id) : undefined;
  const edgeTitle = (e: GraphEdge) =>
    e.kind === 'shared_id' ? `${who(nodeById[e.a]?.owner, e.a)} and ${who(nodeById[e.b]?.owner, e.b)} shared an identifier`
      : e.kind === 'redirect' ? `${e.a} redirected the browser to ${e.b}` : `${e.a} loaded content from ${e.b}`;

  return (
    <section>
      <div className="graph-wrap">
        <div>
          <div className="graph-canvas" ref={box} role="img"
               aria-label={`Network of ${r.graph.nodes.length} domains with ${sharedCount} identifier-sharing links`} />
          <label className="check" style={{ marginTop: 10 }}>
            <input type="checkbox" checked={onlyIds} onChange={(e) => setOnlyIds(e.target.checked)} />
            <span>Show only identifier sharing ({sharedCount} link{sharedCount === 1 ? '' : 's'})</span>
          </label>
          {r.graph.notes.map((n) => <p key={n} className="hint">{n}</p>)}
        </div>
        <aside className="graph-side">
          {sel?.kind === 'node' && (
            <div className="card">
              <p className="eyebrow">{sel.n.first_party ? 'This website' : sel.n.is_tracker ? 'Tracker' : 'Third party'}</p>
              <h3 style={{ marginTop: 6 }}>{sel.n.id}</h3>
              <dl className="kv" style={{ gridTemplateColumns: '90px 1fr' }}>
                <dt>Company</dt><dd>{sel.n.owner ?? 'unknown'}</dd>
                <dt>Type</dt><dd>{CATEGORY_LABEL[sel.n.category] ?? sel.n.category}</dd>
                <dt>Links</dt><dd>{sel.n.degree}</dd>
                {party && <><dt>Requests</dt><dd>{party.request_count}</dd><dt>Known from</dt><dd>{party.sources.join(', ') || '—'}</dd></>}
              </dl>
            </div>
          )}
          {sel?.kind === 'edge' && (
            <div className="card">
              <p className="eyebrow">{sel.e.kind === 'shared_id' ? 'Identifier sharing' : sel.e.kind}</p>
              <h3 style={{ marginTop: 6, wordBreak: 'normal' }}>{edgeTitle(sel.e)}</h3>
              <dl className="kv" style={{ gridTemplateColumns: '90px 1fr' }}>
                <dt>Evidence</dt><dd>{sel.e.evidence_type ?? '—'}</dd>
                <dt>Confidence</dt><dd>{Math.round(sel.e.confidence * 100)}%{sel.e.same_entity ? ' · same company' : ''}</dd>
                <dt>Seen</dt><dd>{sel.e.count}×</dd>
              </dl>
              {sel.e.request_ids.length > 0 && (
                <button className="btn ghost small" onClick={() => onEdgeProof(sel.e.request_ids, edgeTitle(sel.e))}>Show proof</button>
              )}
            </div>
          )}
          {!sel && <div className="card muted">Select a dot or a line to see who it is and the evidence behind it.</div>}
          <div className="card">
            <p className="eyebrow" style={{ marginBottom: 8 }}>Key</p>
            <div className="swatch"><i style={{ background: '#18202c', borderRadius: 3 }} />This website</div>
            {['ad', 'analytics', 'session_replay', 'social', 'tag_manager', 'functional'].map((c) => (
              <div className="swatch" key={c}><i style={{ background: CAT_COLOR[c] }} />{CATEGORY_LABEL[c]}</div>
            ))}
            <div className="swatch"><span className="line" style={{ borderColor: '#5a2d82' }} />Shared a user ID (dashed = weaker evidence)</div>
            <div className="swatch"><span className="line" style={{ borderColor: '#0b7a83', borderTopStyle: 'dashed' }} />Redirected the browser</div>
            <div className="swatch"><span className="line" style={{ borderColor: '#c8d0da' }} />Loaded content</div>
          </div>
        </aside>
      </div>
    </section>
  );
}
