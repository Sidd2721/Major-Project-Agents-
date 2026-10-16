/**
 * SmartOps AI — Shared Navigation Bar
 * Include in every UI:
 *   <script src="/shared/nav.js"></script>
 *   Call: SmartOpsNav.init({ active: 'support' });
 */
(function() {
  const LINKS = [
    { key: 'hub',      label: '⬡ Hub',                url: 'http://localhost:8080' },
    { key: 'portal',   label: '🧑 Customer Portal',   url: 'http://localhost:5173' },
    { key: 'support',  label: '📊 Employee Dashboard', url: 'http://localhost:5174' },
    { key: 'sales',    label: '📈 Sales',              url: 'http://localhost:5175' },
    { key: 'voice',    label: '🎙️ Voice',              url: 'http://localhost:8765' },
  ];

  const CSS = `
  .smartops-nav {
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    height: 50px;
    background: rgba(15,23,42,.95);
    border-bottom: 1px solid rgba(255,255,255,.08);
    backdrop-filter: blur(8px);
    display: flex; align-items: center;
    padding: 0 20px; gap: 6px;
    font-family: Inter, system-ui, sans-serif;
    font-size: 13px;
  }
  .smartops-nav .nav-logo {
    font-weight: 700; color: #fff; margin-right: 12px; white-space: nowrap;
    letter-spacing: -.01em;
  }
  .smartops-nav a {
    color: #94a3b8; text-decoration: none;
    padding: 5px 10px; border-radius: 6px;
    transition: color .12s, background .12s;
    white-space: nowrap;
  }
  .smartops-nav a:hover { color: #fff; background: rgba(255,255,255,.08); }
  .smartops-nav a.active { color: #fff; background: rgba(79,70,229,.25); }
  .smartops-nav .nav-mode {
    margin-left: auto; padding: 3px 10px; border-radius: 100px;
    font-size: 11px; font-weight: 700; letter-spacing: .06em;
    display: flex; align-items: center; gap: 5px;
  }
  .smartops-nav .mode-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
  .nav-live   { background: rgba(22,163,74,.15);  color: #4ade80; border: 1px solid rgba(22,163,74,.3); }
  .nav-mock   { background: rgba(202,138,4,.15);   color: #fbbf24; border: 1px solid rgba(202,138,4,.3);  }
  .nav-replay { background: rgba(2,132,199,.15);   color: #38bdf8; border: 1px solid rgba(2,132,199,.3);  }
  /* Push page content below nav */
  .smartops-nav-spacer { height: 50px; display: block; }
  @media (max-width: 600px) {
    .smartops-nav .nav-link-label { display: none; }
  }
  `;

  function inject(active, modeEndpoint) {
    // Inject styles
    const style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);

    // Build nav
    const nav = document.createElement('nav');
    nav.className = 'smartops-nav';
    nav.setAttribute('role', 'navigation');
    nav.setAttribute('aria-label', 'SmartOps platform navigation');

    nav.innerHTML = `
      <span class="nav-logo">SmartOps AI</span>
      ${LINKS.map(l => `
        <a href="${l.url}" ${l.key === active ? 'class="active" aria-current="page"' : ''}
           ${l.url !== window.location.href && !l.url.endsWith(window.location.port) ? 'target="_blank" rel="noopener"' : ''}>
          ${l.label}
        </a>`).join('')}
      <span class="nav-mode nav-unknown" id="smartops-mode-badge">
        <span class="mode-dot"></span>
        <span id="smartops-mode-txt">…</span>
      </span>
    `;
    document.body.insertBefore(nav, document.body.firstChild);

    // Spacer so content isn't hidden under fixed nav
    const spacer = document.createElement('div');
    spacer.className = 'smartops-nav-spacer';
    spacer.setAttribute('aria-hidden', 'true');
    nav.after(spacer);

    // Fetch mode
    if (modeEndpoint) {
      fetch(modeEndpoint, { cache: 'no-store' })
        .then(r => r.json())
        .then(d => setMode(d.mode))
        .catch(() => setMode(null));
    }
  }

  function setMode(mode) {
    const badge = document.getElementById('smartops-mode-badge');
    const txt   = document.getElementById('smartops-mode-txt');
    if (!badge) return;
    badge.className = 'nav-mode nav-' + (mode || 'unknown');
    txt.textContent = mode ? mode.toUpperCase() : 'OFFLINE';
  }

  window.SmartOpsNav = {
    init: function(opts = {}) {
      const active = opts.active || '';
      const modeEndpoint = opts.modeEndpoint || null;
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => inject(active, modeEndpoint));
      } else {
        inject(active, modeEndpoint);
      }
    }
  };
})();
