# pumprun / DEGEN|TERMINAL — Product Spec v4

A single-page crypto timing game. Player toggles between HODLing Bitcoin and
YOLOing into the 5 most volatile altcoins over a 365-day historical window
(2017–2026). Opponent: the Honey Badger, which bought BTC on day one.

All code reproducible from this spec alone.

---

## 1. Architecture

Single HTML file (~147 KB) with embedded market data. Go server binary (`pumprun-server`)
for stats. Canvas charting client-side. No framework, no accounts, no cookies.

Build: `python3 build.py` — embeds data files, generates JS, verifies syntax, outputs `web/index.html`.
Deploy: gRPC streaming push to `server.fyra.sh:50052` via `fyra.v1.DeployService/Push`.

---

## 2. Data Flow

**Lobby**: fetches `GET /pump/ledger` (global stats) and `GET /pump/recent?n=20` (ticker tape + recent results table)
concurrently on page load. Degrades gracefully if server unreachable.

**Game**: all data embedded (basket returns, BTC prices, coin list, seasons, events,
price tiers). No server calls during simulation.

**Game End**: summary modal appears. Banana test runs client-side (1,000 permutations, chunked 50/tick).
Results populate `#sps`. `POST /pump/run` fires fire-and-forget with game result.
Server stores 6 fields (short names), returns price tier text.

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
- Play speed: 8 DPS at 1× (~45s full game), adjustable 0.5×/1×/2×/4×

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

| Condition | Stamp | Color | Class |
|-----------|-------|-------|-------|
| 0 trades, 100% BTC | HODLER | green | `hodler` |
| ret > 0.02 AND pct >= 90 | DEGEN | green | `degen` |
| ret > -0.01, not DEGEN | LUCKY APE | amber | `lucky` |
| Unwinnable window, matched badger | HODLER | green | `hodler` |
| Lost to badger (ret < -0.01) | HONEY BADGER WINS | red | `badger` |

### 3.7 Permutation Test (Banana Test)
Extracts YOLO block lengths from player's position log. 1,000 permutations:
shuffle blocks, random gap distribution, simulate returns. If player beats ≥90% → DEGEN.
Uses precomputed `basket_returns.bin` for O(1) daily lookups. Runs asynchronously
in 50-permutation chunks via setTimeout to avoid blocking. Implemented and working.

### 3.8 Unwinnable Windows
~7.5% of all 365-day windows: basket never outperforms BTC. Matching badger stamps HODLER.
Banana test never fires (beat-badger check fails first). No special-case branch — data enforces invariant.

---

## 4. Chart Specification

