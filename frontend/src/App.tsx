import { useEffect, useState } from 'react';
import Home from './Home';
import ScanView from './ScanView';
import Pilot from './Pilot';

function useHashRoute(): string {
  const [hash, setHash] = useState(window.location.hash || '#/');
  useEffect(() => {
    const on = () => { setHash(window.location.hash || '#/'); window.scrollTo(0, 0); };
    window.addEventListener('hashchange', on);
    return () => window.removeEventListener('hashchange', on);
  }, []);
  return hash;
}

export function Logo({ size = 26 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <circle cx="16" cy="16" r="13" fill="none" stroke="var(--stamp)" strokeWidth="3" />
      <path d="M5 18 L12 18 L15 9 L19 24 L22 16 L27 16" fill="none" stroke="var(--trace)" strokeWidth="2.5" strokeLinejoin="round" />
    </svg>
  );
}

export default function App() {
  const route = useHashRoute();
  const scanMatch = route.match(/^#\/scan\/([\w-]+)/);
  const page = scanMatch ? 'scan' : route.startsWith('#/cases') ? 'cases' : route.startsWith('#/pilot') ? 'pilot' : 'home';
  return (
    <>
      <header className="topbar">
        <a className="wordmark" href="#/" aria-label="TraceMap home"><Logo />TraceMap</a>
        <nav className="topnav" aria-label="Main">
          <a href="#/" aria-current={page === 'home' ? 'page' : undefined}>New scan</a>
          <a href="#/cases" aria-current={page === 'cases' ? 'page' : undefined}>Case files</a>
          <a href="#/pilot" aria-current={page === 'pilot' ? 'page' : undefined}>Pilot study</a>
        </nav>
      </header>
      <main>
        {scanMatch ? <ScanView key={scanMatch[1]} scanId={scanMatch[1]} /> : page === 'pilot' ? <Pilot /> : <Home casesOnly={page === 'cases'} />}
      </main>
    </>
  );
}
