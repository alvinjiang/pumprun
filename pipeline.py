#!/usr/bin/env python3
"""Pipeline to fetch Binance daily klines and compute the volatility basket.

Source: Binance public REST API (no auth needed for klines)
- Daily candles at 00:00 UTC
- 54 coins (BTC pairs for most, USDT pairs for memes)
- Period: 2017-07-14 to present (or 2026-07-15 for historical)

Basket methodology (from DESIGN-NOTES.md):
1. Compute daily log returns for each coin (BTC-denominated)
2. 30-day rolling annualized stddev of log returns
3. Rank by volatility, take top 5
4. 14-day persistence filter: must hold top-5 for 14 consecutive days to enter
5. Equal-weighted, rebalanced daily
6. First 30 days (2017-09-16 to 2017-10-15): fixed basket of BNB, ETH, LTC, NEO
7. USDT pairs converted to BTC terms via BTCUSDT cross-rate

Outputs (in design/data/):
- <SYMBOL>.json: per-coin daily [{t, c_usd, c_btc}]
- btcusdt.json: BTC/USD daily [{t, c}]
- index.json: coin metadata
- basket_returns.bin: Float32Array of daily basket log returns
- basket_history.json: daily composition
- vol_history.json: per-coin vol snapshots
- basket_rotations.json: rotation events
- coins_summary.json: coin summary
"""

import json
import struct
import time
import urllib.request
import os
import sys
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "design", "data")
BINANCE_KLINES = "https://api.binance.com/api/v3/klines"

# All 54 coins: symbol -> Binance pair
COINS = {
    # BTC pairs (Binance lists them as <ASSET>BTC)
    "ETHBTC": "ETHBTC", "LTCBTC": "LTCBTC", "BNBBTC": "BNBBTC", "NEOBTC": "NEOBTC",
    "QTUMBTC": "QTUMBTC", "LINKBTC": "LINKBTC", "IOTABTC": "IOTABTC",
    "EOSBTC": "EOSBTC", "ETCBTC": "ETCBTC", "DASHBTC": "DASHBTC",
    "TRXBTC": "TRXBTC", "XRPBTC": "XRPBTC", "XMRBTC": "XMRBTC",
    "ZECBTC": "ZECBTC", "ADABTC": "ADABTC", "XLMBTC": "XLMBTC",
    "WAVESBTC": "WAVESBTC", "ICXBTC": "ICXBTC", "ZILBTC": "ZILBTC",
    "ONTBTC": "ONTBTC", "VETBTC": "VETBTC", "ATOMBTC": "ATOMBTC",
    "ALGOBTC": "ALGOBTC", "BCHBTC": "BCHBTC", "SOLBTC": "SOLBTC",
    "DOTBTC": "DOTBTC", "AVAXBTC": "AVAXBTC", "MATICBTC": "MATICBTC",
    "FILBTC": "FILBTC", "UNIBTC": "UNIBTC", "AAVEBTC": "AAVEBTC",
    "DOGEBTC": "DOGEBTC", "SUSHIBTC": "SUSHIBTC", "COMPBTC": "COMPBTC",
    "MKRBTC": "MKRBTC", "SNXBTC": "SNXBTC", "YFIBTC": "YFIBTC",
    "ENJBTC": "ENJBTC", "HOTBTC": "HOTBTC", "BATBTC": "BATBTC",
    "ZRXBTC": "ZRXBTC", "GRTBTC": "GRTBTC", "1INCHBTC": "1INCHBTC",
    "CRVBTC": "CRVBTC",
    # USDT pairs (memes — converted to BTC via cross-rate)
    "SANDUSDT": "SANDUSDT", "MANAUSDT": "MANAUSDT", "GALAUSDT": "GALAUSDT",
    "PEOPLEUSDT": "PEOPLEUSDT", "FTTUSDT": "FTTUSDT", "FLOKIUSDT": "FLOKIUSDT",
    "PEPEUSDT": "PEPEUSDT", "BONKUSDT": "BONKUSDT", "WIFUSDT": "WIFUSDT",
    "LUNCUSDT": "LUNCUSDT",
}


