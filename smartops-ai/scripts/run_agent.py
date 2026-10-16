"""
SmartOps AI — Run a single agent independently.

Usage:
  python scripts/run_agent.py support   # API :8000 + worker + customer :5173 + employee :5174
  python scripts/run_agent.py sales     # sales dashboard :5175
  python scripts/run_agent.py voice     # voice console :8765
  python scripts/run_agent.py hub       # hub :8080
  python scripts/run_agent.py all       # all agents (same as run_all.py)

Each command:
  - Checks its ports are free
  - Checks .env and reports missing keys (keys are OPTIONAL — no keys = mock mode)
  - Starts ONLY what that agent needs
  - Waits for its health URL(s)
  - Prints the URL(s)
  - Stops cleanly on Ctrl+C
"""
import subprocess, sys, time, os, socket, signal, shutil, threading, argparse
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# ── Windows UTF-8 fix ──────────────────────────────────────────────────────
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

WIN  = sys.platform == "win32"
ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

# ── Port + service definitions ─────────────────────────────────────────────
AGENT_PORTS = {
    "support": [8000, 5173, 5174],
    "sales":   [5175],
    "voice":   [8765],
    "hub":     [8080],
    "all":     [8000, 5173, 5174, 5175, 8765, 8080],
}

PORT_NAMES = {
    8000: "Customer Support API",
    5173: "Customer Portal",
    5174: "Employee Dashboard",
    5175: "Sales Dashboard",
    8765: "Voice Agent",
    8080: "Central Hub",
}

# ── Helpers ────────────────────────────────────────────────────────────────
def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0

def check_ports(agent: str) -> bool:
    """Returns True if all required ports are free."""
    ports  = AGENT_PORTS.get(agent, [])
    blocked = [f":{p} ({PORT_NAMES.get(p, p)})" for p in ports if not port_free(p)]
    if blocked:
        print(f"\n❌ Ports already in use: {', '.join(blocked)}")
        print("   Stop those processes first, then re-run.\n")
        return False
    return True

def venv_python(folder: Path) -> str:
    for sub in ("venv", ".venv"):
        p = folder / sub / ("Scripts/python.exe" if WIN else "bin/python")
        if p.exists():
            return str(p)
    return sys.executable

def venv_uvicorn(folder: Path) -> str:
    for sub in ("venv", ".venv"):
        u = folder / sub / ("Scripts/uvicorn.exe" if WIN else "bin/uvicorn")
        if u.exists():
            return str(u)
    return "uvicorn"

