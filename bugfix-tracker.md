# bugfix-tracker.md

Open bugs for defihodler. File format: date, severity, description, repro, status.

| # | Date | Sev | Description | Repro | Status |
|---|------|-----|-------------|-------|--------|
| 1 | 2026-07-19 | P0 | Summary screen doesn't show after game end — `finishGame()` used `verdict`, `stampClass`, `youD`, etc. before assignment (duplicate summary-population block) | Play any game to end | **FIXED** — deleted duplicate broken block, kept correct one with `classList.add('on')` |
| 2 | 2026-07-19 | P0 | `youDollarsFinal is not defined` — `runBananaTest` (module scope) referenced `var youDollarsFinal` from `finishGame` (function scope), unreachable | Banana test would throw, percentile stuck at "—" | **FIXED** — compute `youDollarsFinal` inside `runBananaTest` from `G.btcQty * BTC_PRICE[DATES[G.s+WIN-1]]` |

## Severity Guide
- **P0**: broken/crashes/unplayable
- **P1**: wrong behavior, incorrect values, logic errors
- **P2**: cosmetic, visual glitch, text mismatch
