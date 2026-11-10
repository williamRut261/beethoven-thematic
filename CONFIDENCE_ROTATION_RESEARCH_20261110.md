# Beethoven confidence-rotation research — 10 November 2026

## Decision
**Best next Composer research candidate:** `strategies/beethoven_hybrid_confidence_relative20_200.json`. This is **not** a verified superior strategy or an expected-return forecast. The current Composer-tested #1 hybrid remains the reference; no live changes.

## Critical comparability correction
- User Composer export for current SOXL/SOXS+TSLQ #1: 280 trading days, **2025-09-30 to 2026-11-09**, screenshot **503.8% CAGR / -41.9% max drawdown / 2.29 Sharpe**.
- User Composer exports for PTIR/DFEN fixed rotation and PTIR/DFEN momentum: 375 trading days, **2025-05-14 to 2026-11-09**. Screenshots: **368.7% / -35.4%** and **376.6% / -36.8%**, respectively.
- The old and new Composer figures MUST NOT be compared as causal evidence when calendar windows are different. On overlapping 280 days, reverse-combining SOXL+PTIR/DFEN from the fixed rotation reproduces all original #1 target weights exactly. This is reproducible from provided allocation CSVs.

## Research data and method
- Inputs: user-uploaded three Composer daily-allocation CSVs; adjusted historical daily closes `public_closes.csv` from existing GitHub Actions evidence artifact 13766198532; independently sourced TSLQ adjusted price series from Massive market-data aggregates. Daily prices are not trade quotes.
- Close_t allocation held for close_t→close_t+1 returns, 1bp per unit of modeled weight turnover, no broker execution. Composer's daily backtest is proprietary and not exactly reproduced; daily rebalancing realized in the last 15 minutes can differ. Model uses target-weight turnover and does not fully model drifted positions, spreads, partial orders, interest/margin, taxes, delayed fills.
- Training diagnostic May 14 2025–Mar 31 2026; later diagnostic Apr 1–Nov 9 2026. **Not independent forward OOS**: this date span was repeatedly inspected and optimized in prior exchanges.

## Date-matched reconstruction
| Strategy | Window | Reconstructed CAGR @ 1bp | Max DD | CAGR @ 20bps |
|---|---|---:|---:|---:|
| Original #1 SOXL/SOXS+TSLQ baseline | 375 days | +340.3% | -42.0% | +264.4% |
| PTIR down 30% / DFEN up 10%, fixed | 375 days | +372.7% | -35.4% | +290.6% |
| Top 20-day momentum PTIR vs DFEN in down regime | 375 days | +380.8% | -36.8% | +296.6% |
| **Proposed confidence filter: rotate only when PTIR/DFEN 20-day cumulative return > SOXL** | 375 days | **+401.8%** | **-36.8%** | **+312.8%** |
| Original #1 baseline | overlapping 280 days | +514.9% | -42.0% | +403.4% |
| Fixed rotation | overlapping 280 days | +584.3% | -35.4% | +458.2% |
| Proposed confidence | overlapping 280 days | +644.3% | -36.8% | See full-period figures |

**Qualification:** The proposed 401.8% at 1bp was computed using original daily allocation targets with a causal hypothetical rotation overlay; the committed JSON differs from original on a handful of dormant filter alternatives pruned to fit Composer. It has not been independently backtested inside Composer; 401.8% is not an exact strategy result. It barely passes the 400% target even in this optimistic model.

### Causal trade-timing stress
- If all target portfolios execute **one full closing session later**, with modeled 20bps turnover cost, proposed confidence strategy's reconstructed full-period CAGR drops to about **+72.2%**, DD -44.5%. Fixed-rotation reference about +66.3%, DD -42.6%.
- This one-session delay is a deliberately harsh alternative assumption, *not* Composer's actual default execution. Composer uses a late-afternoon execution window. See https://help.composer.trade/article/63-trading-period .
- 10bps costs full period: proposed **+357.5% / -37.2%**; fixed rotation **+331.9% / -35.9%**.
- Illustrative 1,000-path 10-trading-day block bootstrap on modeled daily returns with 10bps costs: about **29.5%** of proposed-strategy resampled paths reached a >50% drawdown. This is NOT a calibrated forecast probability.

## Ticker-specific indicator research (33 symbols, 10 predeclared daily indicator families)
Price-derived signals are through daily close t, evaluated against the close_t→close_t+1 return. Report below uses **train / later diagnostic**, in basis points *difference* between next-day average return when signal true vs false. These are descriptive and mostly not statistically significant, with inter-ticker correlation and repeated testing.

