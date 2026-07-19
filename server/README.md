# defihodler-server

Single Go binary. Append-only game storage with in-memory stats.
No external database. Rate-limited. Production-ready behind haproxy or standalone with TLS.

## Quick Start

```bash
# Copy binary to server
scp defihodler-server user@host:/opt/defihodler/

# Run (HTTP, for use behind haproxy/nginx)
./defihodler-server -addr :8080 -data /var/lib/defihodler/

# Compact the log (safe to run while server is live, cron-friendly)
./defihodler-server -compact -data /var/lib/defihodler/
```

## Building from Source

```bash
# Requires Go 1.21+
go build -o defihodler-server .
```

No additional dependencies beyond `golang.org/x/time` (fetched automatically by `go mod tidy`).

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-addr` | `:8080` | Listen address |
| `-data` | `data/` | Data directory for `db.jsonl` |
| `-compact` | `false` | Compact the data file and exit (does not start server) |
| `-allow-origin` | `""` | Allowed CORS origin (empty = disable check) |
| `-allow-referer` | `""` | Required Referer prefix (empty = disable check) |

## API Endpoints

### GET /api/ledger
Global stats. Computed in-memory from log replay.

```json
{"games":70108,"badger_wins":48631,"degen_wins":7620,"lucky_wins":13857,"lost":73819812}
```

### GET /api/recent?n=20
Last N game results. Default N=10.

```json
{"games":[{"i":"uuid","s":1234,"p":94,"r":0.22,"t":[0,5,20],"d":2450}]}
```

### POST /api/run
Record a game result. Rate-limited: 1 write/sec/IP (burst 3).

Request:
```json
{"i":"uuid","s":1234,"p":94,"r":0.22,"t":[0,5,20],"d":2450,"final":14145}
```

Response:
```json
{"tier":"$100,000+","tierText":"Tesla for your BTC?","dailyRank":{"total":0,"worse":0}}
```

### GET /api/daily-rank?day=N&rel=X
Daily leaderboard. v1 returns mock data.

## Data Storage

`data/db.jsonl` — append-only JSON lines, one per game. Fsynced after every write.
No ledger/aggregate entries in the log. Ledger computed in-memory at startup.

### Field Reference

| Key | Meaning |
|-----|---------|
| `i` | UUID, client-generated |
| `s` | Start day index (identifies 365-day window) |
| `p` | Banana test percentile (0–100) |
| `r` | Return vs badger (e.g. 0.22 = +22%) |
| `t` | Array of trade day indices since `s` |
| `d` | Signed dollar difference vs badger |

### Compaction

```bash
# Compact the log — removes old key versions, reduces file size
./defihodler-server -compact -data /var/lib/defihodler/

# Cron example: compact daily at 3am
0 3 * * * /opt/defihodler/defihodler-server -compact -data /var/lib/defihodler/
```

Safe to run while server is live. Uses atomic rename — the running server keeps its
file descriptor; new starts pick up the compacted file.

## Deployment

### Option A: Behind haproxy (recommended)

```
# haproxy.cfg
frontend https
  bind :443 ssl crt /etc/ssl/defihodler.pem
  use_backend defihodler if { hdr(host) -i defihodler.com }

backend defihodler
  server s1 127.0.0.1:8080

# Server runs on localhost only
./defihodler-server -addr 127.0.0.1:8080 -data /var/lib/defihodler/
```

### Option B: Standalone with Let's Encrypt

Add `golang.org/x/crypto/acme/autocert` to `main.go`:

```go
import "golang.org/x/crypto/acme/autocert"

m := &autocert.Manager{
    Cache:      autocert.DirCache("/var/lib/defihodler/certs"),
    Prompt:     autocert.AcceptTOS,
    HostPolicy: autocert.HostWhitelist("defihodler.com"),
}
server := &http.Server{
    Addr:      ":443",
    TLSConfig: m.TLSConfig(),
    Handler:   handler,
}
// Also listen on :80 for ACME challenges
go http.ListenAndServe(":80", m.HTTPHandler(nil))
log.Fatal(server.ListenAndServeTLS("", ""))
```

### Option C: Static cert file

```go
log.Fatal(http.ListenAndServeTLS(":443", "/etc/ssl/cert.pem", "/etc/ssl/key.pem", handler))
```

### Cert Renewal

- **haproxy**: use certbot with `--deploy-hook "systemctl reload haproxy"`
- **autocert**: automatic renewal, no cron needed
- **static cert**: certbot cron: `0 0 * * * certbot renew --quiet --deploy-hook "systemctl restart defihodler"`

## Spam Prevention

All checks are optional and disabled by default:

```bash
# Enable origin check (only accept POSTs from your domain)
./defihodler-server -allow-origin https://defihodler.com

# Enable referer check
./defihodler-server -allow-referer https://defihodler.com/
```

Rate limiting (1 write/sec/IP, burst 3) is always active. In-memory only, resets on restart.

## Systemd Unit

```
# /etc/systemd/system/defihodler.service
[Unit]
Description=defihodler game server
After=network.target

[Service]
Type=simple
User=defihodler
ExecStart=/opt/defihodler/defihodler-server -addr 127.0.0.1:8080 -data /var/lib/defihodler/
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo useradd -r -s /bin/false defihodler
sudo mkdir -p /var/lib/defihodler
sudo chown defihodler:defihodler /var/lib/defihodler
sudo systemctl enable --now defihodler
```

## File Size

Binary: ~7.7 MB (static, no runtime dependencies). Data file grows ~150 bytes per game.
At 100K games: ~15 MB. Compact periodically to reclaim space from duplicate keys.
