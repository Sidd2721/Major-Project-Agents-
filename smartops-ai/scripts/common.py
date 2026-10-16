"""
SmartOps AI — Shared Script Utilities & Health Checkers
Centralizes UTF-8 encoding fix, port management, health verification, and venv resolution.
"""
import os
import sys
import time
import socket
import subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# 1. Central Windows UTF-8 console encoding fix
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    os.environ["PYTHONIOENCODING"] = "utf-8"

# 2. Key Directories
ROOT = Path(__file__).resolve().parent.parent
CSA_DIR = ROOT / "Customer-Support-Agent"
SALES_DIR = ROOT / "sales_agent_module"
VOICE_DIR = ROOT / "gemini-voice-agent"
HUB_DIR = ROOT / "hub"
SHARED_DIR = ROOT / "shared"
DOCS_DIR = ROOT / "docs"

# 3. Ports & Service Definitions
SERVICES = {
    8000: {"name": "Customer Support API", "health": "http://localhost:8000/health", "mode": "http://localhost:8000/api/mode"},
    5173: {"name": "Customer Portal", "health": "http://localhost:5173", "mode": None},
    5174: {"name": "Employee Dashboard", "health": "http://localhost:5174", "mode": None},
    5175: {"name": "Sales Dashboard", "health": "http://localhost:5175/health", "mode": "http://localhost:5175/api/mode"},
    8765: {"name": "Voice Agent", "health": "http://localhost:8765/api/health", "mode": "http://localhost:8765/api/mode"},
    8080: {"name": "Central Hub", "health": "http://localhost:8080", "mode": None},
}

def port_free(port: int) -> bool:
    """Checks whether a TCP port is available on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0

def kill_process_on_port(port: int) -> None:
    """Terminates any process holding a specific port on Windows."""
    if sys.platform != "win32":
        return
    try:
        cmd = f'Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique'
        res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        pids = [p.strip() for p in res.stdout.splitlines() if p.strip() and p.strip() != "0"]
        for pid in pids:
            subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
    except Exception:
        pass

def venv_python(folder: Path) -> Path:
    """Finds the Python executable inside a folder's virtualenv."""
    candidates = [
        folder / "venv" / "Scripts" / "python.exe",
        folder / ".venv" / "Scripts" / "python.exe",
        folder / "venv" / "bin" / "python",
        folder / ".venv" / "bin" / "python",
    ]
    for c in candidates:
        if c.exists():
            return c
    return Path(sys.executable)

def venv_uvicorn(folder: Path) -> str:
    """Finds uvicorn inside a virtualenv."""
    u = folder / "venv" / "Scripts" / "uvicorn.exe"
    if u.exists():
        return str(u)
    u_dot = folder / ".venv" / "Scripts" / "uvicorn.exe"
    if u_dot.exists():
        return str(u_dot)
    return "uvicorn"

def wait_health(url: str, timeout: int = 40, label: str = "") -> bool:
    """Polls a URL until it returns 200 or timeout expires."""
    start = time.time()
    req = Request(url, headers={"User-Agent": "SmartOps-HealthChecker/1.0"})
    while time.time() - start < timeout:
        try:
            with urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False
