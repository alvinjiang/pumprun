# defihodler — Product Spec v3

A single-page crypto timing game. Player toggles between HODLing Bitcoin and
YOLOing into the 5 most volatile altcoins over a 365-day historical window
(2017–2026). Opponent: the Honey Badger, which bought BTC on day one.

All code reproducible from this spec alone.

---

## 1. Architecture

Single HTML file (~142 KB) with embedded market data. Go server binary for stats.
Canvas charting client-side. No framework, no accounts, no cookies beyond localStorage.

Build: `python3 build.py` — embeds data files, generates JS, verifies syntax, outputs `web/index.html`.

---

## 2. Data Flow

**Lobby**: fetches `GET /api/tape` (scrolling game results) and `GET /api/ledger` (global stats)
concurrently on page load. Degrades gracefully if server unreachable.

**Game**: all data embedded (basket returns, BTC prices, coin list, seasons, events,
price tiers). No server calls during simulation.

**Game End**: summary modal appears. `POST /api/run` fires fire-and-forget with game result.
Server stores 6 fields, returns price tier text. Falls back to client-side tier table if server unreachable.

---

## 3. Game Mechanics

### 3.1 Position Model
```
Start: $10,000 buys X BTC at day-1 BTC/USD price
During HODL: X BTC unchanged
During YOLO: X BTC *= basket_daily_return (BTC-denominated log returns)
End: final_BTC × BTC/USD_end = final dollars
```

BTC quantity is static during HODL periods. Basket returns compound the BTC quantity
during YOLO periods. Dollar conversion only at endpoints.

### 3.2 Basket Construction
- 54 coins from Binance, daily OHLCV 2017-07-14 to 2026-07-15
- 30-day annualized volatility of BTC-denominated log returns
- Top 5 coins by vol, equal-weighted, rebalanced daily
- 14-day persistence filter: must hold top-5 for 14 consecutive days to enter
- First 30 days: fixed basket of BNB, ETH, LTC, NEO (only 4 coins at Binance launch)
- USDT pairs converted to BTC terms via BTCUSDT cross-rate (16-digit precision for micro-caps)
- Basket returns precomputed into `basket_returns.bin` (Float32Array, 12.8 KB)

### 3.3 Window & Timing
- Window: 365 days (1 year in crypto)
- Playable range: 2017-08-17 to 2026-07-15 (2,890 distinct windows)
- BTC/USD gap (2017-07-14 to 2017-08-16): filled from GitHub historical CSV, adjusted -1.38%
- Play speed: 8 DPS at 1× (45s full game), adjustable 0.5×/1×/2×/4×

### 3.4 Countdown
- 3-second countdown before simulation begins
- Overlay text: "The next block confirms in..." above countdown number
- Subtitle: "You start in the token basket. Switch during the countdown to start HODLing Bitcoin."
- Default position: YOLO (in basket, FOMO state)
- Free toggling during countdown — no trades counted, toggles logged as day 0 in trades array
- At 0: overlay hidden, simulation starts from current position

