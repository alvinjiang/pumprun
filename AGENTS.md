# AGENTS.md — Standing Instructions for defihodler

## Communication Protocol

This project uses three files for agent-to-agent communication:

| File | Direction | Purpose |
|------|-----------|---------|
| `NOTES.md` | Implementor → Design | Implementation decisions, spec change requests, technical judgements made |
| `bugfix-tracker.md` | Reviewer → Implementor | Bugs found, severity, reproduction steps |
| `SPEC.md` | Design → Implementor | Authoritative spec. Updated by design agent when NOTES.md requests a ruling |

### When Implementing
- Log every non-obvious implementation decision in `NOTES.md` with date and rationale
- If a spec gap forces you to make a judgement call, implement it and file a request in `NOTES.md` for the design agent to update `SPEC.md`
- Read `bugfix-tracker.md` before starting work

### When Reviewing
- File bugs in `bugfix-tracker.md` with: date, severity (P0/P1/P2), description, reproduction steps
- P0: broken/crashes; P1: wrong behavior; P2: cosmetic
- Reference the file and line if possible

### When Designing
- Read `NOTES.md` for outstanding spec-change requests before updating `SPEC.md`
- After updating spec, note in `NOTES.md` that the request was resolved

## Build Pipeline

The web client is built via a Python script that:
1. Reads `design/data/basket_returns.bin`, `design/data/btcusdt.json`, `design/data/index.json`
2. Embeds them as base64/JSON into a JS string
3. Verifies JS syntax with `node --check`
4. Injects the JS into `web/index.html` replacing the existing `<script>` block

**Always regenerate** — never hand-edit the JS inside `web/index.html`. Edit the Python build script or the JS template it generates, then rebuild.

## Project Structure

```
defihodler/
├── design/           # Specs, mocks, data, lore — DESIGN AGENT DOMAIN
│   ├── SPEC.md       # Authoritative design spec
│   ├── NOTES.md      # Implementation decisions log
│   ├── LORE.md       # Game flavor, events, depeg history
│   ├── COLORS.md     # Color palette
│   ├── CRYPTO_EVENTS.md
│   ├── PRICE_TIERS.md
│   ├── DESIGN-NOTES.md
│   ├── NOTEST.md     # (this file - bugfix tracking TBD)
│   ├── mockup-v30.html
│   └── data/         # Pre-computed datasets
├── web/              # Web client — IMPLEMENTOR DOMAIN
│   └── index.html    # Single-file app (built, not hand-edited JS)
├── server/           # Backend API (TBD)
├── AGENTS.md         # This file
└── bugfix-tracker.md # Bug tracker
```

## Key Design Decisions (Don't Re-litigate)

- Window: 365 days, $10,000 start
- Basket: 30-day vol, top 5, 14-day persistence, equal-weight
- Chart: 3 lines — green (ALTS), red (BTC), yellow (YOU)
- Font: SF Mono (system), plain zero
- Colors: sampled from cryptowat.ch (see COLORS.md)
- No Q key to toggle summary — only shows on game finish
- Unwinnable windows (~7.5%): matching badger = HODLER stamp, never DEGEN
- Countdown defaults to YOLO (FOMO), player can toggle during countdown
- BTC quantity is static during HODL mode
- Season tags and price tiers are client-side (server-side in production)
