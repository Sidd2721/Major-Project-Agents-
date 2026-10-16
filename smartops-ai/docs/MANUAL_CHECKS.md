# SmartOps AI — Manual Verification Checklist & Localhost Audit

Automated verification tests run via `python scripts/verify.py` and are recorded in `docs/VERIFICATION.md`.
The following physical checks have been executed on `http://localhost:5175` and all linked services.

## Phase E: Sales Outreach Assistant Localhost Checklist

| # | Check Item | Status | Real Evidence & Details |
|---|---|---|---|
| **E1** | **Multi-width layout & zero horizontal scroll** | ✅ **PASS** | Verified at 1920x1080, 1280x800, 768x1024, and 375x667. Zero horizontal scrollbar detected. Screenshots saved in `docs/screens/sales_1920.png`, `sales_1280.png`, `sales_768.png`, `sales_375.png`. |
| **E2** | **No forbidden strings in main view** | ✅ **PASS** | Verified zero occurrences of port badges (`:5175`), old banners (`Major Project Live Demonstration`), raw error codes (`HTTP 403`), or raw markdown (`**`) in rendered view. |
| **E3** | **Shared top bar & mode badge visible** | ✅ **PASS** | Top navigation bar rendered via `shared/nav.js` with active `Sales` link. Mode badge correctly displays `MOCK MODE` via `/api/mode`. |
| **E4** | **Strong-fit prospect workflow & progress** | ✅ **PASS** | Selected `Alex Mercer` (Apex Dynamics). Clicked *Prepare outreach*. Plain-English progress steps completed in sequence with zero console errors. |
| **E5** | **Verdict card (Standout element)** | ✅ **PASS** | Displays green `Good fit` badge, **8.5 out of 10** fit score, 3 plain-language reasons, matching success story citation (*"Similar to Spark Retail..."*), and data quality line (*"Based on 4 of 5 sources • High confidence"*). |
| **E6** | **Email draft card** | ✅ **PASS** | Subject and personalized body shown with label *"Draft only. Nothing has been sent."* Clicked *Copy email* (toast confirmation displayed). Clicked *Mark as contacted* (status updated to *Contacted*). |
| **E7** | **Call script card** | ✅ **PASS** | Displays conversational opening hook, 3 discovery questions, 2 anticipated objections with scripted replies, and expandable full pitch. |
| **E8** | **Research accordion & friendly errors** | ✅ **PASS** | Sources show `Read` or `Could not read`. Failed sources show friendly message: *"This site blocks automated reading, so we skipped it"* with technical detail behind *Show details*. Supporting dossiers rendered with local safe markdown. |
| **E9** | **Poor-fit prospect handling** | ✅ **PASS** | Selected `Timmy Small` (Solo Blogger). Result returned `Not a fit right now`, score **2.8 out of 10**, plain-language advice, and zero email drafted (*"Outreach is intentionally withheld for low-fit prospects"*). Zero crashes. |
| **E10** | **Offline zero-key operation** | ✅ **PASS** | Tested with no API keys in `LLM_MODE=mock` and replay mode. All flows complete deterministically and signal sample/demo status clearly. |
| **E11** | **Keyboard-only navigation (A11y)** | ✅ **PASS** | Tabbing moves through selector, inputs, *Prepare outreach* button, copy button, and accordion triggers with high-contrast focus rings (`outline: 2px solid #4f46e5; outline-offset: 2px`). |
| **E12** | **Page refresh resilience** | ✅ **PASS** | Reloading `http://localhost:5175/` instantly restores the last prepared result and prospect selection without blank states or re-computation. |
| **E13** | **Other services unaffected** | ✅ **PASS** | All 6 services confirmed online and healthy: Hub (`:8080`), Customer Portal (`:5173`), Employee Dashboard (`:5174`), Support API (`:8000`), Sales Assistant (`:5175`), Voice Console (`:8765`). |

---

## Action Items for the User / Presenter

1. **Rotate Leaked API Keys**:
   - The git history scan revealed that legacy Groq key fragments existed in early commits of `docs/KNOWN_ISSUES.md`.
   - Visit [Groq Console](https://console.groq.com/keys) and delete/revoke legacy keys.
   - Generate a fresh API key and save it strictly in your local uncommitted `.env`.

2. **Chrome Microphone Permission Check**:
   - Open `http://localhost:8765` in Chrome or Edge.
   - When prompted for microphone access, select **Allow**.
   - Speak: *"Hello, what is your role?"*
   - Confirm the waveform activates and the synthesized voice audio plays through your speakers. (If audio hardware is absent, use the fallback text prompt).
