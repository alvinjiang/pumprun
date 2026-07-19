# defihodler — Implementation Notes

## Build Pipeline

HTML is generated via Python script that embeds data files into a single `index.html`:
- `basket_returns.bin` → base64 → decoded client-side to Float32Array (12.8 KB)
- `btcusdt.json` → compact `[[t, c], ...]` JSON array (120 KB)
- `coin_index.json` → JSON object (2.7 KB)
- JS syntax verified via `node --check` after each build
- Total output: ~134 KB single file

## Game Mechanics Implementation

### Position Model
- BTC quantity is static during HODL mode; only changes during basket exposure
- `G.btcQty *= Math.exp(ret)` when in basket and return is valid
- Dollar conversion at end only: `btcQty * btcPrice[end]`
- This is mathematically equivalent to "BTC held, alt returns layered on top"
- Decision date: 2026-07-18, corrected from earlier model that incorrectly compounded BTC returns during HODL

### Chart Rendering
- Three independent data series computed each step:
  - `btcSeries`: BTC % from window start (badger baseline)
  - `altSeries`: Pure altcoin basket % (always computed regardless of position)
  - `youSeries`: Player's actual portfolio % (tracks position switches)
- Y-axis auto-scales to fit all three series + future BTC projection
- Future BTC shown as red dashed line beyond current day
- Position background shading: 8% opacity green (basket) / red (BTC)
- Removed yellow BTC bands (v1) — visually conflicted with yellow YOU line
- Decision date: 2026-07-18

### Permutation Test (Banana Test)
- Precomputed `basket_returns.bin` enables O(1) daily return lookup
- Each permutation: shuffle YOLO block lengths, random gap distribution, simulate via array lookups
- 1,000 permutations in ~11ms (down from 16,000ms naive)
- Runs client-side only
- Not yet implemented in production build
- Decision date: 2026-07-17

### Countdown
- 3-second countdown before simulation
- Default position: YOLO (in basket, FOMO state)
- Player can toggle freely during countdown — no trades counted
- Overlay text: "The next block confirms in..." with countdown number below
- At 0, overlay hidden, simulation begins from current position
- Decision date: 2026-07-18

## Verdict System Implementation

### Thresholds
- DEGEN: `rel > 0.02` (beat badger by >2%)
- LUCKY APE: `rel > -0.02` (within 2% either direction)
- HONEY BADGER WINS: `rel < -0.02` (lost by >2%)
- HODLER: 0 trades AND 0 basket days (pure HODL)
- These thresholds are implementation constants, not design specs

### Unwinnable Windows
- ~7.5% of all 365-day windows: basket never outperforms BTC
- In these windows, `rel > 0.02` is impossible → DEGEN never awarded
- Matching badger (rel ≈ 0) stamps HODLER
- If player trades, they lose → HONEY BADGER WINS
- Banana test never runs in unwinnable windows (beat-badger check fails first)
- No special-case branch visible in source — data enforces the invariant
- Decision date: 2026-07-18

### Unloseable Windows
- ~1.5% of windows: basket always outperforms BTC
- Even random switching wins → many LUCKY APE stamps
- Banana test correctly identifies these as non-skill wins

## Data Handling

### BTC/USD Gap
- BTC pair data starts 2017-07-14; BTCUSDT starts 2017-08-17
- 34-day gap filled from GitHub historical CSV (adjusted −1.38% for USDT/USD slippage)
- First playable game start: 2017-08-17 (need 30+ days of BTC pair history for basket vol)

### USDT Pair Precision
- Micro-cap coins (PEPE, FLOKI, BONK) had zero BTC values due to 8-decimal precision loss
- Fixed by storing BTC price as `c_usd / btcPrice` with 16-decimal precision
- Decision date: 2026-07-17

### Season Tags
- 16 seasons defined inline, covering 2017-2026 with zero gaps
- Every possible 365-day window overlaps with at least 1 season
- Client-side lookup in finishGame() — no server dependency
- Decision date: 2026-07-18

