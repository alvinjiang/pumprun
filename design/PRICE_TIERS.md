# Price Tiers — "What Can You Buy?"

Returned by server in `/api/run` response. Shown as a dialog box at game end.
Tiers are threshold-based: you get the highest tier your final dollar value meets or exceeds.
The text is snarky, crypto-native. Priced approximately for the game's 2017–2026 context.

| Threshold | Text |
|-----------|------|
| $500,000+ | "Not the U.S. Constitution — you're a little short of the 2021 $43.2M price." |
| $350,000+ | "Now Lambo." |
| $250,000+ | "If only you had an allocation from RM..." |
| $100,000+ | "Tesla for your BTC?" |
| $60,000+ | "You'd still need to trade that Daytona in for a Royal Oak." |
| $40,000+ | "Fly your friends private for a Vegas whale experience." |
| $20,000+ | "Pepsi or Batman?" |
| $10,000+ | "A decent APE NFT." |
| $5,000+ | "Antminer or RTX GPU?" |
| $1,000+ | "Aeron or Embody?" |
| $500+ | "Rimowa or Rama Works, depending on how active you are." |
| $100+ | "You'll want a cold wallet for all that Bitcoin!" |
| $40+ | "Order yourself a 2010 Bitcoin Pizza." |
| < $40 | "Beef or Shrimp Ramen?" |

## Notes

- Price references are 2017–2026 era: Lamborghini (~$350K), Tesla Model S (~$100K), 
  Bored Ape floor (~$100K at peak, ~$10K post-crash), Bitcoin Pizza ($41 in 2010),
  Rolex Daytona (~$35K), Audemars Piguet Royal Oak (~$60K), ConstitutionDAO ($43.2M bid, 2021),
  Herman Miller Aeron (~$1,500), Herman Miller Embody (~$1,800),
  Rimowa luggage (~$800), Rama Works keyboard (~$500),
  Antminer S19 (~$3K at peak), RTX 4090 (~$1,600),
  Ledger/Trezor cold wallet (~$100-200),
  RM (Rothschild/Market-maker allocation reference),
  Pepsi vs Batman = Rolex Pepsi GMT vs Batman GMT (~$20K grey market)
- Server-side to avoid exposing the tier list in client source
- Dialog box should show total value prominently, then the matched tier text
