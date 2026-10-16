"""
S0 Gate: Scan tree for committed secrets (API keys).
Run: python scripts/scan_secrets.py
"""
import os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PATTERNS = {
    "Gemini/GCP key": re.compile(r'AIza[0-9A-Za-z_-]{35}'),
    "Groq key":       re.compile(r'gsk_[0-9A-Za-z]{40,}'),
    "OpenAI key":     re.compile(r'sk-[0-9A-Za-z]{40,}'),
    "GitHub token":   re.compile(r'gh[pousr]_[0-9A-Za-z]{36,}'),
}

SKIP_DIRS = {'.venv', 'venv', 'node_modules', '__pycache__', '.git', 'dist', 'build'}
SKIP_FILES = {'uv.lock', 'package-lock.json', 'requirements-frozen.txt'}

hits = []
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for file in files:
        if file in SKIP_FILES:
            continue
        filepath = Path(root) / file
        try:
            text = filepath.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for label, pat in PATTERNS.items():
            for m in pat.finditer(text):
                # Don't flag placeholders
                if "YOUR_" in val or "your_" in val or "xxx" in val.lower() or "REPLACE" in val:
                    continue
                hits.append(f"  [{label}] {filepath.relative_to(ROOT)}: key pattern found (redacted)")

if hits:
    print("⚠️  POTENTIAL SECRETS FOUND — ROTATE THESE KEYS:")
    for h in set(hits):
        print(h)
    sys.exit(1)
else:
    print("✅ No secrets pattern found in tracked files.")
