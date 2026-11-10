# Beethoven #1 — ticker rotation research (2026-11-10)

**Status:** Research variants, not Composer-verified. Original 434-node strategy and the winning 199-node SOXL/SOXS+TSLQ hybrid are unchanged. No live trading or broker operations.

## Baseline / source data
- Source: Composer-exported allocation history `Beethoven Hybrid | SOXL_SOXS + TSLQ 50% of bearish sleeve.csv` uploaded by the user: 280 allocations, 2025-09-30 through 2026-11-09.
- Existing public price-history evidence from GitHub Actions artifact `13766198532`, `public_closes.csv`. For TSLQ, historical daily closes retrieved from Massive's adjusted OHLC stock API. No price series was synthetically extended before an ETF launch.
- Composer #1 screenshot: **503.8% annualized return**, **−41.9% max drawdown**, Sharpe 2.29, annualized standard deviation 101.3%.
- Independently reconstructed base with allocation weights as of close t, earned return to close t+1, 1 basis point modeled turnover cost: **506.39% CAGR**, **−41.97% max drawdown**. Small mismatch due to model/price/execution differences; do not report the reconstructed results as Composer results.

**Important concentration:** SOXL on **188/280** allocation days; SOXS+TSLQ on **77/280**; other holdings on **15/280**. The 94.6% core-pair presence means simply rotating the rare lower-ranking stock selections will have little effect. The core risk is SOXL exposure in the bullish sleeve: the baseline reconstruction peaked July 22 and bottomed November 5, 2026 (about −42%). Over that interval SOXL was held on 61 of 75 days.

## Research logic

Preserve ALL existing priority decision conditions (36 IF nodes including seven SOXL-SMA100 guards), the bearish risk sleeve (SOXS/TSLQ split 50/50 within risky exposure, with remaining BIL), and the original priority hierarchy.

The selected rotations use the **existing** SOXL vs. 100-day moving-average state:
1. **Regime / fixed sector rotation (recommended first Composer test)**:
   - SOXL below its SMA100: 42% SOXL + 18% PTIR + 40% BIL (the former 60% SOXL exposure contributes 30% to PTIR).
   - Otherwise: 81% SOXL + 9% DFEN + 10% BIL (the former 90% SOXL exposure contributes 10% to DFEN).
   - SOXS+TSLQ/BIL unchanged.
   - Exactly **199 Composer-counted nodes**; all nine original filters preserved, six algebraically redundant single-child equal-weight wrappers folded.
2. **20-day momentum alternative**:
   - SOXL below its SMA100: 42% SOXL + 18% ranked top-one PTIR/DFEN by 20-day *average daily return* + 40% BIL.
   - Above its SMA100: original 90% SOXL + 10% BIL unchanged.
   - SOXS+TSLQ/BIL unchanged.
   - Exactly **200 Composer-counted nodes**; original nine filters retained plus three new ranking filters. Two unused nuclear filter candidates (BWXT, CEG) were removed to stay within 200 nodes. They weren't held in the uploaded allocation period but may matter in other regimes.

## Retrospective reconstruction — do not extrapolate

| Strategy | Reconstructed CAGR @ 1bp | MDD @ 1bp | CAGR @ 20bps turnover | MDD @ 20bps |
|---|---:|---:|---:|---:|
| Current #1 baseline | +506.39% | −41.97% | +392.78% | −43.93% |
| Regime: PTIR 30% down, DFEN 10% up | **+574.23%** | **−35.43%** | **+445.28%** | −36.39% |
| 20-day momentum: down-state PTIR/DFEN, 30% | +571.06% | −36.78% | +442.70% | −37.73% |

The modeled prices/holdings were one day apart, with signals computed through the allocation date. This does NOT prove that a signal known at the close could be executed at that same closing print. The original strategy's Composer methodology may differ. No out-of-sample period was reserved; these were chosen after extensive same-window exploration and are vulnerable to overfitting, regime dependence, leverage resets, and transaction-cost misspecification.

## Results by subperiod (1bp, reconstructed)

| Period | Baseline return / MDD | Regime return / MDD | Momentum return / MDD |
|---|---|---|---|
| 2025-09-30 to 2026-03-30 | +25.90% / −30.2% | +29.13% / −28.83% | +23.39% / −31.8% |
| 2026-03-30 to 2026-11-09 | +485.99% / −41.97% | +542.61% / −35.43% | +568.99% / −36.78% |
| July 22 to Nov 9, 2026 | −29.3% / −42.0% | −9.69% / −28.75% | −15.09% / −31.54% |

Subperiods are descriptive, not unseen test samples.

## Ready-to-import research JSON

- [Regime PTIR/DFEN, 199 nodes](strategies/beethoven_hybrid_199_regime_ptir30_dfen10.json)
- [20-day momentum PTIR/DFEN, 200 nodes](strategies/beethoven_hybrid_200_momentum_ptir_dfen.json)

Both JSONs were parsed after being read back from GitHub, checked for unique IDs and all specified weights adding to 100%, and checked against the current #1 base to ensure the **SOXS/TSLQ pair weights and all original decision-condition parameters are identical**.

## Further verification

1. Import **regime** candidate in Composer and check actual allocations on days SOXL is below/above its SMA100, then backtest identical 2025-09-30 to 2026-11-09 dates, fees/slippage. Record CAGR/DD/Sharpe.
2. Repeat with **momentum** candidate and verify the added top-one ranking chooses PTIR versus DFEN according to historical moving-average-return indicators.
3. Test higher slippage, longer periods and untouched forward paper data. Leverage concentration, stale or incorrect prices, overnight gaps and real fills can cause losses far beyond observed MDD.
4. No strategies are authorized for live trading by these research results.
