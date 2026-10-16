"""
SmartOps AI — Root Automated Verification Suite
Run this from the repository root to verify all 17 system points:
    python verify.py
"""
import sys
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SMARTOPS_DIR = ROOT / "smartops-ai"
VERIFY_SCRIPT = SMARTOPS_DIR / "scripts" / "verify.py"

def main():
    if not VERIFY_SCRIPT.exists():
        print(f"❌ Error: Could not locate verify script at {VERIFY_SCRIPT}")
        sys.exit(1)
    
    cmd = [sys.executable, str(VERIFY_SCRIPT)] + sys.argv[1:]
    res = subprocess.run(cmd, cwd=str(SMARTOPS_DIR))
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