def fetch_klines(symbol, start_ms, end_ms, retries=3):
    """Fetch daily klines from Binance. Returns list of [open_time, open, high, low, close, ...]."""
    url = f"{BINANCE_KLINES}?symbol={symbol}&interval=1d&startTime={start_ms}&endTime={end_ms}&limit=1000"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "pumprun/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            print(f"  Attempt {attempt+1}/{retries} for {symbol}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return []


def fetch_all_klines(symbol, start_ms, end_ms):
    """Fetch all klines in 1000-candle chunks (Binance limit)."""
    all_candles = []
    chunk_start = start_ms
    while chunk_start < end_ms:
        candles = fetch_klines(symbol, chunk_start, end_ms)
        if not candles:
            break
        # Remove last candle if it's the same as previous chunk's last
        if all_candles and candles and all_candles[-1][0] == candles[0][0]:
            candles = candles[1:]
        all_candles.extend(candles)
        chunk_start = candles[-1][0] + 86400000  # next day
        print(f"  {symbol}: fetched {len(candles)} candles, total {len(all_candles)}")
        if len(candles) < 1000:
            break
        time.sleep(0.2)  # rate limit
    return all_candles


def build_btc_pair_data(candles):
    """Convert klines to [{t, c_usd, c_btc}] for a BTC pair.
    BTC pair: symbol is like ETHBTC, close price is in BTC.
    We need to compute c_usd using BTCUSDT rate.
    """
    return candles  # raw for now, processed later with BTCUSDT cross-rate


def save_coin_data(symbol, data):
    """Save coin data to JSON file."""
    path = os.path.join(DATA_DIR, f"{symbol}.json")
    with open(path, "w") as f:
        json.dump(data, f)
    print(f"  Saved {len(data)} entries to {path}")


def load_btcusdt():
    """Load BTCUSDT data as {timestamp_ms: price}."""
    path = os.path.join(DATA_DIR, "btcusdt.json")
    with open(path) as f:
        raw = json.load(f)
    return {entry["t"]: float(entry["c"]) for entry in raw}


def compute_basket_returns():
    """Compute daily basket log returns.
    
    Returns list of 3289 floats matching BTCUSDT length exactly.
    NaN for days before basket starts. First valid at index ~56.
    """
    import math
    
    btcusdt = load_btcusdt()
    all_ts = sorted(btcusdt.keys())
    
    # Load coin BTC prices: {symbol: {ts: btc_price}}
    coin_prices = {}
    for symbol in COINS:
        path = os.path.join(DATA_DIR, f"{symbol}.json")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            raw = json.load(f)
        prices = {}
        for entry in raw:
            t = entry["t"]
            if entry.get("c_btc") is not None:
                prices[t] = float(entry["c_btc"])
            elif t in btcusdt:
                prices[t] = float(entry["c_usd"]) / btcusdt[t]
        coin_prices[symbol] = prices
    
    # Daily log returns: {symbol: {ts: log_ret}}
    log_rets = {}
    for sym, prices in coin_prices.items():
        lr = {}
        pts = sorted(prices.keys())
        for i in range(1, len(pts)):
            prev_t, curr_t = pts[i-1], pts[i]
            if prices[prev_t] > 0 and prices[curr_t] > 0:
                lr[curr_t] = math.log(prices[curr_t] / prices[prev_t])
        log_rets[sym] = lr
    
    FIXED = ["BNBBTC", "ETHBTC", "LTCBTC", "NEOBTC"]
    
    consecutive_top5 = {}
    current_basket = []
    basket_returns = []
    basket_history = {}
    rotations = []
    fixed_started = False
    
    for day_idx, ts in enumerate(all_ts):
        date_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        
        # Compute 30-day annualized vol for each coin
        vols = {}
        for sym in coin_prices:
            window = []
            for j in range(max(0, day_idx - 30), day_idx):
                t = all_ts[j]
                if t in log_rets.get(sym, {}):
                    window.append(log_rets[sym][t])
            if len(window) >= 2:
                mean = sum(window) / len(window)
                var = sum((r - mean)**2 for r in window) / (len(window) - 1)
                if var > 0:
                    vols[sym] = math.sqrt(var) * math.sqrt(365)
        
        if not vols:
            basket_returns.append(float('nan'))
            basket_history[date_str] = []
            continue
        
        # Rank by vol
        ranked = sorted(vols.items(), key=lambda x: x[1], reverse=True)
        top5_set = set(sym for sym, vol in ranked[:5])
        
        # Update consecutive days in top 5
        for sym in list(consecutive_top5.keys()):
            consecutive_top5[sym] = consecutive_top5[sym] + 1 if sym in top5_set else 0
        for sym in top5_set:
            if sym not in consecutive_top5:
                consecutive_top5[sym] = 1
        
        # Build basket
        if not fixed_started:
            # Fixed basket period: use FIXED coins that have vol data
            basket = [s for s in FIXED if s in vols]
            if len(basket) >= 3:
                fixed_started = True
            else:
                basket_returns.append(float('nan'))
                basket_history[date_str] = []
                continue
        else:
            # Persistence-filtered basket: coins with 14+ consecutive days in top 5
            eligible = [(sym, vols[sym]) for sym, days in consecutive_top5.items() 
                       if days >= 14 and sym in vols]
            eligible.sort(key=lambda x: x[1], reverse=True)
            basket = [sym for sym, vol in eligible[:5]]
        
        # Record rotation
        if basket != current_basket:
            rotations.append({
                "date": date_str,
                "basket": [(sym, round(vols.get(sym, 0) * 100, 1)) for sym in basket]
            })
            current_basket = basket[:]
        
        basket_history[date_str] = basket[:]
        
        # Equal-weight basket return
        day_rets = [log_rets[sym][ts] for sym in basket if ts in log_rets.get(sym, {})]
        basket_returns.append(sum(day_rets) / len(day_rets) if day_rets else float('nan'))
    
    return basket_returns, basket_history, rotations

