# SmartOps AI — Known Issues & Remediation Guide

This document transparently records known constraints, security findings, and recommended manual actions for the user and evaluation panel.

## 1. Security: Leaked API Keys in Legacy Subdirectories
- **Symptom**: Automated secret scanner (`scripts/scan_secrets.py`) detected active Groq API keys committed inside legacy environment files in previous unpolished branches.
- **Root Cause**: Early exploratory development lacked `.gitignore` enforcement for local environment files.
- **Remediation**:
  1. All `.env` files are now strictly added to `.gitignore` and `.env.example` templates are provided.
  2. **USER ACTION REQUIRED**: Go to [console.groq.com](https://console.groq.com/keys), revoke any previously active legacy keys, and generate a fresh key.
  3. Insert the new key into `.env` only when running with `LLM_MODE=live`.

---

## 2. LLM Provider Rate Limits (Gemini Free Tier)
- **Symptom**: Google Gemini free-tier keys enforce a strict rate limit (~15-20 requests/minute and daily caps). High-volume test runs previously crashed with HTTP 429.
- **Workaround**:
  - The Sales Agent module persists full successful runs to `data/replay/sales_replay.json`.
  - When demonstrating to project guides, run with `LLM_MODE=mock` or `LLM_MODE=replay` to guarantee zero dependency on external cloud quotas.

---

## 3. LinkedIn Anti-Scraping Defenses
- **Symptom**: Autonomous headless scraping of LinkedIn profiles triggers Cloudflare bot challenges or IP blocks.
- **Workaround**:
  - Outbound scraping is disabled by default (`ENABLE_LINKEDIN_SCRAPE=false`).
  - The pipeline accepts pre-loaded CRM lead records (from `data/samples/leads.json` or Airtable) and clearly flags them with a `DEMO LEAD` badge in the UI.

---

## 4. Web Speech API Permissions in Certain Browsers
- **Symptom**: Web Speech audio recognition in Chrome or Brave may be blocked if microphone permissions are denied or if running over insecure non-localhost IPs.
- **Workaround**:
  - A permanent text-input fallback box is provided at the bottom of `web_client.html` on `:8765`.
  - The system operates via local WebSockets with full bidirectional text capability even when audio hardware is unavailable.
