# Photon Design System

This file is read before ANY frontend code is written or modified.
No exceptions. Every component, every page, every color must follow
this specification. "Close enough" is not acceptable.

Visual reference: Linear.app, Vercel dashboard, Retool dark mode.
Not Bootstrap dark. Not basic Tailwind. Not Material UI.
Everything must look intentional and professional.

---

## Color tokens — use these exact values, no improvising

```css
/* Backgrounds — layered depth system */
--bg-base: #09090b;          /* page background */
--bg-surface: #111113;       /* cards, panels */
--bg-elevated: #1a1a1f;      /* modals, dropdowns, hover states */
--bg-overlay: #222228;       /* tooltips, popovers */

/* Borders */
--border-subtle: #1f1f26;    /* default borders */
--border-default: #2a2a35;   /* inputs, cards */
--border-strong: #3a3a48;    /* focused states, dividers */

/* Text */
--text-primary: #f4f4f5;     /* headings, primary content */
--text-secondary: #a1a1aa;   /* labels, descriptions */
--text-tertiary: #71717a;    /* placeholders, disabled */
--text-inverse: #09090b;     /* text on accent backgrounds */

/* Accent — electric indigo */
--accent-primary: #6366f1;   /* primary buttons, links, active states */
--accent-hover: #4f46e5;     /* hover on accent */
--accent-muted: #1e1b4b;     /* accent backgrounds, badges */
--accent-border: #3730a3;    /* accent borders */

/* Semantic */
--success: #22c55e;
--success-muted: #052e16;
--warning: #f59e0b;
--warning-muted: #1c1408;
--error: #ef4444;
--error-muted: #1a0a0a;
--info: #3b82f6;
--info-muted: #0c1a2e;

/* KPI delta colors */
--delta-positive: #4ade80;
--delta-negative: #f87171;
--delta-neutral: #a1a1aa;
```

---

## Typography — Inter font, loaded from Google Fonts

```
Font: Inter (weights: 400, 500, 600, 700)
Import: https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap

Monospace: JetBrains Mono or Fira Code (for code blocks)
Import: https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap

Scale:
- Display: 48px / 700 / -0.02em tracking / line-height 1.1
- H1: 32px / 700 / -0.01em / 1.2
- H2: 24px / 600 / -0.005em / 1.3
- H3: 18px / 600 / 0 / 1.4
- Body: 14px / 400 / 0 / 1.6
- Small: 12px / 400 / 0.01em / 1.5
- Label: 11px / 500 / 0.05em / 1.4 (UPPERCASE for section labels)
- Code: 13px / 400 / 0 / 1.7 (JetBrains Mono)
```

---

## Spacing system — 4px base, never deviate

```
4px  — xs  (tight gaps, icon padding)
8px  — sm  (inline spacing, badge padding)
12px — md  (compact component padding)
16px — lg  (standard component padding)
24px — xl  (section gaps, card padding)
32px — 2xl (major section spacing)
48px — 3xl (page sections)
64px — 4xl (hero sections)
```

---

## Border radius

```
2px  — subtle (tags, small badges)
6px  — default (inputs, buttons, cards)
8px  — medium (larger cards, panels)
12px — large (modals, hero cards)
full — pills (status badges, chips)
```

---

## Shadows

```css
/* Cards */
box-shadow: 0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.6);

/* Elevated panels */
box-shadow: 0 4px 6px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.4);

/* Modals */
box-shadow: 0 20px 25px rgba(0,0,0,0.6), 0 10px 10px rgba(0,0,0,0.4);

/* Glow on accent elements */
box-shadow: 0 0 0 1px var(--accent-primary), 0 0 20px rgba(99,102,241,0.15);
```

---

## Component specifications

### Primary Button
```
Background: var(--accent-primary)
Text: white, 14px, weight 500
Padding: 8px 16px
Border radius: 6px
Hover: background var(--accent-hover), transform scale(1.01)
Active: transform scale(0.99)
Transition: all 150ms ease
No box-shadow on default state
Focus: outline 2px var(--accent-primary), outline-offset 2px
Disabled: opacity 0.4, cursor not-allowed
```

### Secondary Button
```
Background: var(--bg-elevated)
Border: 1px solid var(--border-default)
Text: var(--text-primary), 14px, weight 500
Padding: 8px 16px
Border radius: 6px
Hover: background var(--bg-overlay), border-color var(--border-strong)
Transition: all 150ms ease
```

### Input / Textarea
```
Background: var(--bg-surface)
Border: 1px solid var(--border-default)
Text: var(--text-primary), 14px
Placeholder: var(--text-tertiary)
Padding: 10px 12px
Border radius: 6px
Focus: border-color var(--accent-primary), outline none,
       box-shadow 0 0 0 3px rgba(99,102,241,0.15)
Transition: border-color 150ms ease, box-shadow 150ms ease
```

### Card
```
Background: var(--bg-surface)
Border: 1px solid var(--border-subtle)
Border radius: 8px
Padding: 24px
No default shadow — add only when elevated above page
```

### KPI Card
```
Background: var(--bg-surface)
Border: 1px solid var(--border-subtle)
Border radius: 8px
Padding: 20px
Label: 11px, UPPERCASE, weight 500, color var(--text-tertiary),
       letter-spacing 0.05em
Value: 28px, weight 700, color var(--text-primary)
Delta: 12px, weight 500 — green if positive, red if negative
       Include ▲ or ▼ arrow glyph
Trend spark: small 40x20px sparkline if data available
Hover: border-color var(--border-default), slight background shift
```

