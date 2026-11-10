# Beethoven Thematic — Independent, public research

**No broker access, no account keys, no LIVE/PAPER order submission, no scheduled automation.**

This is a **ticker adaptation** of the author-provided Beethoven 6.6 Composer source plus a **separate** ex-ante risk-control overlay. All **67 conditional rules**, **9 ranking filters**, weighting groups and numerical thresholds are retained in the unmodified ticker-mapped strategy. Risk overlay deliberately changes final weights to cap gross exposure and concentrate remaining capital in BIL.

## Versions
- `data/original.json`: original Beethoven source and original tickers (benchmark only).
- `data/role_v2.json`: prior branch's 55-to-52 role-aware map retaining 16 core stocks.
- `data/thematic_v3.json`: v3 ticker map, changing former GDXU/GDXD high-volatility pair to **FNGU/FNGD** (daily +3x/-3x FANG+ ETNs), and former AGQ silver slot to **LABU** biotech. Retains defense **DFEN/PTIR**, nuclear **URAA/BWXT/CEG**, robotics **ISUL**, quantum **IONL**, AI/semis, and original cash, duration, inverse and volatility defenses. This is a candidate, not a proven improvement.
- `catalog/thematic_v3.json`: explicit 55-position mapping and preserved signal-only overrides. Underlying signal symbols may be unleveraged; the portfolio can own core stocks as selected.

## Predeclared risk overlays (all closing-price data causal)
- `thematic_v3__original`: full original target exposure; no risk cap.
- `thematic_v3__half`: at most 50% in non-BIL assets, at most 40% in one, remainder BIL.
- `thematic_v3__regime_vol40`: SPY 200d trend gate; max 75% non-BIL in bull regime, 35% otherwise, per-name max 35%; historical 20d portfolio-volatility estimate limits predicted total volatility to 40% annualized, remainder BIL.
- `thematic_v3__regime_vol30`: identical except 30% volatility target.

These are **pre-specified hypothesis tests**, not evidence of future drawdown staying below 50%. Results must not be cherry-picked as a forward guarantee. Holding daily leveraged ETNs/ETFs entails compounding losses and (ETNs) issuer credit risk. BIL is a short Treasury ETF, not a bank deposit. SPY trend is a regime heuristic, not proven predictive.

## Research execution
Select **Actions → One-shot Beethoven research backtest (NO TRADING) → Run workflow**, or push research code to main. Runs are not scheduled. GitHub Actions public-repo runner billing is subject to GitHub's current policy.

Uses public Yahoo Finance dividend/split-adjusted daily close histories, 200 trading-day warmup, starts Nov 2024, Nov 2025, May 2026, Oct 2026 as available. Missing histories block an exact window rather than manufacture leveraged product history. Results logged in `evidence/summary.json` artifact, along with price histories and curves. A window with 10 valid days is an experiment, not convincing investment evidence.

**Critical caveat:** The Composer engine and rebalance fills are not independently parity-verified. Closing-to-next-closing simulation and turnover costs are not executable broker fills. Market-history survivorship, borrowing/shorting constraints, spreads, and exact transaction fees are not fully modeled. All variants are retrospective exploratory analyses; none is a true untouched out-of-sample test.

Do not enable LIVE or deploy any of this to A15 without a separately authorized, validated project.
