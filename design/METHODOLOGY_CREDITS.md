# METHODOLOGY & CREDITS

----

# Real Data

Market data is sourced from Binance, without which we wouldn't have a liquid token ecosystem. The constraints that come from this choice and realistic and practical. Because crypto has no daily closing price (it's a 24/7 market), we pick a fixed time every day to source a single daily price. The dataset starts in mid-2017, when Binance was founded. Although Bitcoin was already trading at around USD 2,000 by then, there were not many alternative coins (fewer still which were not Bitcoin forks or clones). The altcoin market really only grew after Binance (in an attempt to get a lead over earlier competitors like Bittrex with stricter listing rules) quickly started listing every coin it could find. The choice to use Binance data was grounded in easy access to reliable market data and its role in shaping the ecosystem but it also means we miss the truly degen stuff like the Solana meme coins. It turns out anyway that such short-lived tokens would have to be excluded to make the game playable.

# The Alt Basket

Our degen altcoin basket is made up of the Top 5 (for at least the prior 2 weeks) volatile (30-day rolling annual stddev) altcoins equally weighted. The chart ticks on daily prices so having a 14-day minimum filters out coins that may otherwise show as blips rather than a trend on a 365 day chart. This results in about +/- 50 coins that stay in the basket for an average of 7 days (after the 14-day filter) as of this writing.

The trading window is 1 year, which for crypto is 365 trading days. This was selected to give a good balance of playtime at 1x speed (about 45s), cover sufficient crypto events/seasons and also happily covers both the time horizon between trading and investing, and typical crypto holding periods. It probably comes as no surprise that as the window lengthens the proportion of Badger wins goes up - from about 60% at 90 days to 80% at 2 years (according to our banana casino).

# Fees, Spread and Slippage

No fees, spread, slippage. These are the things that will kill you in real life trading, which don't matter as much to a long term single-asset HODLer. It's in your favour that we don't model it here. 

# Calculation

Both portfolios start with $10,000 worth of Bitcoin on day 1, at day 1 BTC/USD prices. 

The badger holds this BTC and converts it back at the end of the 365 days at day 365 BTC/USD prices. It does not trade at all during the period, not even BTC/USD. 

The player's (your) portfolio starts in the altcoin (aka Degen) basket, unless you toggle out to hold BTC during the countdown before Day 1. Then it starts same as the badger. Whenever you toggle, the full value of your holdings are converted into the other side at market prices. This means you'll want to be on the side of the higher line, and optimally switch when the gap is the biggest and about to move in the opposite direction. The yellow line represents your current performance. 

# Chart

The green line represents the performance of the altcoin basket, red line for BTC performance. The yellow line represents your performance, so ideally you'll want to keep that above both red and green. When you first start the game it may not be easy to see 3 lines, as the yellow line will initially follow either the green or red line (depending on if you toggled HODL/YOLO during the countdown).

The day bar represents how far you are in the game. There is no option for other time periods. You can speed it up using the speed controls if you feel it's going nowhere, or slow it down for more precise timing. You can also Pause and toggle during the Pause - the game is less about market timing than predicting the future, and if you wanted an edge on predictability just keep replaying the same game.

# Inspiration

In parts of my personal and professional life I've been asked to consider the value (or my opinion) of trading shitcoins. At those times I often wished there was a simple resource explaining how HODLing BTC long term is a "better" strategy than degen ape-ing into coins. (Unless you're a professional, which I occasionally was, but if you are you wouldn't be asking me.) The point being that, yes there may be alpha that traders work hard to capture; if you want 2-min advice, try this game!

When I recently stumbled upon the absolutely fantastic [Beat The Couch](https://beatthecouch.com/), I realised that it was exactly what I was looking for, except applied to crypto trading (rather than market timing). I want to give credit to their biggest innovation - the monkey simulator, that runs 1000 rounds using the same parameters you played to give you an idea if you're really good or just lucky. Run a monkey simulator on your real-life trades to align for a quick ego/skill alignment. 

# Gratitude

Besides the couch at Beat the Couch, I'm also very grateful to [fyra](https://fyra.sh) for hosting this on their CDN. The stats tracking backend is a small self-hosted worker hosted by the [GRIDRUN](https://gridrun.net) team. 

Thanks also to you for playing, giving [feedback](mailto:degen@gridrun.net) or sharing the link. Hope you had fun and remember when asking a professional trader for tips - yes we're secretive but it's actually not that we don't want to share, it's just that... it's not that simple.

I leave you with a note from my AI coding partner: 
_Interesting... BTC is down ~34% of the time, up ~66% of the time over 365-day windows. The badger wins 70.2% of the time, but BTC itself only wins 65.6% — meaning the basket underperforms BTC even when BTC is up, and gets crushed when BTC is down._


