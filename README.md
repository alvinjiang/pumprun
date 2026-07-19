# pumprun

A crypto degen timing game. You have $10,000 and one year (365 days) of secret
historical market data. One button: HODL Bitcoin or YOLO into the 5 most volatile
altcoins. Your opponent is the Honey Badger — it bought BTC on day one and never
looked back.

**[Play now](https://pumprun.com)**

## How It Works

1. **$10,000 in BTC.** A random 365-day window from 2017–2026.
2. **One button.** HODL BTC or YOLO the basket of top 5 most volatile altcoins.
3. **The badger bought BTC and never looked back.** Beat it.

Every win is audited by 1,000 simulated apes (permutation test). Beat 90% of them
and you're a DEGEN. Otherwise, you're just a LUCKY APE.

## Project Structure

```
├── web/                  # Single-page game client
│   └── index.html        # ~142 KB, no framework, embedded data
├── server/               # Go stats server
│   ├── main.go           # ~350 lines, append-only JSON-lines storage
│   └── README.md         # Deploy instructions
├── design/               # Specs, mocks, data, lore
│   ├── SPEC.md           # Authoritative product spec
│   ├── data/             # Pre-computed datasets (54 coins, 2017–2026)
│   └── kiro/             # UI mockups (design proposals)
├── build.py              # Web client build script
├── AGENTS.md             # Agent communication protocol
└── bugfix-tracker.md     # Bug tracker
```

## Quick Start

### Web Client
```bash
python3 build.py          # generates web/index.html
cd web && python3 -m http.server 8900
```

### Server
```bash
cd server
go build -o defihodler-server .
./defihodler-server -addr :8080 -data data/
```

See `server/README.md` for full deploy instructions.

## Tech Stack

- **Client**: single HTML file, vanilla JS, Canvas API. No framework.
- **Server**: Go, append-only JSON-lines file, in-memory stats, rate-limited.
- **Data**: 54 Binance coins, 2017–2026, pre-computed basket returns (12.8 KB binary).
- **Font**: SF Mono (system, plain zero). Colors sampled from cryptowat.ch.

## License

TBD

## Configuration

### Pointing the client to your server

Set the `<meta name="api-base">` tag in `web/index.html`:

```html
<meta name="api-base" content="https://api.yourdomain.com">
```

If left empty, the client uses the same origin as the page.

### Server authentication

Protect the POST endpoint with a shared secret:

```bash
./defihodler-server -api-key "your-secret-here"
```

See `server/README.md` for full deploy instructions, TLS setup, and systemd unit.
