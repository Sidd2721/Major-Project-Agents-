# SmartOps AI — Design Tokens Reference

This document defines the core tokens used across all SmartOps AI user interfaces, implemented in `shared/tokens.css` and `shared/components.css`.

## 1. Color Palette

### Brand Colors
- `--color-brand`: `#4f46e5` (Primary Indigo)
- `--color-brand-dark`: `#3730a3` (Hover & active)
- `--color-brand-light`: `#818cf8` (Accents & focus rings)
- `--color-brand-subtle`: `rgba(79, 70, 229, 0.12)`

### Neutral Scale (Dark Theme)
- `--color-neutral-900`: `#0f172a` (Primary page background)
- `--color-neutral-800`: `#1e293b` (Card & panel surface)
- `--color-neutral-700`: `#334155` (Borders & dividers)
- `--color-neutral-400`: `#94a3b8` (Muted secondary text)
- `--color-neutral-100`: `#f1f5f9` (Primary readable text)

### Semantic Priority Tokens (Always paired with text labels)
- **P1 Critical**: `--color-p1`: `#dc2626` | Background: `rgba(220, 38, 38, 0.15)`
- **P2 High**: `--color-p2`: `#ea580c` | Background: `rgba(234, 88, 12, 0.15)`
- **P3 Medium**: `--color-p3`: `#ca8a04` | Background: `rgba(202, 138, 4, 0.15)`
- **P4 Low**: `--color-p4`: `#16a34a` | Background: `rgba(22, 163, 74, 0.15)`

---

## 2. Typography
- **Font Stack**: `--font-sans`: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Monospace Stack**: `--font-mono`: `ui-monospace, "Cascadia Code", "Fira Code", monospace`
- **Scale**:
  - `12px` (`--text-xs`): Badges, timestamps, captions
  - `14px` (`--text-sm`): Secondary body, form labels
  - `16px` (`--text-base`): Main body text
  - `20px` (`--text-lg`): Subheadings & card titles
  - `24px` (`--text-xl`): Section headers
  - `32px` (`--text-2xl`): Page headers

---

## 3. Spacing & Radius
- **Base Grid**: 4px increment scale (4px, 8px, 12px, 16px, 20px, 24px, 32px)
- **Border Radius**:
  - Small: `6px` (`--radius-sm`) for inputs and buttons
  - Medium: `10px` (`--radius-md`) for panels and strips
  - Large: `16px` (`--radius-lg`) for main cards and modals

---

## 4. Elevation & Shadows
- `--shadow-sm`: `0 1px 3px rgba(0, 0, 0, 0.12)`
- `--shadow-md`: `0 4px 12px rgba(0, 0, 0, 0.18)`
- `--shadow-lg`: `0 12px 32px rgba(0, 0, 0, 0.28)`