| Security | Candidate and earlier/later conditional difference | Interpretation |
|---|---|---|
| SOXL | Following 5-day negative return +16 / +73 bps | Short-term reversal possible; longer-trend signs flipped |
| SOXS | Following 5-day negative return +12 / +158 bps | Short-term reversal but high inverse ETF risk |
| TSLA | 5-day negative return +48 / -22 bps | Unstable: cannot claim a useful daily timing signal |
| PTIR | 5-day negative return +1 / +121 bps | Possible but sample and regime dependence |
| DFEN | Price above 20d SMA +53 / -77 bps | Trend rule reversed; reject as stable classifier |
| NVDL | 5-day negative return +57 / +4 bps | Weaker later edge |
| NVDA | 5-day negative return +17 / +9 bps | Small consistent reversal, much less upside leverage |
| LMT | Positive 20d return +26 / +41 bps | Modest consistent signal, but historically low growth versus SOXL |
| IONL | 5-day negative return +126 / -320 bps | Extreme sign reversal; reject |
| URAA | Below-median rolling vol +44 / +32 bps | Small consistency but not enough to replace core |
| META | 5-day negative return +25 / -40 bps | Unstable |
| QQQ | 5-day negative return +13 / +5 bps | Small consistency |

Across 32 tickers evaluated for 5-day negative-return signal, 23 had positive conditional next-day differences in both chronological segments. This is *not* 23 independent proofs due to correlated stocks, selection and shared market regimes.

## VWAP diagnostic (Massive adjusted daily OHLCV, signal at end of day, next-day returns)
Composer documented IF/ELSE block indicators currently do NOT include VWAP: https://www.composer.trade/learn/how-composer-symphonies-work .
Daily cross below VWAP of the daily bar is NOT the same as an intraday session VWAP crossing trade signal. Available sample daily bars Sep 2025 and later:

- TSLA: **54** train downward-cross days, average next session TSLA return **-0.009%**; **39** later downward-cross days **-0.234%**. Too weak to justify TSLA inverse trading solely on VWAP.
- PTIR below VWAP: next-session mean **+0.563%** early / **+1.235%** later; above VWAP next-session mean **-0.176% / -0.581%**. This is contrarian, not clear trend continuation.
- SOXL below VWAP: following-session mean **+1.341% / +1.944%**, above VWAP **+0.157% / -0.322%**. Contrary to blanket bearish-below-VWAP interpretation.
- TSLQ cross signals changed direction across segments. Bear-score family tests (10 TSLA/TSLQ/SOXS conditions) did not produce stable reliable evidence for changing the SOXS/TSLQ ratio; preserve pair rather than data-mine it.

## Composer candidate construction
- Base: working 199-node fixed PTIR/DFEN hybrid on `research/composer-hybrid-rotation-20261110`.
- **Preserves**: SOXL/SOXS/TSLQ risk weights, all 35 surviving high-priority decision conditions, the seven SMA100 guards, all 9 named original filter mechanisms, and BIL defensive limits.
- **Adds**: Six 20-trading-day cumulative-return **TOP 1** filters inside 18% PTIR and 9% DFEN allocation sleeves: winner between PTIR and SOXL (in downside-trend branch), or winner between DFEN and SOXL (in upside-trend branch).
- **Prunes to fit 200 nodes**: NVDL high-volatility alternative sub-branch (including one low-priority IF), NVDL and IONL from one 15-day momentum list, IONL from two others, BWXT and CEG from one rarely chosen defensive/nuclear list. These candidates had zero portfolio holdings in provided 375-day export, but future changes in selection behavior are possible.
- Output: **200 Composer-counted nodes, 35 IF decision containers, 15 filters, 95 asset occurrences, 235 structural nodes**. File read back from GitHub; JSON parses, all specified weights sum to 100%, all IDs unique, all nine top-level filter rules preserved, and bearish pair allocations preserved. No Composer import/backtest confirmation.

## Recommended next verification
1. Import JSON and run **both** original May 14 2025–Nov 9 2026 and matching Sep 30 2025–Nov 9 2026 windows at the same 1bp cost. Do not compare different periods.
2. Repeat 10bps/20bps costs; compare the new confidence candidate with untouched 199-node original and fixed 199-node regime variant.
3. Analyze conditional fill and signal timing in Composer's 3:45–4 PM ET trading period; daily-close backtests may diverge significantly.
4. Reserve genuinely new paper data before selecting the strategy for live deployment. Evaluate drawdowns under unseen large gaps, ETF daily resets, financing/issuer risk, liquidity and trading fees. No LIVE orders or modifications.

Key official sources:
- https://help.composer.trade/article/67-backtest-basics
- https://www.composer.trade/learn/how-composer-symphonies-work
- https://help.composer.trade/article/63-trading-period
- https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-alerts/sec
