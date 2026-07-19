# pumprun-server

Single Go binary. Append-only game storage with in-memory stats. No external database.
Rate-limited. Production-ready behind haproxy or standalone.

## Quick Deploy (Ubuntu/Debian)

```bash
# 1. Create unprivileged user
sudo useradd -r -s /bin/false pumprun

# 2. Create directories
sudo mkdir -p /opt/pumprun /var/lib/pumprun
sudo chown pumprun:pumprun /opt/pumprun /var/lib/pumprun

# 3. Copy binary
sudo cp defihodler-server /opt/pumprun/pumprun-server
sudo chmod +x /opt/pumprun/pumprun-server

# 4. Install startup script
sudo cp pumprun-server.sh /opt/pumprun/
sudo chmod +x /opt/pumprun/pumprun-server.sh

# 5. Install and start systemd service
sudo cp pumprun-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pumprun-server
```

## Startup Script

`/opt/pumprun/pumprun-server.sh`:

```bash
#!/bin/bash
# pumprun game stats server
# Deployed at /opt/pumprun, data at /var/lib/pumprun

cd /opt/pumprun
exec ./pumprun-server \
  -addr :8090 \
  -data /var/lib/pumprun \
  -allow-origin https://pumprun.com \
  -api-key "${PUMPRUN_API_KEY:-}"
```

Set the API key in `/etc/default/pumprun`:

```bash
# /etc/default/pumprun
PUMPRUN_API_KEY="your-secret-key-here"
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

## Architecture

```
CDN (pumprun.com)                Server (api.pumprun.com:8090)
─────────────────                ────────────────────────────
index.html                       pumprun-server
<meta name="api-base"            -addr :8090
  content="https://api.pumprun.com">  -data /var/lib/pumprun
                                       -api-key "secret"
POST /api/run  ────────────────→  X-Api-Key: secret
                 HTTPS (haproxy)
```

The client (CDN-hosted HTML) points to the server via the `<meta name="api-base">` tag.
The server runs on port 8090 behind haproxy which handles TLS and forwards to localhost.

## haproxy Config

```
frontend api-https
  bind :443 ssl crt /etc/ssl/api.pumprun.com.pem
  use_backend pumprun-api if { hdr(host) -i api.pumprun.com }

backend pumprun-api
  server s1 127.0.0.1:8090
```

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-addr` | `:8080` | Listen address. Use `:8090` for production |
| `-data` | `data/` | Data directory for `db.jsonl` |
| `-compact` | `false` | Compact the data file and exit (does not start server) |
| `-allow-origin` | `""` | Allowed CORS origin for POST requests |
| `-allow-referer` | `""` | Required Referer prefix for POST requests |
| `-api-key` | `""` | Required `X-Api-Key` header for POST /api/run |

## Building from Source

```bash
# Requires Go 1.21+
go build -o pumprun-server .
```

## Compaction

Safe to run while server is live. Cron-friendly:

```bash
# /etc/cron.d/pumprun — daily at 3am
0 3 * * * pumprun /opt/pumprun/pumprun-server -compact -data /var/lib/pumprun
```

Uses atomic rename — the running server is unaffected.

## Cert Management

### Option A: haproxy (recommended)

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d api.pumprun.com
sudo cat /etc/letsencrypt/live/api.pumprun.com/fullchain.pem \
         /etc/letsencrypt/live/api.pumprun.com/privkey.pem \
         > /etc/ssl/api.pumprun.com.pem
# Auto-renewal
sudo certbot renew --deploy-hook "systemctl reload haproxy"
```

### Option B: Built-in autocert

Replace `main.go` listen block with:

```go
m := &autocert.Manager{
    Cache:      autocert.DirCache("/var/lib/pumprun/certs"),
    Prompt:     autocert.AcceptTOS,
    HostPolicy: autocert.HostWhitelist("api.pumprun.com"),
}
go http.ListenAndServe(":80", m.HTTPHandler(nil))
log.Fatal(http.ListenAndServeTLS(":443", m.TLSConfig(), handler))
```

## Client Configuration

Set the server URL in the HTML `<meta>` tag before deploying to CDN:

```html
<meta name="api-base" content="https://api.pumprun.com">
```

If left empty, the client uses same-origin (only works if client and server share a domain).

To include the API key in client requests, add it to the fetch headers in `build.py`:

```javascript
fetch(API+'/api/run', {
  method:'POST',
  body:payload,
  keepalive:true,
  headers: {'X-Api-Key': 'your-secret-here'}
})
```

## API Endpoints

See `design/SPEC.md` §7 for full API contract.

## Data Format

`/var/lib/pumprun/db.jsonl` — append-only JSON lines. Six fields per game:

| Key | Meaning |
|-----|---------|
| `i` | UUID |
| `s` | Start day index |
| `p` | Banana percentile |
| `r` | Return vs badger |
| `t` | Trade day indices |
| `d` | Signed dollar diff |

## Shared haproxy Setup

If haproxy already serves other sites, add an ACL for the pumprun hostname.
All traffic for `api.gridrun.net` routes to the pumprun backend on `127.0.0.1:8090`.

```
# In your existing frontend section:
frontend https
  bind :443 ssl crt /etc/ssl/
  
  # ... your existing ACLs and backends ...
  
  # pumprun API — route by hostname
  acl is_pumprun hdr(host) -i api.gridrun.net
  use_backend pumprun_api if is_pumprun

# At the bottom:
backend pumprun_api
  server s1 127.0.0.1:8090
```

If you want to match by path instead (e.g., everything under `/api/` goes to pumprun):

```
  acl is_pumprun path_beg /api/
  use_backend pumprun_api if is_pumprun
```

After editing, validate and reload:

```bash
sudo haproxy -c -f /etc/haproxy/haproxy.cfg
sudo systemctl reload haproxy
```