### 3.5 Controls
| Key | Action |
|-----|--------|
| Space | Toggle HODL ↔ YOLO |
| P | Pause / resume |
| Speed buttons | 0.5×, 1×, 2×, 4× (purple #3C425B, default 1×) |

### 3.6 Verdict System

| Condition | Stamp | Color |
|-----------|-------|-------|
| 0 trades, 100% BTC (trades=[0], one countdown toggle to BTC) | HODLER | green |
| Beat badger (ret > 0.02) + top 10% banana (pct >= 90) | DEGEN | green |
| Beat badger (ret > -0.01), not DEGEN | LUCKY APE | amber |
| Unwinnable window, matched badger | HODLER | green |
| Lost to badger (ret < -0.01) | HONEY BADGER WINS | red |

### 3.7 Permutation Test (Banana Test)
Extracts YOLO block lengths from player's position log. 1,000 permutations:
shuffle blocks, random gap distribution, simulate returns. If player beats ≥90% → DEGEN.
Uses precomputed `basket_returns.bin` for O(1) daily lookups. ~11ms execution.
Runs client-side. Not yet implemented in production build (pct hardcoded to 50).

### 3.8 Unwinnable Windows
~7.5% of all 365-day windows: basket never outperforms BTC. Matching badger stamps HODLER.
Banana test never fires (beat-badger check fails first). No special-case branch — data enforces invariant.

---

## 4. Chart Specification

- Canvas-based, 600px height. 3 independent data series:
  - `btcSeries`: BTC % from window start (badger baseline, red #C10706)
  - `altSeries`: Pure altcoin basket % (always computed regardless of position, green #00BC00)
  - `youSeries`: Player's actual portfolio % (tracks position toggles, yellow #FCFF00)
- Y-axis: starts at ±25%, expands when any visible line approaches within 10% of edge.
  Only uses currently rendered data (no future projection in range calc). Never contracts.
- Future BTC: red dashed projection beyond current day (opacity 0.15)
- Position background shading: 8% opacity green (basket) / red (BTC) bands
- Grid: #141416 lines, 6 horizontal × 12 vertical
- Baseline: dashed white at 0%
- Day marker: subtle vertical line at current day
- Auto-scaling Y-axis labels at grid intersections

---

## 5. UI Screens

### 5.1 Lobby
- Ticker tape: full-width, fixed at top of viewport (28px). Scrolling animation (30s CSS).
  Shows recent game results from `GET /api/recent?n=20`: color-coded verdict badge,
  window date range, return vs badger.
- Masthead: "DEGEN TERMINAL" logo, tagline
- Challenge box: shown when `?t=N` URL param present. Yellow "You've been challenged!"
  header. PLAY button uses challenged start day via `setAttribute('onclick', ...)`.
- Play button: "Token Degen" — starts game in YOLO mode. onclick set by init code.
- How It Works: 3-step cards.
- Global Ledger: 5-stat grid (games, badger wins, lucky apes, degens, LOST).
  Stats are all vs the Honey Badger (BTC HODL), not absolute returns.
- Recent Results: scrollable feed, last 10 games, verdict badges, trade counts, vs-badger %.
- Footer: methodology link, data source note. All text +4pt from original mockup.

### 5.2 Game Screen
- Purple 2px accent bar at page top
- Header: "DEGEN TERMINAL" + "No Fees · No Spread · No Mercy" right-aligned
- Duel row (3 columns):
  - Left: You — portfolio value (32px, green/red), total P&L + trades in subtitle
  - Center: VS — delta vs badger (22px, green/red)
  - Right: Honey Badger — portfolio value (28px, text-mid), today's P&L in subtitle
- Position banner: SAFU (green bg) / FOMO (red bg) with description text.
  No blinking cursor.
- Chart: 600px canvas (see §4)
- Position strip: colored blocks for HODL/BASKET periods, grey for future
- Legend: Alts (green), You (yellow), BTC (red)
- Progress bar: DAY X / 365, 6px height, gradient fill (#5a6080→#9a9fc0) on
  dark track (#1a1a20). Width updated via `style.width = (G.i/WIN*100) + '%'`.
- Speed controls: purple buttons, default 1×
- Toggle button: green "HODL · SWITCH TO BITCOIN" in FOMO, red "YOLO · SWITCH TO ALTCOINS" in SAFU
- Countdown overlay (see §3.4)

### 5.3 Summary Modal
- 9:16 portrait card (420px, 24px border-radius). Overlay at 45% opacity.
  Card aligned to chart-top level.
- Top labels: "DEGEN OR HODLER?" + datetime
- Verdict box: stamp (30px, colored), window dates, season tag
- Stat row: TRADES, TIME IN ALTS %, % VS APES
- Outcome box: win/loss text, YOU row (amount + %), HONEY BADGER row,
  "How ya gonna spend it?" + tier text
- Events box: notable events during window (from inline EVENTS array, 30+ entries)
- CHALLENGE A FRIEND button (yellow, full-width): onclick copies `?t=N` link, flashes yellow
- SHARE button: onclick copies base URL (no params), flashes yellow
- PLAY AGAIN + BACK TO LOBBY buttons

---

## 6. Client Data (embedded in HTML)

| Data | Format | Size |
|------|--------|------|
| Basket returns | Float32Array (base64) | 12.8 KB |
| BTC/USD prices | JSON array of `[t, c]` | 120 KB |
| Coin list | JSON object | 2.7 KB |
| Seasons | JS array, 16 entries | inline |
| Events | JS array, 31 entries | inline |
| Price tiers | JS array, 14 entries | inline |

Total HTML: ~142 KB.

---

## 7. API Contract

### 7.1 GET /api/ledger
```json
{"games":70108,"badger_wins":48631,"degen_wins":7620,"lucky_wins":13857,"lost":73819812}
```
`lost` = sum of `abs(diff)` for all games where `diff < 0`.

### 7.2 GET /api/recent?n=N
```json
{"games":[{"id":"uuid","s":1234,"pct":94,"ret":0.22,"trades":[0,5,20],"diff":2450}]}
```
Returns last N games. Default N=10.

### 7.3 POST /api/run
Request (client sends 7 fields, server stores 6):
```json
{"id":"uuid","s":1234,"pct":94,"ret":0.22,"trades":[0,5,20],"diff":2450,"final":14145}
```
Response:
```json
{"tier":"$100,000+","tierText":"Tesla for your BTC?","dailyRank":{"total":342,"worse":287}}
```

### 7.4 GET /api/daily-rank?day=N&rel=X
```json
{"total":342,"worse":287}
```

---

## 8. Server

Go binary, single `main.go`. See `SERVER_SPEC.md` for implementation details.

### 8.1 Storage Format
`data/db.jsonl` — append-only JSON lines, one per game. Fsynced every write.
No ledger entries in the log. Six fields stored per game:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | UUID, client-generated |
| `s` | int | Start day index (identifies 365-day window) |
| `pct` | float64 | Banana test percentile (0–100). Must be stored |
| `ret` | float64 | Return vs badger. Derivable but stored for zero-cost replay |
| `trades` | []int | Trade day indices since s. `[]` = never toggled (stayed YOLO). `[0]` = countdown toggle to BTC. Default start: YOLO |
| `diff` | float64 | Signed dollar difference vs badger |

### 8.2 Ledger Computation
In-memory only, computed at startup by replaying log, updated with each POST:
- `games`: count of `run:*` entries
- `degen_wins`: `ret > 0.02 AND pct >= 90`
- `lucky_wins`: `ret > -0.01 AND NOT degen`
- `badger_wins`: `ret < -0.01`
- `lost`: sum of `abs(diff)` for all games where `diff < 0`

No BTC price data needed server-side. Verdict derived from `ret` + `pct` alone.

### 8.3 Client POST vs Storage
Client sends additional fields (e.g. `final`) for price tier lookup.
Server filters to the 6 essential fields before writing to log.

### 8.4 Compaction
`./defihodler-server -compact` rewrites log with only latest value per key.
Atomic rename. Safe against running instance. Cron-friendly.

### 8.5 Spam Prevention
Rate limit: 1 write/sec/IP (in-memory token bucket, resets on restart).
Optional referer/origin checks via CLI flags. TLS via haproxy or built-in autocert.

---

## 9. Challenge Feature

- URL param `?t=N`: forced start day index. Lobby shows challenge banner.
- PLAY button onclick set via `setAttribute('onclick', 'startGame(N)')`.
- Summary: CHALLENGE A FRIEND button copies `?t=N` link via `navigator.clipboard`.
  Flashes yellow background + "LINK COPIED!" for 1.8s. Fallback: `execCommand('copy')`.
- SHARE button copies base URL (no params). Same flash behavior.
- Legacy `?s=N` param still supported.

---

## 10. Design System

### Colors (cryptowat.ch sampled)
#000000 bg, #0D0D10 panel, #1C1C20 border, #5C5C60 dim, #8A8A8E mid, #C8C8CC bright,
#00BC00 green, #C10706 red, #FCFF00 yellow, #3C425B purple.

### Typography
SF Mono (system, plain zero). Monaco/Menlo/Consolas fallback. Monospace for all data.
No rounded corners on terminal UI. 24px border-radius on summary modal.

---

## 11. Sound Effects

Programmatic Web Audio API. Square waves for ape (quick, bright), sine waves for badger
(slow, deep). Mute toggle in localStorage. See `web/sounds.html` for samples.

---

## 12. Build Pipeline

```bash
python3 build.py
```

1. Reads `design/data/basket_returns.bin`, `btcusdt.json`, `index.json`
2. Embeds as base64/JSON into JS template
3. Writes complete HTML to `web/index.html`
4. Verifies JS syntax via `node --check`

Always regenerate via build script — never hand-edit the JS in `web/index.html`.

### Field Name Map (storage → meaning)

| Key | Meaning |
|-----|---------|
| `i` | UUID, client-generated |
| `s` | Start day index (identifies 365-day window) |
| `p` | Banana test percentile (0–100) |
| `r` | Return vs badger (e.g. 0.22 = +22%) |
| `t` | Array of trade day indices since `s`. `[0]` = countdown toggle to BTC. `[]` = stayed YOLO |
| `d` | Signed dollar difference vs badger |

Example: `{"key":"run:x1","value":{"i":"x1","s":500,"p":94,"r":0.22,"t":[0,5],"d":2450}}`
