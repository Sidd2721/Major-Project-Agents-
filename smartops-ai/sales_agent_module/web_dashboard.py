import os
import subprocess
import threading
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SmartOps AI Sales Outreach Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

pipeline_state = {
    "status": "ready",
    "last_run": None,
    "current_step": "idle",
    "logs": []
}

def run_pipeline_task():
    global pipeline_state
    pipeline_state["status"] = "running"
    pipeline_state["current_step"] = "Executing LangGraph Multi-Agent Pipeline..."
    venv_python = BASE_DIR / "venv" / "Scripts" / "python.exe"
    main_script = BASE_DIR / "main.py"
    try:
        proc = subprocess.Popen(
            [str(venv_python), str(main_script)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in proc.stdout:
            pipeline_state["logs"].append(line.strip())
            if len(pipeline_state["logs"]) > 200:
                pipeline_state["logs"].pop(0)
        proc.wait()
        if proc.returncode == 0:
            pipeline_state["status"] = "completed"
            pipeline_state["current_step"] = "Outreach reports generated successfully"
        else:
            pipeline_state["status"] = "finished_with_warnings"
            pipeline_state["current_step"] = f"Finished (Exit code {proc.returncode})"
    except Exception as e:
        pipeline_state["status"] = "error"
        pipeline_state["current_step"] = str(e)

@app.get("/api/reports")
def get_reports():
    reports = []
    if REPORTS_DIR.exists():
        for file in sorted(REPORTS_DIR.glob("*.txt")):
            try:
                content = file.read_text(encoding="utf-8")
            except Exception:
                content = file.read_text(encoding="latin-1", errors="ignore")
            reports.append({
                "title": file.stem,
                "filename": file.name,
                "size_kb": round(file.stat().st_size / 1024, 2),
                "content": content
            })
    return {"reports": reports}

@app.get("/api/status")
def get_status():
    return pipeline_state

@app.post("/api/run")
def trigger_run(background_tasks: BackgroundTasks):
    if pipeline_state["status"] == "running":
        return JSONResponse({"status": "already_running", "message": "Pipeline is already running."})
    pipeline_state["logs"] = []
    background_tasks.add_task(run_pipeline_task)
    return {"status": "started", "message": "Autonomous sales outreach agent initiated."}

@app.get("/health")
def health():
    return {"status": "ok", "service": "sales_agent_module"}

@app.get("/api/mode")
def api_mode():
    mode = os.getenv("LLM_MODE", "mock").lower()
    return {"mode": mode, "service": "sales_agent_module", "degraded": (mode == "mock")}

@app.get("/workflow.png")
def get_workflow_diagram():
    img_path = BASE_DIR / "workflow.png"
    if img_path.exists():
        return FileResponse(img_path)
    return JSONResponse({"error": "Workflow image not found"}, status_code=404)

@app.get("/", response_class=HTMLResponse)
def index_page():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SmartOps AI | Sales Outreach Automation Platform</title>
  <style>
    :root {
      --bg-gradient: radial-gradient(circle at 10% 20%, rgb(18, 22, 34) 0%, rgb(10, 13, 20) 90%);
      --card-bg: rgba(22, 28, 45, 0.75);
      --card-border: rgba(255, 255, 255, 0.08);
      --accent-purple: #7952ff;
      --accent-cyan: #00d2ff;
      --accent-gradient: linear-gradient(135deg, #7952ff 0%, #00d2ff 100%);
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --success: #10b981;
      --warning: #f59e0b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background: var(--bg-gradient);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .brand-logo {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: var(--accent-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 1.2rem;
      color: #fff;
      box-shadow: 0 4px 15px rgba(121, 82, 255, 0.4);
    }
    .brand-title {
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }
    .brand-subtitle {
      font-size: 0.8rem;
      color: var(--text-muted);
    }
    .nav-links {
      display: flex;
      gap: 1rem;
      align-items: center;
    }
    .nav-btn {
      text-decoration: none;
      font-size: 0.85rem;
      padding: 0.45rem 0.9rem;
      border-radius: 8px;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      background: rgba(255,255,255,0.03);
      transition: all 0.2s;
    }
    .nav-btn:hover {
      color: #fff;
      border-color: var(--accent-cyan);
      background: rgba(0, 210, 255, 0.1);
    }
    .main-container {
      max-width: 1440px;
      margin: 0 auto;
      padding: 2rem;
      width: 100%;
      display: grid;
      grid-template-columns: 340px 1fr;
      gap: 2rem;
      flex: 1;
    }
    .sidebar {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    .card {
      background: var(--card-bg);
      backdrop-filter: blur(10px);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1.5rem;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .card-title {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: #e2e8f0;
    }
    .badge {
      font-size: 0.7rem;
      padding: 0.2rem 0.6rem;
      border-radius: 20px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .badge-success { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-running { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); animation: pulse 1.5s infinite; }
    .badge-purple { background: rgba(121, 82, 255, 0.2); color: #a78bfa; border: 1px solid rgba(121, 82, 255, 0.4); }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    .lead-info-item {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      padding: 0.5rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .lead-info-item span:first-child { color: var(--text-muted); }
    .lead-info-item span:last-child { font-weight: 500; color: #fff; }
    .btn-run {
      background: var(--accent-gradient);
      color: white;
      border: none;
      padding: 0.85rem 1.25rem;
      border-radius: 10px;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.3s;
      box-shadow: 0 4px 15px rgba(121, 82, 255, 0.4);
      width: 100%;
    }
    .btn-run:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(0, 210, 255, 0.5);
    }
    .content-area {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
    .tabs-bar {
      display: flex;
      gap: 0.5rem;
      overflow-x: auto;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--card-border);
    }
    .tab-btn {
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 0.5rem 1rem;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s;
    }
    .tab-btn.active, .tab-btn:hover {
      background: rgba(121, 82, 255, 0.15);
      color: #fff;
      border-color: var(--accent-purple);
    }
    .report-viewer {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.5rem;
      min-height: 480px;
      font-size: 0.95rem;
      line-height: 1.7;
      white-space: pre-wrap;
      font-family: 'Outfit', sans-serif;
      overflow-y: auto;
      max-height: 600px;
      color: #e2e8f0;
    }
    .report-viewer h1, .report-viewer h2, .report-viewer h3 {
      color: #fff;
      margin: 1.2rem 0 0.6rem 0;
    }
    .workflow-img {
      width: 100%;
      border-radius: 12px;
      border: 1px solid var(--card-border);
      background: #000;
      cursor: pointer;
    }
    .dual-nav-banner {
      background: linear-gradient(90deg, rgba(121, 82, 255, 0.15), rgba(0, 210, 255, 0.15));
      border: 1px solid rgba(121, 82, 255, 0.3);
      border-radius: 12px;
      padding: 1rem 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1rem;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="brand-logo">SO</div>
      <div>
        <div class="brand-title">SmartOps AI Outreach Agent</div>
        <div class="brand-subtitle">LangGraph Multi-Agent Sales & Research Engine</div>
      </div>
    </div>
    <div class="nav-links">
      <span class="badge badge-success">Port 5175 Active</span>
      <a class="nav-btn" href="http://localhost:8765" target="_blank" style="background: rgba(121, 82, 255, 0.25); border-color: var(--accent-purple); color: #fff; font-weight:600;">🎙️ Voice AI Platform (:8765)</a>
      <a class="nav-btn" href="http://localhost:5173" target="_blank">🌐 Customer Portal (:5173)</a>
      <a class="nav-btn" href="http://localhost:5174" target="_blank">📊 Support Dashboard (:5174)</a>
      <a class="nav-btn" href="http://localhost:8000/docs" target="_blank">⚡ API Docs (:8000)</a>
    </div>
  </header>

  <div class="main-container">
    <div class="sidebar">
      <div class="card">
        <div class="card-title">
          <span>Active Pipeline</span>
          <span id="status-badge" class="badge badge-success">Ready</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.25rem;">
          Autonomous research on LinkedIn, Company blogs, YouTube, News, and RAG Case Studies.
        </p>
        <button id="run-btn" class="btn-run" onclick="triggerRun()">
          <span id="run-icon">🚀</span> Run Outreach Workflow
        </button>
      </div>

      <div class="card">
        <div class="card-title">
          <span>Target Lead / CRM</span>
          <span class="badge badge-purple">Qualified</span>
        </div>
        <div class="lead-info-item">
          <span>Lead Name</span>
          <span>John Doe</span>
        </div>
        <div class="lead-info-item">
          <span>Company</span>
          <span>Microsoft Corp</span>
        </div>
        <div class="lead-info-item">
          <span>Target Email</span>
          <span>satya@microsoft.com</span>
        </div>
        <div class="lead-info-item">
          <span>AI Lead Score</span>
          <span style="color: #34d399; font-weight:700;">8.5 / 10</span>
        </div>
        <div class="lead-info-item">
          <span>Status</span>
          <span>ATTEMPTED_TO_CONTACT</span>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>Workflow Architecture</span>
        </div>
        <img src="/workflow.png" alt="LangGraph Architecture Diagram" class="workflow-img" onclick="window.open('/workflow.png', '_blank')">
        <p style="font-size:0.75rem; color: var(--text-muted); margin-top:0.5rem; text-align:center;">Click image to enlarge graph</p>
      </div>
    </div>

    <div class="content-area">
      <div class="dual-nav-banner">
        <div>
          <strong style="color:#fff;">🎯 Major Project Live Demonstration</strong>
          <p style="font-size:0.85rem; color:var(--text-muted); margin-top:0.25rem;">
            Both AI systems running live: Customer Support Agent (:5173, :5174) + Sales Outreach Agent (:5175).
          </p>
        </div>
        <div style="display:flex; gap:0.5rem;">
          <button class="nav-btn" onclick="fetchReports()">🔄 Refresh Reports</button>
        </div>
      </div>

      <div class="card">
        <div class="card-title">
          <span>Generated Intelligence & Outreach Reports</span>
          <span id="report-count" class="badge badge-purple">8 Reports</span>
        </div>
        <div class="tabs-bar" id="tabs-bar">
          <!-- Rendered dynamically -->
        </div>
        <div class="report-viewer" id="report-viewer">
          Loading report contents...
        </div>
      </div>
    </div>
  </div>

  <script>
    let reportsData = [];
    let activeIndex = 0;

    async function fetchReports() {
      try {
        const res = await fetch('/api/reports');
        const data = await res.json();
        reportsData = data.reports || [];
        renderTabs();
        if (reportsData.length > 0) {
          showReport(activeIndex < reportsData.length ? activeIndex : 0);
        } else {
          document.getElementById('report-viewer').innerText = "No reports generated yet. Click 'Run Outreach Workflow' to start!";
        }
        document.getElementById('report-count').innerText = `${reportsData.length} Reports`;
      } catch (e) {
        console.error(e);
      }
    }

    function renderTabs() {
      const tabsBar = document.getElementById('tabs-bar');
      tabsBar.innerHTML = '';
      reportsData.forEach((rep, idx) => {
        const btn = document.createElement('button');
        btn.className = `tab-btn ${idx === activeIndex ? 'active' : ''}`;
        btn.innerText = rep.title;
        btn.onclick = () => showReport(idx);
        tabsBar.appendChild(btn);
      });
    }

    function showReport(idx) {
      activeIndex = idx;
      renderTabs();
      const viewer = document.getElementById('report-viewer');
      if (reportsData[idx]) {
        viewer.innerText = reportsData[idx].content;
      }
    }

    async function triggerRun() {
      const btn = document.getElementById('run-btn');
      const badge = document.getElementById('status-badge');
      btn.disabled = true;
      btn.innerText = "⏳ Pipeline Running...";
      badge.className = "badge badge-running";
      badge.innerText = "Running";
      try {
        await fetch('/api/run', { method: 'POST' });
        pollStatus();
      } catch (e) {
        alert("Error starting pipeline: " + e);
        btn.disabled = false;
        btn.innerText = "🚀 Run Outreach Workflow";
      }
    }

    async function pollStatus() {
      const interval = setInterval(async () => {
        const res = await fetch('/api/status');
        const data = await res.json();
        const badge = document.getElementById('status-badge');
        const btn = document.getElementById('run-btn');
        if (data.status === 'running') {
          badge.className = "badge badge-running";
          badge.innerText = "Running";
        } else {
          clearInterval(interval);
          badge.className = "badge badge-success";
          badge.innerText = "Completed";
          btn.disabled = false;
          btn.innerText = "🚀 Run Outreach Workflow";
          fetchReports();
        }
      }, 3000);
    }

    fetchReports();
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_dashboard:app", host="0.0.0.0", port=5175, reload=False)