def verify_against_existing():
    """Compare newly computed data against existing files."""
    print("\n=== VERIFICATION ===")
    
    # Compare basket_returns.bin
    new_path = os.path.join(DATA_DIR, "basket_returns.bin")
    # Load existing from build.py's embedded data? No — compare with a copy.
    # For now, just report stats.
    with open(new_path, "rb") as f:
        data = f.read()
    floats = struct.unpack(f"<{len(data)//4}f", data)
    print(f"New basket_returns.bin: {len(floats)} entries, {len(data)} bytes")
    print(f"  Range: [{min(floats):.6f}, {max(floats):.6f}]")
    
    # Compare coin counts
    for symbol in sorted(COINS.keys()):
        path = os.path.join(DATA_DIR, f"{symbol}.json")
        if os.path.exists(path):
            with open(path) as f:
                coin = json.load(f)
            print(f"  {symbol}: {len(coin)} entries, {coin[0]['t']} to {coin[-1]['t']}")



def compute_basket_forward(last_ts, lookback_days=60):
    """Compute basket returns for NEW data only (after last_ts).
    Uses vol-based 14-day persistence filter.
    Returns: list of (ts, basket_return) tuples for dates > last_ts.
    """
    import math
    
    btcusdt = load_btcusdt()
    all_ts = sorted(btcusdt.keys())
    
    # Find index of last_ts
    try:
        start_idx = all_ts.index(last_ts) + 1
    except ValueError:
        start_idx = len(all_ts)
    
    if start_idx >= len(all_ts):
        return []
    
    # Load coin data
    coin_prices = {}
    for symbol in COINS:
        path = os.path.join(DATA_DIR, f"{symbol}.json")
        if not os.path.exists(path):
            continue
        with open(path) as f:
            raw = json.load(f)
        prices = {}
        for entry in raw:
            t = entry["t"]
            if entry.get("c_btc") is not None:
                prices[t] = float(entry["c_btc"])
            elif t in btcusdt:
                prices[t] = float(entry["c_usd"]) / btcusdt[t]
        coin_prices[symbol] = prices
    
    # Compute log returns
    log_rets = {}
    for sym, prices in coin_prices.items():
        lr = {}
        pts = sorted(prices.keys())
        for i in range(1, len(pts)):
            if prices[pts[i-1]] > 0 and prices[pts[i]] > 0:
                lr[pts[i]] = math.log(prices[pts[i]] / prices[pts[i-1]])
        log_rets[sym] = lr
    
    # Track consecutive days in top 5
    consecutive_top5 = {}
    current_basket = []
    results = []
    
    for day_idx in range(start_idx, len(all_ts)):
        ts = all_ts[day_idx]
        date_str = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        
        # Compute 30-day rolling annualized vol
        vols = {}
        for sym in coin_prices:
            window = []
            for j in range(max(0, day_idx - 30), day_idx):
                t = all_ts[j]
                if t in log_rets.get(sym, {}):
                    window.append(log_rets[sym][t])
            if len(window) >= 2:
                mean = sum(window) / len(window)
                var = sum((r - mean)**2 for r in window) / (len(window) - 1)
                if var > 0:
                    vols[sym] = math.sqrt(var) * math.sqrt(365)
        
        if not vols:
            continue
        
        # Update consecutive top-5 counters
        ranked = sorted(vols.items(), key=lambda x: x[1], reverse=True)
        top5_set = set(sym for sym, vol in ranked[:5])
        
        for sym in list(consecutive_top5.keys()):
            consecutive_top5[sym] = consecutive_top5[sym] + 1 if sym in top5_set else 0
        for sym in top5_set:
            if sym not in consecutive_top5:
                consecutive_top5[sym] = 1
        
        # Build basket from coins with 14+ consecutive days in top 5
        eligible = [(sym, vols[sym]) for sym, days in consecutive_top5.items()
                   if days >= 14 and sym in vols]
        eligible.sort(key=lambda x: x[1], reverse=True)
        basket = [sym for sym, vol in eligible[:5]]
        
        if len(basket) < 5:
            continue  # Not enough qualifying coins yet
        
        # Compute equal-weight return
        day_rets = [log_rets[sym][ts] for sym in basket if ts in log_rets.get(sym, {})]
        if day_rets:
            results.append((ts, sum(day_rets) / len(day_rets)))
    
    return results