def wait_health(url: str, timeout: int = 40, label: str = "") -> bool:
    start = time.time()
    req = Request(url, headers={"User-Agent": "SmartOps-HealthChecker/1.0"})
    while time.time() - start < timeout:
        try:
            with urlopen(req, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    print(f"  ⚠️  {label} did not respond within {timeout}s (check logs/)")
    return False

def check_env(folder: Path) -> None:
    """Ensure .env exists; report missing keys (never print values)."""
    env_f = folder / ".env"
    if not env_f.exists():
        env_f.write_text("GROQ_API_KEY=\nGEMINI_API_KEY=\nLLM_MODE=mock\n")
        print(f"  📋 Created {folder.name}/.env — running in MOCK mode (no keys required)")
        return
    # Inspect which optional keys are empty
    missing = []
    for line in env_f.read_text(errors="replace").splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            k = k.strip()
            if k in ("GROQ_API_KEY", "GEMINI_API_KEY") and not v.strip():
                missing.append(k)
    if missing:
        print(f"  ℹ️  {folder.name}/.env: {', '.join(missing)} not set → MOCK mode active (fine for demo)")
    else:
        print(f"  ✅ {folder.name}/.env found with keys → LIVE mode available")

procs: list = []

def start(cmd: list, cwd: Path, label: str, log_name: str | None = None) -> subprocess.Popen:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    use_shell = False
    if log_name is None:
        log_name = label.split()[0].lower().replace(":", "").replace("/", "_")
    log_file = open(LOGS / f"{log_name}.log", "w", encoding="utf-8", errors="replace")
    if WIN and cmd and cmd[0] == "npm":
        cmd[0] = shutil.which("npm") or "npm.cmd"
        use_shell = True
    p = subprocess.Popen(cmd, cwd=str(cwd), env=env,
                         stdout=log_file, stderr=subprocess.STDOUT,
                         shell=use_shell)
    print(f"  ▶  {label} (PID {p.pid})", flush=True)
    return p

def shutdown(sig=None, frame=None):
    print("\n\n🛑 Stopping services...")
    for p in procs:
        try:
            if WIN:
                p.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                p.terminate()
        except Exception:
            pass
    time.sleep(0.8)
    for p in procs:
        try:
            p.kill()
        except Exception:
            pass
    print("✅ All services stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
if WIN:
    try:
        signal.signal(signal.SIGBREAK, shutdown)
    except AttributeError:
        pass

# ── Agent launchers ────────────────────────────────────────────────────────

def run_support():
    print("\n🛡️  Customer Support Agent")
    print("=" * 50)
    csa = ROOT / "Customer-Support-Agent"
    if not csa.exists():
        print("❌ Customer-Support-Agent folder not found"); sys.exit(1)
    check_env(csa)
    os.environ.update({"PYTHONPATH": str(csa), "PYTHONIOENCODING": "utf-8"})

    p1 = start(
        [venv_uvicorn(csa), "Backend.api:app", "--port", "8000", "--host", "0.0.0.0"],
        csa, "Customer Support API  :8000", "support_api"
    )
    procs.append(p1)
    ok = wait_health("http://localhost:8000/health", 40, "Customer Support API")
    if not ok:
        wait_health("http://localhost:8000/docs", 10, "Customer Support API /docs")

    p2 = start([venv_python(csa), "main_worker.py"], csa, "Support AI Worker", "support_worker")
    procs.append(p2)

    portal = csa / "Frontend" / "customer"
    if portal.exists():
        p3 = start(["npm", "run", "dev", "--", "--port", "5173"], portal,
                   "Customer Portal        :5173", "portal")
        procs.append(p3)
        wait_health("http://localhost:5173", 30, "Customer Portal")

    emp = csa / "Frontend" / "employee-dashboard"
    if emp.exists():
        p4 = start(["npm", "run", "dev", "--", "--port", "5174"], emp,
                   "Employee Dashboard     :5174", "employee")
        procs.append(p4)
        wait_health("http://localhost:5174", 30, "Employee Dashboard")

    _print_urls([
        ("Customer Support API", "http://localhost:8000/docs"),
        ("Customer Portal",      "http://localhost:5173"),
        ("Employee Dashboard",   "http://localhost:5174"),
    ])

def run_sales():
    print("\n💼 Sales Outreach Agent")
    print("=" * 50)
    sales = ROOT / "sales_agent_module"
    if not sales.exists():
        print("❌ sales_agent_module folder not found"); sys.exit(1)
    check_env(sales)

    p = start([venv_python(sales), "web_dashboard.py"], sales,
              "Sales Dashboard        :5175", "sales")
    procs.append(p)
    wait_health("http://localhost:5175", 30, "Sales Dashboard")
    _print_urls([("Sales Dashboard", "http://localhost:5175")])

def run_voice():
    print("\n🎙️  Voice Agent")
    print("=" * 50)
    voice = ROOT / "gemini-voice-agent"
    if not voice.exists():
        print("❌ gemini-voice-agent folder not found"); sys.exit(1)
    check_env(voice)

    uv_exe = shutil.which("uv")
    if uv_exe:
        vcmd = [uv_exe, "run", "python", "bot.py"]
    else:
        vcmd = [venv_python(voice), "bot.py"]
    p = start(vcmd, voice, "Voice Agent            :8765", "voice")
    procs.append(p)
    wait_health("http://localhost:8765", 30, "Voice Agent")
    _print_urls([("Voice Agent", "http://localhost:8765")])

def run_hub():
    print("\n🏠 Central Hub")
    print("=" * 50)
    hub = ROOT / "hub"
    if not hub.exists() or not (hub / "index.html").exists():
        print("❌ hub/index.html not found"); sys.exit(1)

    import http.server, socketserver
    def _serve():
        os.chdir(str(hub))
        Handler = http.server.SimpleHTTPRequestHandler
        Handler.log_message = lambda *a: None
        with socketserver.TCPServer(("", 8080), Handler) as httpd:
            httpd.serve_forever()

    t = threading.Thread(target=_serve, daemon=True)
    t.start()
    print("  ▶  Hub (static server)  :8080")
    wait_health("http://localhost:8080", 10, "Hub")
    _print_urls([("Central Hub", "http://localhost:8080")])

def run_all():
    print("\n🚀 SmartOps AI — All Agents")
    print("=" * 50)
    run_support()
    run_sales()
    run_voice()
    run_hub()

def _print_urls(rows: list):
    print()
    print("-" * 50)
    for label, url in rows:
        print(f"  → {label:<25} {url}")
    print("-" * 50)
    print("Press Ctrl+C to stop.\n")

# ── Entry point ────────────────────────────────────────────────────────────

AGENTS = {
    "support": run_support,
    "sales":   run_sales,
    "voice":   run_voice,
    "hub":     run_hub,
    "all":     run_all,
}

def main():
    parser = argparse.ArgumentParser(
        description="SmartOps AI — run individual agents independently",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_agent.py support   # Support API + portals
  python scripts/run_agent.py sales     # Sales dashboard only
  python scripts/run_agent.py voice     # Voice agent only
  python scripts/run_agent.py hub       # Hub only
  python scripts/run_agent.py all       # Everything
        """,
    )
    parser.add_argument("agent", choices=list(AGENTS.keys()),
                        help="Which agent to start")
    args = parser.parse_args()

    if not check_ports(args.agent):
        sys.exit(1)

    AGENTS[args.agent]()

    # Keep process alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
