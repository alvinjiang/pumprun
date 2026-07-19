# defihodler Color Theme — cryptowat.ch Terminal

Sampled from cryptowatch-big.png (1400×682, app-only area).

## Backgrounds

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-chart` | `#000000` | Chart canvas, main background (81% of pixels) |
| `--bg-header` | `#0E0E0F` | Top bar, barely above black |
| `--bg-statusbar` | `#060C17` | Bottom status bar, blue-tinted dark |
| `--bg-panel` | `#131313` | Side panels, raised surfaces |
| `--divider` | `#121212` | Vertical/horizontal separators |

## Text

| Token | Hex | Usage |
|-------|-----|-------|
| `--text-dim` | `#4A4A4A` | General body text, labels, metadata |
| `--text-mid` | `#7F7F7F` | Secondary emphasis |
| `--text-bright` | `#A8A8A8` | Headers, prominent values, emphasis |

## Graph Lines (Primary)

| Token | Hex | Usage |
|-------|-----|-------|
| `--line-hodl` | `#280101` | HODL/badger line — dark red (non-significant order book digits) |
| `--line-ape` | `#002C00` | Ape/YOLO line — dark green (non-significant order book digits) |

## Accents / Highlights

| Token | Hex | Usage |
|-------|-----|-------|
| `--hl-red` | `#C10706` | Red highlight — significant ask digits, candle red |
| `--hl-green` | `#00BC00` | Green highlight — significant bid digits, positive values |
| `--hl-cyan` | `#23C0CF` | Blue/cyan trend line, interactive elements |
| `--hl-yellow` | `#FCFF00` | Star/favorite yellow, warnings, special markers |
| `--hl-purple` | `#3C425B` | Kraken brand purple, secondary accent |

## Candlestick

| Token | Hex | Usage |
|-------|-----|-------|
| `--candle-green` | `#0F680C` | Bullish candle body |
| `--candle-red` | `#C10706` | Bearish candle body (same as hl-red) |

## Typography

- **Primary font**: SF Mono (system monospace, plain zero)
- **Web fallback**: Monaco, Menlo, Consolas, monospace
- **UI labels**: Inter, -apple-system, BlinkMacSystemFont, sans-serif
- **Small caps labels**: SF Mono at 9px, letter-spacing 0.16em, uppercase, color `--text-dim`
- **All price data in monospace** — tabular numerals, aligned columns
- **Digit zero is plain** (not slashed, not dotted)
- **No rounded corners, no shadows, no cards** — raw data on black canvas
