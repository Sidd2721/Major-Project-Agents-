"""
SmartOps AI — One-command setup.
Run: python scripts/setup.py               # set up everything
     python scripts/setup.py --agent sales  # set up only the sales agent
     python scripts/setup.py --agent support
     python scripts/setup.py --agent voice
     python scripts/setup.py --agent all    # same as no flag

Creates venvs, installs dependencies, copies .env.example -> .env (if missing),
pins versions. Cross-platform (Windows + macOS/Linux).
"""
import subprocess, sys, shutil, os, argparse
from pathlib import Path

# Fix Windows console UTF-8 centrally
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
WIN = sys.platform == "win32"

def run(cmd, cwd=None, env=None):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    r = subprocess.run(cmd, cwd=cwd, env=env)
    if r.returncode != 0:
        print(f"  ❌ FAILED (exit {r.returncode})")
        sys.exit(r.returncode)

def venv_python(venv_path):
    if WIN:
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"

def venv_pip(venv_path):
    if WIN:
        return venv_path / "Scripts" / "pip.exe"
    return venv_path / "bin" / "pip"

def setup_venv(name, folder, requirements):
    print(f"\n{'='*50}")
    print(f"📦 Setting up: {name}")
    print(f"{'='*50}")
    venv = folder / "venv"
    if not venv.exists():
        run([sys.executable, "-m", "venv", str(venv)])
    else:
        print("  ✓ venv already exists, upgrading pip")
    run([str(venv_python(venv)), "-m", "pip", "install", "--upgrade", "pip", "-q"])
    run([str(venv_pip(venv)), "install", "-r", str(requirements), "-q"])
    print(f"  ✅ {name} ready")
    return venv

def copy_env(folder):
    env_ex = folder / ".env.example"
    env_f  = folder / ".env"
    if env_ex.exists() and not env_f.exists():
        shutil.copy(env_ex, env_f)
        print(f"  📋 Copied .env.example -> .env in {folder.name}")
    elif not env_f.exists():
        env_f.write_text("# Add your keys here\nGROQ_API_KEY=\nGEMINI_API_KEY=\nLLM_MODE=mock\n")
        print(f"  📋 Created empty .env in {folder.name}")

def setup_node(name, folder):
    if not (folder / "package.json").exists():
        return
    nm = folder / "node_modules"
    if nm.exists():
        print(f"  ✓ {name} node_modules already installed")
        return
    print(f"\n{'='*50}")
    print(f"📦 npm install: {name}")
    print(f"{'='*50}")
    run(["npm", "install", "--prefer-offline"], cwd=folder)
    print(f"  ✅ {name} npm ready")

def setup_support():
    csa = ROOT / "Customer-Support-Agent"
    if not csa.exists():
        print("⚠️  Customer-Support-Agent not found, skipping"); return
    setup_venv("Customer Support Agent", csa, csa / "requirements.txt")
    copy_env(csa)
    for ui in ["Frontend/customer", "Frontend/employee-dashboard"]:
        p = csa / ui
        if p.exists():
            setup_node(f"Customer UI — {ui.split('/')[-1]}", p)

def setup_sales():
    sales = ROOT / "sales_agent_module"
    if not sales.exists():
        print("⚠️  sales_agent_module not found, skipping"); return
    setup_venv("Sales Outreach Agent", sales, sales / "requirements.txt")
    copy_env(sales)

def setup_voice():
    voice = ROOT / "gemini-voice-agent"
    if not voice.exists():
        print("⚠️  gemini-voice-agent not found, skipping"); return
    uv = shutil.which("uv")
    if uv:
        print(f"\n{'='*50}")
        print("📦 Setting up: Voice Agent (uv)")
        print(f"{'='*50}")
        run([uv, "sync"], cwd=voice)
    else:
        req = voice / "requirements.txt"
        if not req.exists():
            req.write_text("fastapi\nuvicorn\npython-dotenv\nhttpx\ngoogle-generativeai\ngroq\n")
        setup_venv("Voice Agent", voice, req)
    copy_env(voice)

def seed_data():
    print(f"\n{'='*50}")
    print("🌱 Seeding demo data (12 tickets, 5 leads, replay)...")
    print(f"{'='*50}")
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from seed_demo import run_reset
        res = run_reset()
        print(f"  ✅ Seeded {res['tickets_seeded']} tickets and {res['leads_seeded']} leads in {res['duration_seconds']}s")
    except Exception as e:
        print(f"  ⚠️ Could not seed demo data: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="SmartOps AI — install dependencies for one or all agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup.py                  # install all agents
  python scripts/setup.py --agent sales    # install only Sales agent
  python scripts/setup.py --agent support  # install only Customer Support agent
  python scripts/setup.py --agent voice    # install only Voice agent
  python scripts/setup.py --agent all      # same as no flag
        """,
    )
    parser.add_argument("--agent", choices=["support", "sales", "voice", "all"],
                        default="all", help="Which agent to set up (default: all)")
    args = parser.parse_args()

    agent = args.agent
    print(f"\n🚀 SmartOps AI — Setup ({agent})")
    print("=" * 50)

    if agent in ("support", "all"):
        setup_support()
    if agent in ("sales", "all"):
        setup_sales()
    if agent in ("voice", "all"):
        setup_voice()
    if agent == "all":
        seed_data()

    print("\n" + "="*50)
    print("✅ Setup complete!")
    print()
    print("Next steps:")
    print("  1. Edit .env files in each agent folder and add your API keys")
    print("     OR leave blank for LLM_MODE=mock (offline demo, no keys needed)")
    if agent == "all":
        print("  2. Run: python scripts/run_all.py")
    else:
        print(f"  2. Run: python scripts/run_agent.py {agent}")
    print("="*50)

if __name__ == "__main__":
    main()