- Canvas-based, 600px height @ 2x DPR. 3 independent data series:
  - `btcSeries`: BTC % from window start (badger baseline, red #C10706)
  - `altSeries`: Pure altcoin basket % (always computed regardless of position, green #00BC00)
  - `youSeries`: Player's actual portfolio % (tracks position toggles, yellow #FCFF00)
- Y-axis: starts at ±25%, expands when any visible line approaches within 10% of edge.
  Only uses currently rendered data (no future projection in range calc). Never contracts.
- Position background shading: 8% opacity green (basket) / red (BTC) bands
- Grid: #111116 lines, 6 horizontal
- Future grey area: beyond current day

---

## 5. UI Screens

### 5.1 Lobby (v2-path-a-lobby design)
- **Gradient accent bar**: 2px, #1a1a2e → #3c425b → #5a6080 → #3c425b → #1a1a2e
- **Ticker tape**: below accent bar, 30s CSS scroll animation. Shows recent game results:
  color-coded verdict badge (DEGEN/BADGER WINS/LUCKY APE/HODLER), window range, return vs badger.
  HODLER verdicts show "matched badger" in grey instead of percentage.
- **Hero section**: centered, border-bottom separator
  - Chips: ⚡ Token Degen (green) VS 🦡 Bitcoin HODLer (red)
  - Title: "DEGENTERMINAL" (38px, green D)
  - Tagline: "No Fees · No Spread · No Mercy · 2017–2026" (11px, dim, uppercase)
  - Copy: $10,000. 365 days. One button. HODL Bitcoin or YOLO the top-5 most volatile alts.
    The honey badger bought BTC on day one and never looked back. Beat it.
  - CTA row: ▶ PLAY NOW (green, 280×46px) + ⊞ DAILY CHALLENGE (bordered, 280×46px)
- **Challenge mode** (`?t=N`): PLAY NOW button becomes "YOU'VE BEEN CHALLENGED!" (yellow, 13px, same width). onclick set to `startGame(N)`.
- **Global Statistics**: 4-column grid (#0d0d10 panels, 1px #1c1c20 gaps)
  - Games Played (white), Badger Wins (red), Median vs Badger (yellow), Best Human Ever (green)
  - Median and best computed from last 100 games. Games/Badger from `/pump/ledger`.
- **Recent Results**: table with VERDICT, WINDOW, VS BADGER, TRADES, SEASON columns.
  Verdict badges: color-coded (green=DEGEN, red=BADGER WINS, yellow=LUCKY APE, grey=HODLER).
  Returns always vs badger — no separate absolute return column.
- **The Lore**: 2-column cards
  - Token Degen (You): "Wins 27.9% of the time" (red, static). Basket text: "DOGE, PEPE, ENJ. The coins you forgot you held."
  - The Bitcoin HODLer: "Wins 72.1% of the time" (green, static). "Bought BTC on day one. Never looked back. Not interested in your thesis, doesn't care about use cases, and a depeg doesn't matter when it values everything in sats."
- **Footer**: "Data: Binance 2017–2026 · 54 coins · Daily resolution" | "The ape trades. The badger waits. Guess who wins."

### 5.2 Game Screen
- Header: "DEGENTERMINAL" + "No Fees · No Spread · No Mercy"
- Duel row (3 columns):
  - Left: You — portfolio value (32px, green/red), total P&L + trades in subtitle
  - Center: VS — delta vs badger (22px, green/red)
  - Right: Honey Badger — portfolio value (28px, text-mid), today's P&L in subtitle
- Position banner: SAFU (green bg) / FOMO (red bg) with description text
- Chart: 600px canvas (see §4)
- Position strip: colored blocks for HODL/BASKET periods, grey for future
- Legend: Alts (green), You (yellow), BTC (red)
- Progress bar: DAY X / 365, 6px height, gradient fill (#5a6080→#9a9fc0) on dark track (#1a1a20)
- Speed controls: purple buttons, default 1×
- Toggle button: green "HODL · SWITCH TO BITCOIN" in FOMO, red "YOLO · SWITCH TO ALTCOINS" in SAFU
- Countdown overlay (see §3.4)

### 5.3 Summary Modal
- Full-viewport fixed overlay, 45% opacity black background, z-index 100
- 9:16 portrait card (420px, 24px border-radius, #0a0a0c background, 1px #1c1c20 border)
- Card aligned to chart-top level (padding-top: 160px)
- **Top row**: "DEGEN OR HODLER?" + datetime (UTC)
- **Verdict box**: stamp (30px, colored by verdict class), window dates, season tag
- **Stat row**: TRADES, TIME IN ALTS %, % VS APES (banana percentile)
- **Outcome box**: win/loss text, YOU row (amount + %), HONEY BADGER row,
  "How ya gonna spend it?" + tier text from TIERS array
- **Events box**: notable events during window (from inline EVENTS array, 30+ entries)
- **Buttons**: CHALLENGE A FRIEND (yellow, copies `?t=N` link), SHARE (copies base URL),
  PLAY AGAIN + BACK TO LOBBY

---

## 6. Client Data (embedded in HTML)

| Data | Format | Size |
|------|--------|------|
| Basket returns | Float32Array (base64) | ~13 KB |
| BTC/USD prices | JSON array of `[t, c]` | ~120 KB |
| Coin list | JSON object | ~3 KB |
| Seasons | JS array, 16 entries | inline |
| Events | JS array, 31 entries | inline |
| Price tiers | JS array, 14 entries | inline |

Total HTML: ~147 KB.

---

## 7. API Contract

All endpoints under `/pump/` path prefix. Client sets `<meta name="api-base">` to
`https://api.gridrun.net`. API key sent as `X-Api-Key` header on POST.

### 7.1 GET /pump/ledger
```json
{"games": 72140, "badger_wins": 48631, "degen_wins": 7620, "lucky_wins": 13857, "lost": 73819812}
```
`lost` = sum of `abs(d)` for all games where `d < 0`.

### 7.2 GET /pump/recent?n=N
```json
{"games": [{"i": "uuid", "s": 1234, "p": 94, "r": 0.22, "t": [0, 5, 20], "d": 2450, "final": 14145}]}
```
Returns last N games, default N=10. Fields use short names (see §8.1).

### 7.3 POST /pump/run
Request (client sends 7 fields, server stores 6):
```json
{"i": "uuid", "s": 1234, "p": 94, "r": 0.22, "t": [0, 5, 20], "d": 2450, "final": 14145}
```
Response:
```json
{"tierText": "Tesla for your BTC?"}
```
Tier text returned if server has TIERS matching. Client falls back to embedded TIERS array.

### 7.4 GET /pump/daily-rank?day=N&rel=X
```json
{"total": 342, "worse": 287}
```
Implemented in server.

---

## 8. Server

Go binary, single `main.go` (~400 lines). Append-only JSON-lines storage.
Deployed at `/opt/pumprun`, port 8090, behind haproxy with `path_beg /pump/` ACL.

### 8.1 Storage Format
`data/db.jsonl` — append-only JSON lines, one per game. Fsynced every write.
Short field names to save disk space:

| Key | Type | Description |
|-----|------|-------------|
| `i` | string | UUID, client-generated |
| `s` | int | Start day index (identifies 365-day window) |
| `p` | float64 | Banana test percentile (0–100) |
| `r` | float64 | Return vs badger |
| `t` | []int | Trade day indices since `s`. `[0]` = countdown toggle to BTC. `[]` = stayed YOLO |
| `d` | float64 | Signed dollar difference vs badger |

Example: `{"key":"run:uuid","value":{"i":"uuid","s":500,"p":94,"r":0.22,"t":[0,5],"d":2450}}`

### 8.2 Ledger Computation
In-memory only, computed at startup by replaying log, updated with each POST:
- `games`: count of `run:*` entries
- `degen_wins`: `r > 0.02 AND p >= 90`
- `lucky_wins`: `r > -0.01 AND NOT degen`
- `badger_wins`: `r < -0.01`
- `lost`: sum of `abs(d)` for all games where `d < 0`

No BTC price data needed server-side. Verdict derived from `r` + `p` alone.

### 8.3 Client POST vs Storage
Client sends additional field (`final`) for price tier lookup. Server filters to the
6 essential fields before writing to log.

### 8.4 Compaction
`./pumprun-server -compact` rewrites log with only latest value per key.
Atomic rename. Safe against running instance. Cron-friendly.

### 8.5 Spam Prevention
Rate limit: 1 write/sec/IP (in-memory token bucket, `golang.org/x/time/rate`).
CORS via `-allow-origin` flag (comma-separated origins). API key via `-api-key` flag.

### 8.6 CLI Flags
| Flag | Default | Description |
|------|---------|-------------|
| `-addr` | `:8080` | Listen address |
| `-data` | `data/` | Data directory |
| `-compact` | `false` | Compact and exit |
| `-allow-origin` | `""` | Allowed origins (comma-separated) |
| `-api-key` | `""` | Required `X-Api-Key` header for POST |

Production flags: `-addr :8090 -data /var/lib/pumprun -allow-origin "https://pumprun.apps.fyra.sh,https://pumprun.fyra.sh" -api-key immadegen`

---

## 9. Challenge Feature

- URL param `?t=N`: forced start day index. Lobby shows yellow "YOU'VE BEEN CHALLENGED!" button
  (13px, 280×46px) instead of "▶ PLAY NOW". onclick set via `setAttribute('onclick', 'startGame(N)')`.
- Summary: CHALLENGE A FRIEND button copies `?t=N` link via `navigator.clipboard`.
  Flashes yellow background + "LINK COPIED!" for 1.8s. Fallback: `execCommand('copy')`.
- SHARE button copies base URL (no params). Same flash behavior.
- Legacy `?s=N` param still supported.

---

## 10. Design System

### Colors (cryptowat.ch sampled)
| Name | Hex | Usage |
|------|-----|-------|
| bg | #000000 | Page background |
| panel | #0D0D10 | Card backgrounds |
| panel2 | #111114 | Inner card surfaces |
| border | #1C1C20 | Borders, separators |
| dim | #5C5C60 | Muted text |
| mid | #8A8A8E | Secondary text |
| bright | #C8C8CC | Primary text |
| green | #00BC00 | Wins, DEGEN, basket, buy |
| red | #C10706 | Losses, BADGER, FOMO |
| yellow | #FCFF00 | Challenge, LUCKY APE |
| purple | #3C425B | Speed buttons, accent |

### Typography
SF Mono (system, plain zero). Monaco/Menlo/Consolas fallback. Monospace for all data.
Body: 15px. No rounded corners on terminal UI. 24px border-radius on summary modal.

### Favicon
Inline SVG: green candle on black rounded rect (16×16).

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

### Deploy
```bash
# Build
python3 build.py

# Deploy via gRPC (see NOTES.md for full auth flow)
cd web && tar --exclude='.deploy.yaml' -czf deploy.tar.gz .
# Stream to fyra.v1.DeployService/Push at server.fyra.sh:50052
```

---

## 13. Mockup Server

Design mockups served at `http://10.44.2.26:8901/` for review before implementation.
Run: `python3 -m http.server 8901 --directory design/mockup --bind 10.44.2.26`
