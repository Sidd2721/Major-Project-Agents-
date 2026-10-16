/**
 * SmartOps AI — Shared Mode Badge Utility
 * Fetches /api/mode and updates or creates a visible LIVE / MOCK / REPLAY badge.
 */
(function() {
  function renderBadge(mode, containerId) {
    const target = containerId ? document.getElementById(containerId) : document.getElementById('smartops-mode-badge');
    const label = (mode || 'MOCK').toUpperCase();
    const styleClass = mode === 'live' ? 'nav-live' : (mode === 'replay' ? 'nav-replay' : 'nav-mock');
    
    if (target) {
      target.className = 'nav-mode ' + styleClass;
      const txt = target.querySelector('#smartops-mode-txt') || target;
      txt.textContent = label;
      return;
    }

    // Floating fallback badge if no container exists
    let badge = document.getElementById('floating-mode-badge');
    if (!badge) {
      badge = document.createElement('div');
      badge.id = 'floating-mode-badge';
      badge.style.cssText = 'position:fixed;bottom:16px;right:16px;z-index:9999;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.05em;display:flex;align-items:center;gap:6px;box-shadow:0 4px 12px rgba(0,0,0,0.3);';
      document.body.appendChild(badge);
    }
    badge.className = styleClass;
    badge.innerHTML = `<span style="width:6px;height:6px;border-radius:50%;background:currentColor;"></span>${label} MODE`;
  }

  window.SmartOpsMode = {
    init: function(endpoint = '/api/mode', containerId = null) {
      fetch(endpoint, { cache: 'no-store' })
        .then(res => res.json())
        .then(data => renderBadge(data.mode, containerId))
        .catch(() => renderBadge('mock', containerId));
    }
  };
})();
