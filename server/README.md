# pumprun-server

Single Go binary. Append-only game storage with in-memory stats. No external database.
Rate-limited. Deployed at `/opt/pumprun`, port `8090`, behind haproxy.

## Quick Deploy (Ubuntu/Debian)

```bash
# 1. Create unprivileged user
sudo useradd -r -s /bin/false pumprun

# 2. Create directories
sudo mkdir -p /opt/pumprun /var/lib/pumprun
sudo chown pumprun:pumprun /opt/pumprun /var/lib/pumprun

# 3. Copy binary
sudo cp pumprun-server /opt/pumprun/
sudo chmod +x /opt/pumprun/pumprun-server

# 4. Install startup script
sudo cp pumprun-server.sh /opt/pumprun/
sudo chmod +x /opt/pumprun/pumprun-server.sh

# 5. Set API key
echo 'PUMPRUN_API_KEY="immadegen"' | sudo tee /etc/default/pumprun

# 6. Install and start systemd service
sudo cp pumprun-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pumprun-server
```

## Startup Script

`/opt/pumprun/pumprun-server.sh`:

```bash
#!/bin/bash
cd /opt/pumprun
exec ./pumprun-server \
  -addr :8090 \
  -data /var/lib/pumprun \
  -allow-origin https://pumprun.apps.fyra.sh \
  -api-key "${PUMPRUN_API_KEY:-}"
```

## Systemd Unit

`/etc/systemd/system/pumprun-server.service`:

```ini
[Unit]
Description=pumprun game stats server
After=network.target

[Service]
Type=simple
User=pumprun
Group=pumprun
EnvironmentFile=/etc/default/pumprun
ExecStart=/opt/pumprun/pumprun-server.sh
Restart=always
RestartSec=5
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/pumprun

[Install]
WantedBy=multi-user.target
```

## API key

Set in `/etc/default/pumprun`:

```
PUMPRUN_API_KEY="immadegen"
```

The client sends this as `X-Api-Key` header on POST /pump/run.
Leave `-api-key` empty to disable authentication.

## Shared haproxy Setup

If haproxy already serves other sites on the same hostname, match by URL path
instead. All requests starting with `/pump/` route to pumprun on port 8090.

```
# In your existing frontend section:
frontend https
  bind :443 ssl crt /etc/ssl/

  # ... existing ACLs and backends ...

  # pumprun API — match by path (all /pump/* requests)
  acl is_pumprun path_beg /pump/
  use_backend pumprun_api if is_pumprun

# At the bottom:
backend pumprun_api
  server s1 127.0.0.1:8090
```

The client `<meta name="api-base">` should be set to the same origin as the
web client (e.g., `https://pumprun.apps.fyra.sh`) since the API lives at
`/pump/*` on the same domain.

Validate and reload:

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy
```

## Cert Management (for haproxy)

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d api.gridrun.net
sudo cat /etc/letsencrypt/live/api.gridrun.net/fullchain.pem \
         /etc/letsencrypt/live/api.gridrun.net/privkey.pem \
         > /etc/ssl/api.gridrun.net.pem
# Auto-renewal
sudo certbot renew --deploy-hook "systemctl reload haproxy"
```

## Compaction

Safe while server is live. Cron-friendly:

```bash
# /etc/cron.d/pumprun — daily at 3am
0 3 * * * pumprun /opt/pumprun/pumprun-server -compact -data /var/lib/pumprun
```

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-addr` | `:8080` | Listen address |
| `-data` | `data/` | Data directory |
| `-compact` | `false` | Compact and exit |
| `-allow-origin` | `""` | Allowed origins (comma-separated) |
| `-allow-referer` | `""` | Required Referer prefix |
| `-api-key` | `""` | Required `X-Api-Key` header for POST |

## API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/pump/ledger` | No | Global stats |
| GET | `/pump/recent?n=N` | No | Last N games |
| POST | `/pump/run` | X-Api-Key | Record game result |
| GET | `/pump/daily-rank?day=N&rel=X` | No | Daily leaderboard |

## Data

`/var/lib/pumprun/db.jsonl` — append-only JSON lines, fsynced every write.

| Key | Meaning |
|-----|---------|
| `i` | UUID |
| `s` | Start day index |
| `p` | Banana percentile |
| `r` | Return vs badger |
| `t` | Trade day indices |
| `d` | Signed dollar diff |
