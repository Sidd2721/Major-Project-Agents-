"""
SmartOps AI — Start all services.
Run: python scripts/run_all.py

Checks ports, starts backend, worker, React apps, voice server, hub.
Prints a live URL table. Stops everything cleanly on Ctrl+C.
"""
import subprocess, sys, time, os, socket, signal, threading, shutil
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

ROOT   = Path(__file__).parent.parent
WIN    = sys.platform == "win32"
PYTHON = sys.executable

# Fix Windows UTF-8 once, centrally
if WIN and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def venv_python(folder):
    v = folder / "venv"
    if WIN:
        p = v / "Scripts" / "python.exe"
    else:
        p = v / "bin" / "python"
    return str(p) if p.exists() else PYTHON

def venv_uvicorn(folder):
    v = folder / "venv"
    if WIN:
        u = v / "Scripts" / "uvicorn.exe"
    else:
        u = v / "bin" / "uvicorn"
    return str(u) if u.exists() else "uvicorn"

def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0

def wait_http(url, timeout=30, label=""):
    start = time.time()
    while time.time() - start < timeout:
        try:
            urlopen(url, timeout=2)
            return True
        except URLError:
            pass
        time.sleep(1)
    print(f"  ⚠️  {label} did not respond at {url} within {timeout}s")
    return False

def start(cmd, cwd, label):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    use_shell = False
    if WIN and cmd:
        if cmd[0] == "npm":
            cmd[0] = shutil.which("npm") or "npm.cmd"
            use_shell = True
    p = subprocess.Popen(
        cmd, cwd=str(cwd), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        shell=use_shell
    )
    print(f"  ▶  {label} (PID {p.pid})")
    return p

procs = []

def shutdown(sig=None, frame=None):
    print("\n\n🛑 Stopping all services...")
    for p in procs:
        try:
            if WIN:
                p.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                p.terminate()
        except Exception:
            pass
    time.sleep(1)
    for p in procs:
        p.kill()
    print("✅ All services stopped. Goodbye!")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)

def check_env(folder, name):
    env_f = folder / ".env"
    if not env_f.exists():
        print(f"  ⚠️  No .env in {name}. Using LLM_MODE=mock (offline demo).")
        env_f.write_text("GROQ_API_KEY=\nGEMINI_API_KEY=\nLLM_MODE=mock\n")

def main():
    print("\n🚀 SmartOps AI — Starting all services")
    print("=" * 55)

    # --- PORT CHECKS ---
    PORTS = {8000:"API", 5173:"Customer Portal", 5174:"Employee Dashboard", 5175:"Sales Dashboard", 8765:"Voice", 8080:"Hub"}
    blocked = [f":{p} ({n})" for p, n in PORTS.items() if not port_free(p)]
    if blocked:
        print(f"❌ Ports in use: {', '.join(blocked)}")
        print("   Stop those processes first, then re-run.")
        sys.exit(1)
    print("✅ All ports free\n")

    # --- CUSTOMER SUPPORT AGENT ---
    csa = ROOT / "Customer-Support-Agent"
    if csa.exists():
        check_env(csa, "Customer-Support-Agent")
        os.environ.update({"PYTHONPATH": str(csa), "PYTHONIOENCODING": "utf-8"})

        p1 = start(
            [venv_uvicorn(csa), "Backend.api:app", "--port", "8000", "--host", "0.0.0.0"],
            csa, "Customer Support API  :8000"
        )
        procs.append(p1)
        wait_http("http://localhost:8000/docs", label="Customer Support API")

        p2 = start(
            [venv_python(csa), "main_worker.py"],
            csa, "Support AI Worker      (background)"
        )
        procs.append(p2)
    else:
        print("⚠️  Customer-Support-Agent not found")

    # --- REACT CUSTOMER PORTAL :5173 ---
    portal = ROOT / "Customer-Support-Agent" / "Frontend" / "customer"
    if portal.exists():
        p3 = start(["npm", "run", "dev", "--", "--port", "5173"], portal, "Customer Portal         :5173")
        procs.append(p3)
        wait_http("http://localhost:5173", timeout=25, label="Customer Portal")

    # --- REACT EMPLOYEE DASHBOARD :5174 ---
    emp = ROOT / "Customer-Support-Agent" / "Frontend" / "employee-dashboard"
    if emp.exists():
        p4 = start(["npm", "run", "dev", "--", "--port", "5174"], emp, "Employee Dashboard      :5174")
        procs.append(p4)
        wait_http("http://localhost:5174", timeout=25, label="Employee Dashboard")

    # --- SALES DASHBOARD :5175 ---
    sales = ROOT / "sales_agent_module"
    if sales.exists():
        check_env(sales, "sales_agent_module")
        p5 = start(
            [venv_python(sales), "web_dashboard.py"],
            sales, "Sales Dashboard         :5175"
        )
        procs.append(p5)
        wait_http("http://localhost:5175", timeout=20, label="Sales Dashboard")

    # --- VOICE AGENT :8765 ---
    voice = ROOT / "gemini-voice-agent"
    if voice.exists():
        check_env(voice, "gemini-voice-agent")
        uv_exe = None
        import shutil as sh
        uv_exe = sh.which("uv")
        if uv_exe:
            vcmd = [uv_exe, "run", "python", "bot.py"]
        else:
            vcmd = [venv_python(voice), "bot.py"]
        p6 = start(vcmd, voice, "Voice Agent             :8765")
        procs.append(p6)
        wait_http("http://localhost:8765", timeout=20, label="Voice Agent")

    # --- HUB :8080 ---
    hub = ROOT / "hub"
    if hub.exists() and (hub / "index.html").exists():
        import http.server, socketserver
        def serve_hub():
            os.chdir(str(hub))
            Handler = http.server.SimpleHTTPRequestHandler
            Handler.log_message = lambda *a: None
            with socketserver.TCPServer(("", 8080), Handler) as httpd:
                httpd.serve_forever()
        t = threading.Thread(target=serve_hub, daemon=True)
        t.start()
        print(f"  ▶  Hub                   :8080 (Python static server)")
        wait_http("http://localhost:8080", timeout=5, label="Hub")

    # --- URL TABLE ---
    print("\n" + "=" * 55)
    print("✅ All services running!\n")
    rows = [
        ("Hub (Overview)",        "http://localhost:8080"),
        ("Customer Portal",       "http://localhost:5173"),
        ("Employee Dashboard",    "http://localhost:5174"),
        ("Customer Support API",  "http://localhost:8000/docs"),
        ("Sales Dashboard",       "http://localhost:5175"),
        ("Voice Agent",           "http://localhost:8765"),
    ]
    for label, url in rows:
        print(f"  {'→':2}  {label:<25} {url}")
    print()
    print("Press Ctrl+C to stop all services.")
    print("=" * 55)

    # Keep alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
