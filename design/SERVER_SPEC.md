# pumprun — Server Spec

## Architecture

Single Go binary (`pumprun-server`). Append-only JSON-lines file for persistence.
In-memory index (Go map) for reads. In-memory token-bucket rate limiter for writes.
No external dependencies beyond Go stdlib + `golang.org/x/time/rate`.

```
haproxy (TLS) → pumprun-server (:8090)
                   ├── /var/lib/pumprun/db.jsonl     (append-only log)
                   ├── in-memory index               (map[string]json.RawMessage)
                   └── in-memory rate limiter
```

## Storage Format

File: `db.jsonl` — one JSON object per line, appended. Short field names.

```jsonl
{"key":"run:uuid-123","value":{"i":"uuid-123","s":1005,"p":50,"r":1.9,"t":[0,17,125],"d":175923}}
```

### File Operations

- **Write**: append JSON line + `\n`, then `f.Sync()` (fsync). No buffering.
- **Read (startup)**: scan file line by line, build `map[string]json.RawMessage` in memory.
  Last write per key wins.
- **Compaction**: `./pumprun-server -compact` writes new file with only latest value per key,
  atomically renames. Safe against running instance.

### Resilience

- File is append-only: crashes never corrupt existing data.
- `f.Sync()` after every write ensures durability.
- On startup, replay log to rebuild index. Tolerates partial last line (truncate and continue).

## API Endpoints

All under `/pump/` path prefix, served behind haproxy with `path_beg /pump/` ACL.

### `GET /pump/ledger`
Returns global stats from in-memory ledger.

```json
{"games": 72140, "badger_wins": 48631, "degen_wins": 7620, "lucky_wins": 13857, "lost": 73819812}
```

### `GET /pump/recent?n=N`
Returns last N game results. Scans index for `run:*` keys, returns most recent by insertion order.
Default N=10.

```json
{"games": [{"i": "uuid", "s": 1234, "p": 94, "r": 0.22, "t": [0, 5, 20], "d": 2450}]}
```

### `POST /pump/run`
Records a single game result. Body: JSON. Stores to key `run:<i>`.
Rate-limited (1/sec/IP). Requires `X-Api-Key` header matching `-api-key` flag.

Request (client sends 7 fields, server stores 6):
```json
{"i": "uuid", "s": 1234, "p": 94, "r": 0.22, "t": [0, 5, 20], "d": 2450, "final": 14145}
```

Response:
```json
{"tierText": "Tesla for your BTC?"}
```

Tier text from price tier lookup using `final` field. Falls back to client-side TIERS
array if server doesn't match.

### `GET /pump/daily-rank?day=N&rel=X`
Returns daily leaderboard for given start day and player's return vs badger.

```json
{"total": 342, "worse": 287}
```

## Ledger Computation

In-memory only (`Ledger` struct), computed at startup by replaying log, updated with each POST:

| Field | Derivation |
|-------|-----------|
| `games` | count of `run:*` keys |
| `degen_wins` | `r > 0.02 AND p >= 90` |
| `lucky_wins` | `r > -0.01 AND NOT degen` |
| `badger_wins` | `r < -0.01` |
| `lost` | sum of `abs(d)` for all games where `d < 0` |

No BTC price data needed server-side. Verdict derived from `r` + `p` alone.

## Rate Limiting

- Token bucket per IP, 1 write per second, burst 3.
- Only applies to `POST /pump/run`.
- In-memory, resets on restart.
- Uses `golang.org/x/time/rate`.

## Spam Prevention

Layered, simple:

1. **CORS**: `-allow-origin` flag (comma-separated origins). Rejects cross-origin POSTs.
2. **Rate limit**: 1 write/sec/IP.
3. **API key**: `-api-key` flag — POSTs require matching `X-Api-Key` header.

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-addr` | `:8080` | Listen address |
| `-data` | `data/` | Data directory |
| `-compact` | `false` | Compact and exit |
| `-allow-origin` | `""` | Allowed origins (comma-separated) |
| `-api-key` | `""` | Required `X-Api-Key` header for POST |

Production: `-addr :8090 -data /var/lib/pumprun -allow-origin "https://pumprun.apps.fyra.sh,https://pumprun.fyra.sh" -api-key immadegen`

## Deployment

```bash
# Build
cd server && go build -o pumprun-server .

# Run (HTTP only, behind haproxy)
./pumprun-server -addr :8090 -data /var/lib/pumprun -allow-origin "https://pumprun.apps.fyra.sh" -api-key immadegen

# Compaction (cron-friendly)
./pumprun-server -compact -data /var/lib/pumprun
```

See `server/README.md` for full systemd unit and haproxy configuration.

## File Structure

```
server/
├── main.go              # Server binary (~400 lines)
├── go.mod
├── go.sum
└── data/                 # Created at runtime
    └── db.jsonl          # Append-only log
```
