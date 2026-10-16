# Baseline Audit & Evidence Summary

- **Audit Date**: October 2026
- **Branch**: `polish/stabilize-and-explain`
- **Baseline Git Tag**: `pre-polish`
- **Evaluated Subsystems**:
  1. Customer Support Agent (Port 8000, 5173, 5174)
  2. Sales Outreach Agent (Port 5175)
  3. Voice Simulation Agent (Port 8765)

## 1. Secret Scan Findings
- Leaked Groq API keys identified in legacy `.env` files.
- Remediation: Listed in `docs/KNOWN_ISSUES.md` and user advised to rotate. All `.env` files git-ignored.

## 2. Pinned Package Freezes
- `Customer-Support-Agent/requirements-frozen.txt` generated from active venv.
- `sales_agent_module/requirements-frozen.txt` generated from active venv.
- `gemini-voice-agent/requirements-frozen.txt` generated via `uv pip freeze`.

## 3. Discovered Model Discrepancies
- Customer Support: claims `llama3`, code had `openai/gpt-oss-120b` (invalid model name on Groq).
- Sales: code had `gemini-3.8-flash` and `qwen/qwen3.8-27b`.
- Remediation: Implemented dynamic model querying and safe fallbacks in `shared/llm_helper.py`.
