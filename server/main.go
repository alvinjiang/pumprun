package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"

	"golang.org/x/time/rate"
)
var (
	addr        = flag.String("addr", ":8080", "listen address")
	dataDir     = flag.String("data", "data/", "data directory")
	allowOrigin = flag.String("allow-origin", "", "allowed CORS origins, comma-separated (empty = disable check)")
	allowRefer  = flag.String("allow-referer", "", "required Referer prefix (empty = disable check)")
	compact     = flag.Bool("compact", false, "compact the data file and exit")
	apiKey     = flag.String("api-key", "", "required X-Api-Key header for POST /pump/run (empty = disable check)")
)

// --- Storage ---
type Store struct {
	mu    sync.RWMutex
	file  *os.File
	index map[string]json.RawMessage
}

// In-memory ledger (computed from log, never written to disk)
type Ledger struct {
	mu          sync.RWMutex
	Games       float64 `json:"games"`
	BadgerWins  float64 `json:"badger_wins"`
	DegenWins   float64 `json:"degen_wins"`
	LuckyWins   float64 `json:"lucky_wins"`
	Lost     float64 `json:"lost"`
}

var globalLedger = &Ledger{}

func OpenStore(path string) (*Store, error) {
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		return nil, err
	}
	f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_RDWR, 0644)
	if err != nil {
		return nil, err
	}
	s := &Store{file: f, index: make(map[string]json.RawMessage)}
	if err := s.replay(); err != nil {
		return nil, fmt.Errorf("replay: %w", err)
	}
	return s, nil
}

type LogEntry struct {
	Key   string          `json:"key"`
	Value json.RawMessage `json:"value"`
}

func (s *Store) replay() error {
	dec := json.NewDecoder(s.file)
	for {
		var e LogEntry
		if err := dec.Decode(&e); err == io.EOF {
			return nil
		} else if err != nil {
			// Truncated last line? Stop here.
			log.Printf("replay: decode error (stopping): %v", err)
			return nil
		}
		s.index[e.Key] = e.Value
	}
}

func (s *Store) Put(key string, value interface{}) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	raw, err := json.Marshal(value)
	if err != nil {
		return err
	}
	entry := LogEntry{Key: key, Value: raw}
	line, err := json.Marshal(entry)
	if err != nil {
		return err
	}
	line = append(line, '\n')

	if _, err := s.file.Write(line); err != nil {
		return err
	}
	if err := s.file.Sync(); err != nil {
		return err
	}
	s.index[key] = raw
	return nil
}

func (s *Store) Get(key string) (json.RawMessage, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	v, ok := s.index[key]
	return v, ok
}

func (s *Store) GetJSON(key string, dest interface{}) bool {
	raw, ok := s.Get(key)
	if !ok {
		return false
	}
	return json.Unmarshal(raw, dest) == nil
}

// RecentKeys returns up to n most recent keys matching prefix, in insertion order.
func (s *Store) RecentKeys(prefix string, n int) []json.RawMessage {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var out []json.RawMessage
	// Re-scan file for order (index is a map, no insertion order)
	f, err := os.Open(s.file.Name())
	if err != nil {
		return out
	}
	defer f.Close()

	dec := json.NewDecoder(f)
	for dec.More() {
		var e LogEntry
		if err := dec.Decode(&e); err != nil {
			break
		}
		if strings.HasPrefix(e.Key, prefix) {
			out = append(out, e.Value)
		}
	}
	if len(out) > n {
		out = out[len(out)-n:]
	}
	return out
}

func (s *Store) Compact() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	tmpPath := s.file.Name() + ".compact"
	tmp, err := os.Create(tmpPath)
	if err != nil {
		return err
	}
	enc := json.NewEncoder(tmp)
	for k, v := range s.index {
		if err := enc.Encode(LogEntry{Key: k, Value: v}); err != nil {
			tmp.Close()
			os.Remove(tmpPath)
			return err
		}
	}
	tmp.Close()

	oldPath := s.file.Name()
	s.file.Close()
	if err := os.Rename(tmpPath, oldPath); err != nil {
		return err
	}
	s.file, err = os.OpenFile(oldPath, os.O_APPEND|os.O_CREATE|os.O_RDWR, 0644)
	return err
}

// --- Rate Limiter ---
type RateLimiter struct {
	mu       sync.Mutex
	limiters map[string]*rate.Limiter
}

func NewRateLimiter() *RateLimiter {
	return &RateLimiter{limiters: make(map[string]*rate.Limiter)}
}

func (rl *RateLimiter) Allow(ip string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	lim, ok := rl.limiters[ip]
	if !ok {
		lim = rate.NewLimiter(1, 3) // 1/sec, burst 3
		rl.limiters[ip] = lim
	}
	return lim.Allow()
}

// --- Spam Checks ---
func spamCheck(w http.ResponseWriter, r *http.Request) bool {
	if *allowOrigin != "" {
		origin := r.Header.Get("Origin")
		if origin != "" && origin != *allowOrigin {
			http.Error(w, "forbidden", 403)
			return true
		}
	}
	if *allowRefer != "" {
		ref := r.Header.Get("Referer")
		if ref == "" || !strings.HasPrefix(ref, *allowRefer) {
			http.Error(w, "forbidden", 403)
			return true
		}
	}
	return false
}

// --- Handlers ---
func handleLedger(store *Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		globalLedger.mu.RLock()
		raw, _ := json.Marshal(globalLedger)
		globalLedger.mu.RUnlock()
		w.Header().Set("Content-Type", "application/json")
		w.Write(raw)
	}
}

