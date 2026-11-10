# Beethoven — asset-specific technical indicator audit
**As of 2026-11-10. Research only. No LIVE changes.**

## Bottom line
The Composer-confirmed #1 semiconductor + TSLQ bearish-sleeve strategy has a **historical** 503.8% annualized return and -41.9% max drawdown over **2025-09-30–2026-11-09**. Its results have already been used to select/modify strategies in the same sample, making them in-sample, not independently prospective.

I inspected both supplied Reddit threads and the original Beethoven source tree; tested daily indicators on historical prices; inspected daily OHLCV/VWAP for selected names; tested the exact original GDXU RSI gates; and expanded screening to all 98 symbols in the existing historical dataset.

**NO risky stock or leveraged ETF signal was statistically significant after a 10%-FDR multiple-testing correction over 962 usable comparisons.** Two tiny <~1.1bp BIL cash-ETF indicator differences passed, economically uninteresting once costs are included. This excludes any claim to have found "the best" profitable indicator per stock.

## Sources
- GitHub Actions artifact `13766198532`, `public_closes.csv`: 98 symbols, 1,254 dates, 2021-11-10–2026-11-09; vendor adjusted daily Yahoo Finance close series; survivorship/inception biases possible.
- User Composer exported allocation CSVs and screenshots from the Beethoven project; their test periods differ, so **compare identical date ranges**.
- Massive.com adjusted daily aggregate OHLCV for TSLA, TSLL, TSLS, TSLQ, GDX, GDXJ, GDXU and GDXD; data as of 2026-11-09. The TSLA ETF joint sample begins 2025-05 because the current TSLQ pull is truncated to that date by accessible source.
- [Original TSLA Reddit strategy](https://www.reddit.com/r/options/comments/1juwtbq/a_decent_tsla_strategy_added_free_indicators/): 3-minute ATR(14,3), proprietary Golden Digger-like filter, exit ATR(14,2.5), W–F trades, 68 claimed trades in 2025. No independently verified track record. No direct equivalent Composer daily rule.
- [Swing indicator Reddit discussion](https://www.reddit.com/r/options/comments/1du8n49/best_indicators_for_swing_trading/): diverse users mention RSI, MACD, MA, Bollinger; anecdotal.
- [Official Composer indicators](https://www.composer.trade/learn/how-composer-symphonies-work): RSI, moving average price/return, EMA price, cumulative return, current price, std dev, maximum drawdown. ATR, MACD, Bollinger and VWAP **not listed natively**. Treat external equivalents as separate execution workflows, not silently approximated.
- [Official Composer trading period](https://help.composer.trade/article/63-trading-period): roughly 3:45–4 PM ET; close-to-close backtest performance does not ensure those fills.
- [SEC leveraged ETFs risk bulletin](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-alerts/sec), [BMO gold-miner leveraged ETN product](https://microsectors.com/goldminers/), [Direxion TSLL/TSLS](https://www.direxion.com/product/daily-tsla-bull-and-bear-leveraged-single-stock-etfs), [Tradr TSLQ](https://www.tradretfs.com/tslq-2x-short-tsla-daily-etf).
- [Technical-rule data-snooping academic paper](https://doi.org/10.1111/0022-1082.00163) and [time-series momentum academic evidence](https://doi.org/10.1016/j.jfineco.2011.11.003). The latter concerns multiple asset-class futures, not proof that any particular daily RSI rule works on TSLA.
- [Options Industry Council pricing](https://www.optionseducation.org/optionsoverview/options-pricing): long/short listed options have time-to-expiry, IV, strike, theta and spreads, so cannot assign leverage or profitability without historical option chain quotes.

## Test design
- Daily-adjusted-close indicators: RSI14, MACD histogram/crosses, SMA20/50/200, ROC5/20/60, Bollinger20 ±2 standard deviations. Buy/sell signals are known only after close t. Main diagnostic: close t to close t+1. Actual late-day order execution could differ.
- Split early `2022-01-03–2024-12-31`, recent `2025-01-02–2026-11-09`. For young funds early samples are limited/nonexistent.
- 962 usable recent-sample comparisons across 98 symbols and 16 candidate indicators, at least 30 positive/negative conditional observations, HAC maxlag 5 standard errors and Benjamini-Hochberg FDR correction. Zero economically meaningful FDR passes on risky instruments.
- A signal's conditional next-day average is **not** the return of an executable strategy. Conditional groups are serially dependent, there are many comparisons, and no true untouched test segment remains in the repeatedly studied 2025–26 dates.

## Particularly useful hypotheses — not proofs
| Underlying / product | Candidate indicator | Earlier vs later descriptive following-day difference | Caveat |
|---|---|---|---|
| SOXL bullish | Close > SMA50 | +43 / +54 bps | Positive but not statistically significant after multiple tests |
| SOXL bullish | ROC5 negative (short pullback) | +67 / +45 bps | Short-term reversal; evaluate nested under longer-term trend |
| SOXL bullish | Original Beethoven RSI3 <30: mean next-day SOXL return | +0.90% / +1.20% | This is conditional mean, not above-vs-below edge |
| SOXL bearish | Original Beethoven RSI10 >79: mean next-day SOXS return | +2.19% / -0.56% | Failed stability; **do not transfer automatically** |
| GDXU bullish | Original Beethoven RSI3 <30: mean next-day GDXU return | +0.14% / +2.55% | Very regime-sensitive, no standalone return proof |
| GDXD bearish | Original Beethoven GDXU RSI10 >79: next-day GDXD mean | +3.96% (9 events) / +0.33% (20 events) | Small sample and uneven effect |
| GDXU bullish | SMA50 > SMA200 | +17 / +54 bps | Trend candidate, not sufficient for 3x pair switch |
| TSLA | MACD bearish histogram crossover | +85 / +251 bps next-day TSLA difference (26/23 events) | **Contrarian**, NOT automatic bearish TSLA signal; no FDR pass |
| TSLA -> TSLR | Original Beethoven RSI3 <30: mean next-day TSLR return | -0.13% / +0.67% | Does not reproduce gold's early/recent consistency |
| NVDL | RSI14 <45 | +122 / +81 bps | Experimental oversold bounce |
| DFEN | RSI14 <45 | +113 / +42 bps | Experimental reversal, not momentum-chase proof |
| PTIR | RSI14 >55 | -317 / -96 bps | Young fund, volatility; avoid treating high RSI as a bull guarantee |
| AMDL | ROC5 negative | +131 / +88 bps | Experimental, no FDR significance |
| URAA | Close > SMA50 | +69 / +31 bps | Young fund, short early sample |
| PLTR | ROC5 negative | +38 / +13 bps | Small descriptive difference |

## ATR and VWAP checks
Massive daily high/low/close true range for selected names. ATR14 / close above rolling prior-126-day 75th-percentile threshold:
- GDXU 2025: next-day **absolute** movement 6.24% on high-ATR days vs 4.98% otherwise; 2026: 8.76% vs 7.46%. Volatility sizing candidate, not directional alpha.
- TSLA 2026: 2.63% high-ATR next-day absolute vs 2.06% otherwise; 2025 only nine high-ATR observations with reversed average (1.82% vs 2.42%).
- Daily VWAP cross DOWN for TSLA: 2025 next-day mean +0.25%; 2026 -0.28%; no stable rule. Daily VWAP crossing is **not** the Reddit author's 3-minute intraday crossing.
- A 3-minute ATR trail / PSAR/Golden Digger entry and stop-loss needs actual intraday 3-minute data, time-stamped options quotes/ETF prices, trade count, spread/fees, and commission assumptions. It was **not** reproduced here.

## Non-equivalence of indicators and leveraged ETF returns
Tesla: TSLR/TSLL/TSLT = +2x daily; TSLQ/TSLZ/TSDD = -2x daily; TSLS=-1x daily; TSL=+1.25x daily. These are issuer-verified product targets; net/tracking differences, fees and available history vary. Tesla calls and puts are not fixed-leverage ETFs.
Gold miners GDXU/GDXD: +3x/-3x daily **ETNs** on the MINERS index (GDX and GDXJ-related), with daily reset and issuer credit risk.
2025-09-30 through 2026-11-06 simplified non-Composer **single-pair** daily rotation checks (60% pair risk on Tesla, 50% on gold; remainder approximated zero-return cash; ~10bps one-way turnover cost; signal evaluated at close t):
- TSLL/TSLQ using TSLA SMA50 cross: about **-76.4% CAGR, -80.6% MDD**; the four-signal RSI/MACD/SMA/ROC composite also lost money.
- TSLL/TSLS using TSLA SMA50 cross: about **-66.6% CAGR, -71.6% MDD**.
- GDXU/GDXD using GDX SMA50: about **-46.3% CAGR, -56.5% MDD**; using GDX ROC20 also negative.
These poor results **do not invalidate Beethoven's full nested strategy**, but disprove the simple idea that a universal common bullish/bearish signal produces 400% CAGR on each pair.

## Candidate bull/bear confidence design (research architecture only)
1. Keep tested #1 core market-regime/priority gates and SOXL/SOXS+TSLQ pair **unchanged** as comparison baseline.
2. Underlying-specific confidence must combine a different *type* of feature: broader trend (SMA50/200), tactical reversal (RSI3/ROC5), volatility risk (ATR14 normalized, or Composer's std-dev *proxy*), and market regime (SPY/QQQ). These inputs are correlated; adding them does not create independent evidence.
3. Use a three-state decision (bull, bear, neutral/BIL) rather than automatically flipping 100% into inverse 2x/3x funds. Require full matched-date Composer tests.
4. For TSLA, avoid standalone bullish/short switching until new forward data validates. A small existing TSLQ bearish-sleeve allocation is already prominent and simpler than replacing core strategy.
5. For gold, prioritize exact original RSI3 oversold logic first. Limit/GDXD side using statistical events and credit/cost risk; don't assume rare RSI10>79 has a durable edge.
6. For high-ATR regimes cap **risk exposure** rather than selecting direction; monitor worst-day/gap/volatility drag.
7. If testing options, first obtain full chain/IV/greeks/tradeable quotes, not a crude delta or 2x ETF substitution.

## Recommended objective and protocol
**Prioritize evidence quality over retrospective annualized ROI**: candidate must improve paired same-date worst drawdown / risk-adjusted return after costs, survive 1- and 2-close execution alternatives, avoid large regressions in prior regimes, have meaningful sample counts, and then pass genuinely untouched forward paper testing.

The current user-selected 400%+ CAGR and <50% DD goal is an *in-sample screening criterion*, not a justified expectation of future performance. This research DOES NOT identify any proven >400% out-of-sample strategy.

## Living registry
See [beethoven_indicator_watchlist.json](beethoven_indicator_watchlist.json). Append new tickers, data periods and revisions in separate explicit research work. Do not edit main or live bots without specific authorization.
