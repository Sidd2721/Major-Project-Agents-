"""
SmartOps AI — Root Unified Platform Launcher
Run this from the repository root to start all services:
    python run_all.py
"""
import sys
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SMARTOPS_DIR = ROOT / "smartops-ai"
RUN_SCRIPT = SMARTOPS_DIR / "scripts" / "run_all.py"

def main():
    if not RUN_SCRIPT.exists():
        print(f"❌ Error: Could not locate launcher script at {RUN_SCRIPT}")
        sys.exit(1)
    
    cmd = [sys.executable, str(RUN_SCRIPT)] + sys.argv[1:]
    res = subprocess.run(cmd, cwd=str(SMARTOPS_DIR))
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
