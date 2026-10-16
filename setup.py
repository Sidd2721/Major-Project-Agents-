"""
SmartOps AI — Root Setup Launcher
Run this from the repository root on any fresh Windows computer:
    python setup.py
"""
import sys
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SMARTOPS_DIR = ROOT / "smartops-ai"
SETUP_SCRIPT = SMARTOPS_DIR / "scripts" / "setup.py"

def main():
    print("=" * 65)
    print("🚀 SMARTOPS AI — ROOT SETUP BOOTSTRAP")
    print("=" * 65)
    if not SETUP_SCRIPT.exists():
        print(f"❌ Error: Could not locate setup script at {SETUP_SCRIPT}")
        sys.exit(1)
    
    # Run the setup script using the current Python interpreter
    cmd = [sys.executable, str(SETUP_SCRIPT)] + sys.argv[1:]
    res = subprocess.run(cmd, cwd=str(SMARTOPS_DIR))
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
