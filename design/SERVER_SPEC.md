# defihodler — Server Spec

## Architecture

Single Go binary. Append-only JSON-lines file for persistence. In-memory index
(Go map) for reads. In-memory token-bucket rate limiter for writes. No external
dependencies beyond Go stdlib + `golang.org/x/time/rate`.

```
haproxy (TLS) → defihodler-server (:8080)
                   ├── data/db.jsonl     (append-only log)
                   ├── in-memory index   (map[string]Entry)
                   └── in-memory rate limiter
```

## Storage Format

File: `data/db.jsonl` — one JSON object per line, appended.

```jsonl
{"key":"ledger","value":{"games":70108,"badger_wins":48631,"degen_wins":7620,"lucky_wins":13857,"donated":73819812.84}}
{"key":"run:uuid-123","value":{"verdict":"degen","trades":8,"rel":0.15,"s":1234,"inPct":0.42,"pct":92,"don":0,"date":"2026-07-19T14:32:01Z"}}
```

### File Operations

- **Write**: append JSON line + `\n`, then `f.Sync()` (fsync). No buffering.
- **Read (startup)**: scan file line by line, build `map[string]json.RawMessage` in memory.
  Last write per key wins.
- **Compaction**: write new file with only latest value per key, atomically rename.
  Triggered manually via `SIGUSR1` or `POST /admin/compact`.
- **Key pattern**: `ledger` for global stats, `run:<uuid>` for individual game results.

### Resilience

- File is append-only: crashes never corrupt existing data.
- `f.Sync()` after every write ensures durability.
- On startup, replay log to rebuild index. Tolerates partial last line (truncate and continue).

## API Endpoints

### `GET /api/ledger`
Returns global stats from key `ledger`.

```json
{"games":70108,"badger_wins":48631,"degen_wins":7620,"lucky_wins":13857,"donated":73819812.84}
```

### `GET /api/recent`
Returns last N game results. Scans log for `run:*` keys, returns most recent by insertion order.
Default N=10, configurable via `?n=20`.

```json
{"games":[{"verdict":"degen","trades":8,"rel":0.15,"date":"2026-07-19T14:32:01Z"}]}
```

### `GET /api/tape`
Returns current top coin ticker data. In v1, returns static data from embedded fixture.
In production, fetches from Binance API and caches for 60s.

```json
{"coins":[{"sym":"BTC","price":64892.35,"change24h":2.41}]}
```

### `POST /api/run`
Records a single game result. Body: JSON. Stores to key `run:<id>`.
Rate-limited. Returns price tier + events.

Request:
```json
{"id":"uuid","verdict":"degen","trades":8,"rel":0.15,"s":1234,"inPct":0.42,"pct":92,"don":0}
```

Response:
```json
{"tier":"$100,000+","tierText":"Tesla for your BTC?","dailyRank":{"total":342,"worse":287}}
```

### `GET /api/daily-rank?day=N&rel=X`
Returns daily leaderboard for given day number and player's relative performance.
In v1, returns mock data.

## Rate Limiting

- Token bucket per IP, 1 write per second, burst 3.
- Only applies to `POST /api/run` and `POST /admin/compact`.
- In-memory, resets on restart.
- Uses `golang.org/x/time/rate` (stdlib-adjacent).

## Admin Endpoints

### `POST /admin/compact`
Rewrites `data/db.jsonl` with only latest value per key. Rate-limited.
Requires `Authorization: Bearer <token>` header (configurable via env var).

## Spam Prevention

Layered, simple:

1. **Referer check**: rejects POSTs without `Referer: https://<your-domain>/` (configurable).
2. **Origin check**: rejects cross-origin POSTs.
3. **Rate limit**: 1 write/sec/IP.
4. **Authorization header**: for admin endpoints (`/admin/*`).

All checks are optional and configurable via environment variables:
- `ALLOW_ORIGIN`: allowed origin (default: empty = check disabled)
- `ALLOW_REFERER`: required referer prefix (default: empty = check disabled)
- `ADMIN_TOKEN`: bearer token for /admin/* (default: empty = admin disabled)

## Deployment

```bash
# Build
go build -o defihodler-server .

# Run (HTTP only, behind haproxy)
./defihodler-server -addr :8080 -data data/

# Run (HTTPS with Let's Encrypt, no proxy needed)
# Requires ACME_EMAIL and DOMAIN env vars
ACME_EMAIL=admin@example.com DOMAIN=defihodler.com ./defihodler-server -addr :443 -data data/
```

TLS via `golang.org/x/crypto/acme/autocert`. Automatic renewal. Serve HTTP on :80 for
ACME challenges when TLS is enabled.

## File Structure

```
server/
├── main.go           # Server binary (~300 lines)
├── go.mod
└── data/              # Created at runtime
    └── db.jsonl       # Append-only log
```