def append_basket_returns(new_returns):
    """Append new returns to basket_returns.bin."""
    path = os.path.join(DATA_DIR, "basket_returns.bin")
    with open(path, "ab") as f:
        for ts, ret in new_returns:
            f.write(struct.pack("<f", float(ret)))
    print(f"Appended {len(new_returns)} new returns to {path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="pumprun data pipeline")
    parser.add_argument("--fetch", action="store_true", help="Fetch fresh data from Binance")
    parser.add_argument("--compute", action="store_true", help="Compute basket returns (WARNING: overwrites basket_returns.bin)")
    parser.add_argument("--append", action="store_true", help="Append new data + compute forward returns (safe)")
    parser.add_argument("--all", action="store_true", help="Fetch + compute")
    args = parser.parse_args()
    
    if not any([args.fetch, args.compute, args.append, args.all]):
        parser.print_help()
        sys.exit(1)
    
    START_MS = 1499990400000
    END_MS = 1784246400000
    
    if args.fetch or args.all:
        print("=== Fetching BTCUSDT ===")
        btc_candles = fetch_all_klines("BTCUSDT", START_MS, END_MS)
        btc_data = [{"t": c[0], "c": c[4]} for c in btc_candles]
        save_coin_data("btcusdt", btc_data)
        
        for symbol, pair in COINS.items():
            print(f"\n=== Fetching {symbol} ({pair}) ===")
            candles = fetch_all_klines(pair, START_MS, END_MS)
            if not candles:
                print(f"  WARNING: No data for {pair}")
                continue
            is_usdt = symbol.endswith("USDT")
            data = [{"t": c[0], "c_usd": c[4], "c_btc": c[4] if not is_usdt else None} for c in candles]
            save_coin_data(symbol, data)
            time.sleep(0.3)
    
    if args.compute or args.all:
        print("\n=== Computing basket returns ===")
        returns, history, rotations = compute_basket_returns()
        save_basket_returns(returns)
        with open(os.path.join(DATA_DIR, "basket_history.json"), "w") as f:
            json.dump(history, f)
        with open(os.path.join(DATA_DIR, "basket_rotations.json"), "w") as f:
            json.dump(rotations, f, indent=2)
    
    if args.append:
        # Find last timestamp in existing basket_returns.bin
        basket_path = os.path.join(DATA_DIR, "basket_returns.bin")
        btcusdt = load_btcusdt()
        all_ts = sorted(btcusdt.keys())
        with open(basket_path, "rb") as f:
            existing = len(f.read()) // 4
        last_ts = all_ts[min(existing, len(all_ts)) - 1] if existing > 0 else all_ts[0]
        print(f"Existing basket: {existing} entries, last timestamp: {last_ts}")
        
        new_returns = compute_basket_forward(last_ts)
        append_basket_returns(new_returns)
