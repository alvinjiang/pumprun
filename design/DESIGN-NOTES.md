# defihodler — Design Decisions Log

## Core Concept
HODL (BTC) vs YOLO (volatile altcoin basket). Toggle between strategies over a 2-year window.

## Game Mechanics
- **Window:** 730 days (~2 years in crypto, 24 "months")
- **Start:** $1,000 worth of BTC (at opening price of the window)
- **Positions:** Binary — always either HODL (BTC) or YOLO (basket)
- **No neutral/cash position.** No friction costs.
- **Chart:** Tracks portfolio value in BTC terms (candlestick or line)
- **Valuation:** Dollar value calculated only at start and end; intermediate values in BTC
- **Opponent:** "The HODLer" or BTC buy-and-hold baseline
- **Character/Tone:** Self-aware degen humor (Option A)

## Basket Construction
- **Top 5 by pure volatility** (30d rolling annualized stddev of daily log returns)
- **2-week persistence filter:** must remain in top-5 for 14 consecutive days to enter basket
- **Equal-weighted, rebalanced daily**
- **Excludes stablecoins**
- **Data universe:** 54 Binance-listed coins (BTC pairs + USDT pairs for memes)
- **No pump.fun/DEX data for v1** — Binance degen is degen enough

## Data Period
- **Start:** 2017-08-17 (Binance BTCUSDT launch)
- **End:** 2026-07-15
- **~3,255 trading days**, daily resolution
- **All timestamps at 00:00 UTC** (Binance daily candles)
- **Data stored in:** `~/aicode/defihodler/data/` (~8MB, 54 coins)

## Verdict System (Proposed)
| Condition | Verdict |
|-----------|---------|
| 0 trades, stayed in BTC | "The HODLer" (enlightened) |
| Beat HODL + top 10% monkey | "Skilled" |
| Beat HODL but not top 10% monkey | "Lucky" |
| Lost to HODL by <10% | "Close" |
| Lost to HODL by >10% | "Rekt" |

## Monkey Test
- **1,000 permutations** of the player's exact trade schedule (same trade count, same out-of-market block sizes) with random placement
- **90th percentile threshold** for "skilled" stamp
- Baseline: random monkeys lose to HODL **79.6% of the time** (median −59.5%)

## Server Architecture
- Static HTML (CDN-hosted), single file ~300KB
- Separate API binary behind haproxy
- Append-only text-based DB or embedded KV
- 3 endpoints: POST /api/run, GET /api/ledger, GET /api/daily-rank
- API returns snarky purchase comparisons as part of /api/run response

## End-of-Game Features
- Snarky "what you could have bought" comparisons (crypto-themed, server-side)
- Crypto events/season tags relevant to the player's window
- Share card generation (canvas-based PNG)
- Challenge links (URL param encoding window start)

## Open Questions
- Ape theme specifics (name, visual identity, copy tone)
- Exact UI layout and screens