### Price Tiers
- 14 snarky tiers from <$40 to $500K+
- Client-side lookup — no server dependency for prototype
- Will move server-side in production (/api/run response)
- Decision date: 2026-07-17

## UI Implementation

### Font Stack
- SF Mono (system, plain zero) as primary
- All price data in monospace for tabular alignment
- UI labels in system sans-serif (Inter on web)
- Decision date: 2026-07-18, confirmed via pixel analysis of cryptowat.ch screenshots

### Color System
- Sampled from cryptowatch-big.png via vision model
- 3-line chart: green (#00BC00) ALTS, red (#C10706) BTC, yellow (#FCFF00) YOU
- Position strip: yellow for basket, red opacity for BTC
- Speed buttons: brand purple (#3C425B)
- Summary modal: 24px border-radius (DeFi wallet style), #0A0A0C card, #111114 inner boxes
- Decision date: 2026-07-17 (colors), 2026-07-18 (3-line chart)

### Interactive Controls
- Space: toggle HODL ↔ YOLO
- P: pause/resume
- Speed: 0.5×/1×/2×/4× (default 1× = 8 DPS)
- Q key handler removed — summary only shows on game finish
- Decision date: 2026-07-18

### Summary Modal
- 9:16 portrait card, 390px wide, 24px border-radius
- Verdict stamp, season tags, 3 stat boxes, outcome comparison, price tier
- "How ya gonna spend it?" section above tier text
- COPY LINK copies `?s=N` URL, PLAY AGAIN restarts, BACK TO LOBBY resets
- Decision date: 2026-07-18

## Future Work (Not Yet Implemented)

- [ ] Banana test in production build
- [ ] Server-side API (/api/run, /api/ledger, /api/daily-rank)
- [ ] Lobby/landing page
- [ ] Share card PNG generation
- [ ] Notable events in summary (server-side)
- [ ] Daily mode (same window for all players)
- [ ] Sound effects

## Sound Effects (Proposed)

Programmatic Web Audio API tones, no external files. All ~100 bytes each.

| Event | Sound | Implementation |
|-------|-------|---------------|
| Countdown tick (3, 2, 1) | Short blip, ascending pitch | Square wave, 80ms, 440→660→880Hz |
| Market open (0) | Block confirmation chime | Two-tone ding: 880Hz 60ms + 1320Hz 80ms |
| Toggle → YOLO (buy basket) | Coin/ka-ching, upbeat | Quick ascending arp: 523, 659, 784Hz, 50ms each |
| Toggle → HODL (sell to BTC) | Vault close, heavy | Low thud: 95Hz sine 120ms + 52Hz sine 200ms |
| DEGEN verdict | Cheap slot jackpot | Rapid arp up: 523,659,784,1047,1318Hz, 40ms each, tinny |
| LUCKY APE verdict | Casino "ding ding ding" | Same as DEGEN but slower, trailing off |
| HONEY BADGER WINS | Single deep drum | 60Hz sine 300ms, slow decay. One beat. No celebration. |
| HODLER verdict | Zen bell | 528Hz sine 600ms, slow attack, slow decay. Peaceful. |

Mute toggle saved to localStorage (`ph_snd`). Default: muted on first visit,
unmuted on subsequent visits if previously enabled.

Ape sounds: quick, bright, slightly desperate. Badger sounds: slow, deep, indifferent.

## Challenge Feature

- URL parameter `?t=N` encodes a challenge window (start day index)
- Lobby shows "You've been challenged!" banner when `?t` is present
- Clicking PLAY in challenge mode uses the challenged start day
- Summary has "CHALLENGE A FRIEND" button (yellow, full-width) that copies `?t=N` link
- Separate from the old `?s=N` param (kept for backward compatibility)
- Decision date: 2026-07-19