### Badge / Status pill
```
Padding: 2px 8px
Border radius: 999px (full)
Font: 11px, weight 500, uppercase, letter-spacing 0.05em
Variants:
  tabular:     bg #1e1b4b, text #a5b4fc, border #3730a3
  time_series: bg #052e16, text #86efac, border #166534
  wide_format: bg #2e1065, text #d8b4fe, border #7e22ce
  success:     bg var(--success-muted), text var(--success)
  error:       bg var(--error-muted), text var(--error)
  warning:     bg var(--warning-muted), text var(--warning)
```

### Code block
```
Background: #0d0d0f
Border: 1px solid var(--border-subtle)
Border radius: 6px
Font: JetBrains Mono, 13px
Text: #e4e4e7
Padding: 16px
Scrollable: overflow-x auto
Line height: 1.7
```

### Chat message — user
```
Alignment: right
Background: var(--accent-muted)
Border: 1px solid var(--accent-border)
Border radius: 12px 12px 2px 12px
Padding: 10px 14px
Text: var(--text-primary), 14px
Max width: 75%
```

### Chat message — assistant (insight narrative)
```
Alignment: left
Background: var(--bg-surface)
Border: 1px solid var(--border-subtle)
Border radius: 12px 12px 12px 2px
Padding: 14px 16px
Text: var(--text-primary), 14px, line-height 1.7
Max width: 85%
```

### Follow-up suggestion chip
```
Background: var(--bg-elevated)
Border: 1px solid var(--border-default)
Border radius: 999px
Padding: 6px 12px
Font: 12px, weight 500, color var(--text-secondary)
Hover: border-color var(--accent-primary), color var(--text-primary),
       background var(--accent-muted)
Cursor: pointer
Transition: all 150ms ease
```

### Loading skeleton
```
Background: linear-gradient(
  90deg,
  var(--bg-elevated) 25%,
  var(--bg-overlay) 50%,
  var(--bg-elevated) 75%
)
Background-size: 200% 100%
Animation: shimmer 1.5s infinite
Border radius: matches the component being loaded
Never use a spinner for content loading — always skeleton
```

---

## Page layouts

### Landing page
```
Full viewport height hero section:
  - Background: var(--bg-base) with subtle radial gradient
    background: radial-gradient(ellipse at 50% 0%,
    rgba(99,102,241,0.08) 0%, transparent 60%), var(--bg-base)
  - Centered content, max-width 640px
  - Badge pill at top: "Open Source · Self-Hostable"
  - H1 display text: "Your data, analyzed."
  - Subheading: one sentence, var(--text-secondary)
  - Two CTAs: primary "Try the demo" + secondary "View on GitHub"
  - Below fold: feature highlights, 3 columns

Feature section (3 columns):
  Icon + H3 + body text
  Icons from lucide-react (20px, var(--accent-primary))
  No card borders — just spacing and typography
```

### Analysis workspace
```
Layout: 100vh, no scroll on outer container
Left panel (380px fixed, not resizable in v1):
  - Background: var(--bg-surface)
  - Right border: 1px solid var(--border-subtle)
  - Top: file/URL input area (collapsible after upload)
  - Middle: conversation thread (scrollable)
  - Bottom: message input (fixed to panel bottom)

Right panel (flex-1):
  - Background: var(--bg-base)
  - Scrollable
  - Top: KPI cards row (horizontal scroll if overflow)
  - Middle: charts (full width)
  - Below charts: insight narrative card
  - Bottom: anomaly callouts (if any)
  - Code block (collapsible, closed by default)
```

### Navbar
```
Height: 56px
Background: var(--bg-surface) / 80% opacity
Backdrop-filter: blur(12px)
Border-bottom: 1px solid var(--border-subtle)
Position: fixed top
Left: Logo (Photon wordmark, Inter 600, white) + version badge
Right: GitHub link (icon + "Star on GitHub"), Demo button
No other nav items in v1
```

---

## Animations and transitions

```css
/* Standard transition for interactive elements */
transition: all 150ms ease;

/* Page transitions — fade in on load */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeIn 200ms ease forwards; }

/* Skeleton shimmer */
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* KPI card entrance — staggered */
Delay each KPI card by 50ms × index

/* Analysis step progress */
Each step fades in as it completes, not all at once
```

---

## Icons

Use lucide-react exclusively. Size 16px for inline, 20px for standalone.
Color: inherit from parent text color unless semantic.
Never use emoji as icons.

Key icons:
- Upload: Upload
- Chart: BarChart2
- Insight: Lightbulb
- Anomaly: AlertTriangle
- Follow-up: MessageCircle
- Code: Code2
- Pipeline: GitBranch
- Success: CheckCircle2
- Error: XCircle
- Loading: Loader2 (animate-spin)
- GitHub: Github (from lucide-react)

---

## What NOT to do — explicit prohibitions

- No white or light backgrounds anywhere
- No default blue (#3b82f6) as primary — use indigo (#6366f1)
- No rounded-full on rectangular elements (buttons, inputs)
- No drop shadows on text
- No gradient text (looks cheap)
- No hover effects that change layout/size significantly
- No more than 3 font sizes visible at once in a component
- No centered body text in paragraphs (left align only)
- No spinning loading indicators for content — use skeletons
- No toast notifications popping from corners — use inline feedback
- No "NASA Data Portal" anywhere
- No "Built for researchers" anywhere
- No copyright 2025 — use 2026
