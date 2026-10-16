# SmartOps AI — Manual Verification Checklist

Automated tests in `scripts/verify.py` cover API status, mock outputs, regression bugs, and auth guards.
The following physical checks should be conducted manually prior to the final viva presentation.

## Checklist for the User / Presenter

- [ ] **1. Rotate Leaked API Keys**:
  - Visit [Groq Console](https://console.groq.com/keys) and delete the previously committed key (`gsk_wcRON2Yf...`).
  - Generate a fresh API key and save it securely.

- [ ] **2. Chrome Microphone Permission Check**:
  - Open `http://localhost:8765` in Chrome or Edge.
  - When prompted for microphone access, select **Allow**.
  - Speak: *"Hello, what is your role?"*
  - Confirm the waveform activates and the synthesized voice audio plays through your speakers.

- [ ] **3. Text Fallback Validation**:
  - On `http://localhost:8765`, type *"How many open P1 tickets are there?"* into the text box and press Enter.
  - Confirm the response cites the exact live DB count without requiring audio hardware.

- [ ] **4. Keyboard-Only Navigation (A11y)**:
  - Open `http://localhost:8080` (Hub) and press `Tab`.
  - Confirm visible focus rings appear around all navigation links and "How It Works" buttons.

- [ ] **5. Presentation Slides Verification**:
  - Review your project presentation slides against `docs/SLIDES_MAPPING.md`.
  - Confirm Email and Invoice agents are clearly marked as **Planned (Semester 2)** and that cold calling is described as **Browser Voice Simulation**.