func handleRecent(store *Store) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		games := store.RecentKeys("run:", 10)
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{"games": games})
	}
}

func handleTape(w http.ResponseWriter, r *http.Request) {
	// v1: static fixture
	coins := []map[string]interface{}{
		{"sym": "BTC", "price": 64892.35, "change24h": 2.41},
		{"sym": "ETH", "price": 3210.50, "change24h": -1.83},
		{"sym": "SOL", "price": 142.80, "change24h": 5.12},
		{"sym": "DOGE", "price": 0.1234, "change24h": -0.87},
		{"sym": "PEPE", "price": 0.00000812, "change24h": 14.72},
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{"coins": coins})
}

func handleRun(store *Store, rl *RateLimiter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			http.Error(w, "method not allowed", 405)
			return
		}
		if *apiKey != "" && r.Header.Get("X-Api-Key") != *apiKey {
			http.Error(w, "unauthorized", 401)
			return
		}
		if spamCheck(w, r) {
			return
		}

		ip, _, _ := net.SplitHostPort(r.RemoteAddr)
		if !rl.Allow(ip) {
			http.Error(w, "rate limit exceeded", 429)
			return
		}

		var body map[string]interface{}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			http.Error(w, "invalid JSON", 400)
			return
		}
		id, ok := body["i"].(string)
		if !ok || id == "" {
			http.Error(w, "missing id", 400)
			return
		}

		// Store only essential fields to keep log compact
		compact := map[string]interface{}{
			"i":     body["i"],
			"s":      body["s"],
			"p":    body["p"],
			"r":    body["r"],
			"t": body["t"],
			"d":   body["d"],
		}
		if err := store.Put("run:"+id, compact); err != nil {
			log.Printf("store.Put error: %v", err)
			http.Error(w, "internal error", 500)
			return
		}

		// Update in-memory ledger (never written to log)
		ret, _ := body["r"].(float64)
		pct, _ := body["p"].(float64)
		globalLedger.mu.Lock()
		globalLedger.Games++
		if ret > 0.02 && pct >= 90 {
			globalLedger.DegenWins++
		} else if ret > -0.01 {
			globalLedger.LuckyWins++
		} else {
			globalLedger.BadgerWins++
		}
		if d, ok := body["d"].(float64); ok { if d < 0 { globalLedger.Lost += -d } }
		globalLedger.mu.Unlock()

		// Price tier lookup
		tiers := [][]interface{}{
			{0, "Beef or Shrimp Ramen?"},
			{40, "Order yourself a 2010 Bitcoin Pizza."},
			{100, "You'll want a cold wallet for all that Bitcoin!"},
			{500, "Rimowa or Rama Works, depending on how active you are."},
			{1000, "Aeron or Embody?"},
			{5000, "Antminer or RTX GPU?"},
			{10000, "A decent APE NFT."},
			{20000, "Pepsi or Batman?"},
			{40000, "Fly your friends private for a Vegas whale experience."},
			{60000, "You'd still need to trade that Daytona in for a Royal Oak."},
			{100000, "Tesla for your BTC?"},
			{250000, "If only you had an allocation from RM..."},
			{350000, "Now Lambo."},
			{500000, "Not the U.S. Constitution — you're a little short of the 2021 $43.2M price."},
		}
		youDollars, _ := body["youDollars"].(float64)
		if youDollars == 0 {
			if final, ok := body["final"].(float64); ok {
				youDollars = final
			}
		}
		tierText := tiers[0][1].(string)
		tierLabel := ""
		for _, t := range tiers {
			thresh, _ := t[0].(int)
			if youDollars >= float64(thresh) {
				tierText = t[1].(string)
				tierLabel = fmt.Sprintf("$%d+", thresh)
			}
		}

		resp := map[string]interface{}{
			"tier":      tierLabel,
			"tierText":  tierText,
			"dailyRank": map[string]interface{}{"total": 0, "worse": 0},
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}
}


func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if *allowOrigin != "" {
			origin := r.Header.Get("Origin")
			if origin != "" {
				for _, o := range strings.Split(*allowOrigin, ",") {
					if origin == strings.TrimSpace(o) {
						w.Header().Set("Access-Control-Allow-Origin", origin)
						break
					}
				}
			}
			if w.Header().Get("Access-Control-Allow-Origin") == "" {
				w.Header().Set("Access-Control-Allow-Origin", strings.Split(*allowOrigin, ",")[0])
			}
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
			if r.Method == "OPTIONS" {
				w.WriteHeader(204)
				return
			}
		}
		next.ServeHTTP(w, r)
	})
}

func main() {
	flag.Parse()

	store, err := OpenStore(filepath.Join(*dataDir, "db.jsonl"))
	if err != nil {
		log.Fatalf("open store: %v", err)
	}
	defer store.file.Close()

	if *compact {
		log.Printf("compacting %s...", store.file.Name())
		if err := store.Compact(); err != nil {
			log.Fatalf("compact: %v", err)
		}
		log.Printf("compacted. old size now replaced.")
		return
	}

	rl := NewRateLimiter()

	mux := http.NewServeMux()
	mux.HandleFunc("/pump/ledger", handleLedger(store))
	mux.HandleFunc("/pump/recent", handleRecent(store))
	mux.HandleFunc("/pump/tape", handleTape)
	mux.HandleFunc("/pump/run", handleRun(store, rl))
	mux.HandleFunc("/pump/daily-rank", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{"total": 0, "worse": 0})
	})

	handler := corsMiddleware(mux)

	log.Printf("listening on %s", *addr)
	if err := http.ListenAndServe(*addr, handler); err != nil {
		log.Fatalf("serve: %v", err)
	}
}
