# defihodler — Design Proposal by Kiro
# Created: 2026-07-19
# Version: 1

## What I Saw in the Current Build

Live game at 8900 inspected. Core observations:

### Game Screen Problems
1. **Ticker row hierarchy**: YOU box has 4 sub-values (portfolio, P&L, today %, trades) in one flex
   row — cramped at any viewport, no visual anchoring. The dominant number (your current value)
   competes with the metadata.
2. **FOMO/SAFU box**: Yellow text on dark-red background reads like a debug state indicator.
   Good concept, poor execution. Needs to be a first-class element, not a traffic light.
3. **Badger box**: One number floating in a box. No structure.
4. **Chart shading**: The bright green background band (basket periods) visually dominates the
   chart, making the price lines secondary. In a trading terminal, the lines should dominate.
5. **Position strip**: 5px bar is barely visible at normal viewing distance.
6. **Toggle button**: "HODL · GO TO BITCOIN" while showing FOMO is a double-negative read.
   The FOMO state already communicates the basket position.
7. **Controls**: speed/kbd hints row feels appended, not integrated.

### What's Good (Don't Break)
- Chart rendering is correct: 3 lines, Y-axis auto-scale, yellow BTC period bands, dashed
  future badger line — the logic is sound, just the visual weight distribution is off.
- Summary card overlay is the best-looking element. Stat boxes, verdict stamp, receipt layout
  all work well. Don't redesign this.
- The game concept and copywriting ("NO FEES · NO SPREAD · NO MERCY") are strong.
- Countdown overlay is clean.

---

## Path A — Refined Terminal (Conservative)

**Philosophy**: Fix the specific problems without changing the language.

### Changes from current
1. **Header**: Added a 2px gradient purple accent bar at the very top (cryptowat.ch has this
   exact element). Logo becomes "DEGEN[TERMINAL]" with green bracket color. Right side shows
   day badge + window dates inline — no wasted space.
2. **Stats row**: 3-column grid replacing the cramped flex row:
   - YOU panel (wide): dominant value at 38px, sub-row below for P&L/Today/Trades with proper
     spacing. Green border tint.
   - POSITION panel (narrow): FOMO/SAFU centered, larger and cleaner. Still red/green bg tint.
   - BADGER panel: value + "YOU ARE $X BEHIND" summary line. Structured, not floating.
3. **Chart**: Reduced the alt-basket fill opacity from current (too green) to lower — the lines
   should read first, shading second.
4. **Strip**: 4px, kept but subtle.
5. **Progress + controls**: Integrated into a single compact belt below the chart.
6. **Toggle button**: "HODL · SWITCH TO BITCOIN" — clearer direction. Arrow icon adds intent.

### Lobby
- Scrolling ticker tape at top showing recent game results (very cryptowat.ch)
- Masthead with game name, one-liner, two CTA buttons
- 4-cell global stats bar
- Recent results mini-cards (3-up)
- How-to-play 3-up
- Footer: data attribution + tagline

---

## Path B — Degen Arcade (Expressive)

**Philosophy**: Same terminal DNA, but lean into the ape-vs-badger narrative.

### Palette shift
- Pure black (#000) → near-black with a blue tint (#040408)
- Borders get a purple tint (#16162a, #1e1e38)
- Green shifts from #00bc00 to #00ff88 (phosphor green — more arcade, less Bloomberg)
- Red shifts from #c10706 to #ff2244 (hotter, more aggressive)
- Subtle scanline overlay via CSS repeating-gradient
- Purple accent is more present — purple fill on speed buttons, purple hero gradient

### Key structural changes
1. **Header**: Condenses all live stats into the header bar itself — your value, badger value,
   delta. The header IS the scoreboard. Below it is pure game.
2. **Duel row**: Explicit "THE APE vs HONEY BADGER" framing with a VS badge between them.
   Each fighter gets a panel with name, value, and today's sub-text. This is the narrative
   tension made visual.
3. **Position badge**: Full-width bar below the duel row. FOMO/SAFU becomes a status banner
   with a blinking cursor — classic terminal alive-indicator.
4. **Chart**: Same data, but brighter lines against darker grid lines. Grid uses purple-tinted
   dark lines (#0e0e1a).
5. **Toggle button**: Has a sweep-highlight hover effect, icon (₿ or 🦍), and SPACE hotkey
   visible inline.

### Lobby
- Same tape at top
- Hero section with big "APE vs HONEY BADGER" chip row before the title
- Large faded "VS" watermark in the hero background (CSS, no image)
- Narrative copy that tells the story
- Purple CTA button (matches brand color, not generic green)
- Global stats with colored bottom-accent bars per card
- Results as a proper table (sortable in production) with verdict badge chips
- Lore section: two-column explaining the Ape and the Badger
  with win rate stats

---

## Recommendation

**Path A** if the goal is faithful cryptowat.ch fidelity — it's the safest path and fixes the
real problems without introducing new risk. The game reads better, the lobby makes sense, and
it's entirely consistent with the existing spec and color palette.

**Path B** if you want the game to have more personality and stand out. The lore framing
(APE vs HONEY BADGER) is already in the spec but it's barely surfaced in the current UI. Path B
makes it the central visual idea. The palette is close enough to cryptowat.ch that it still
reads as terminal; the differences are in direction and saturation.

**Hybrid** (likely the right answer): Take Path A's structural fixes (stat row grid, header
belt, lobby tape) and Path B's duel framing (fighter panels, position banner) and narrative
lobby (hero chips, story copy, lore section). The palette question is the main fork — black-pure
vs black-purple-tinted.

---

## What This Doesn't Cover (Intentionally Out of Scope)
- Summary modal: already the best part, not touched
- Game mechanics: these are correct, only visual treatment changed
- Banana test, sound effects, server API: future work per NOTES.md
- Share card, daily mode: future work

## Files
```
design/kiro/
  index.html              Navigation page (this directory's entry point)
  path-a-game.html        Path A game screen mockup
  path-a-lobby.html       Path A lobby mockup  
  path-b-game.html        Path B game screen mockup
  path-b-lobby.html       Path B lobby mockup
  DESIGN-PROPOSAL.md      This file
```

Served at http://10.44.2.26:8901/ during the session that created these files.
