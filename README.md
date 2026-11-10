# Beethoven Thematic — Independent, public research

## Current leading hypothesis — GDXU/GDXD gate + 30% volatility cap (NOT DEPLOYED)

**Research-only, selected after seeing the 2025–2026 sample.** Restoring the original **GDXU/GDXD +3x/−3x gold-miner pair** in Beethoven's top-priority RSI and trend branches preserved the source's strongest decision logic. Other 55-slot replacements are inherited from role-based V2 (including defense, nuclear, AI, robotics and 16 core stocks); unused risk exposure is allocated to BIL.

| Top-priority bull/bear pair | Same-close 1-year simulated return | Same-close maximum drawdown |
|---|---:|---:|
| **Gold miners GDXU/GDXD +3x/−3x** | **+247.75%** | **−14.61%** |
| Semiconductors SOXL/SOXS +3x/−3x | +83.68% | −16.96% |
| Biotech LABU/LABD +3x/−3x (prior V2) | +52.86% | −22.22% |
| FANG+ FNGU/FNGD +3x/−3x | −11.91% | −27.51% |

The same-close results assume a price-sensitive signal at close `t` earns the return starting at that same close, which may not be executable. **Execution-delay sensitivity**, with signals computed at close `t`, entry at close `t+1`, returns earned thereafter:

| Priority pair + 30% volatility cap | Next-close / 5bps return (DD) | Next-close / 20bps return (DD) |
|---|---:|---:|
| **GDXU/GDXD** | **+76.92% (−15.25%)** | **+62.36% (−16.14%)** |
| SOXL/SOXS | +33.70% (−16.40%) | +24.61% (−17.10%) |
| LABU/LABD | +36.67% (−21.28%) | +26.21% (−22.09%) |
| FNGU/FNGD | −7.68% (−20.30%) | −15.09% (−22.85%) |

Tests cover 250 trading-day observations from November 11, 2025 through November 9, 2026 using Yahoo Finance adjusted daily prices, simplified turnover costs and the research-only Composer interpreter. No Composer parity, real fills, precise spreads, market impact, portfolio tax effects, issuer ETN credit risks or independent out-of-sample edge has been verified. **The results were selected after inspecting the same sample; they are not forecasts.** A drawdown below 50% in this sample cannot guarantee a future drawdown limit.

- [Source-to-role mapping and predeclared hypotheses](ROLE_MAPPING.md)
- [Successful run and detailed logs](https://github.com/williamRut261/beethoven-thematic/actions/runs/42817613459)
- [Archived price data, curves, window results, execution sensitivity](https://github.com/williamRut261/beethoven-thematic/actions/runs/42817613459/artifacts/13764807233)
- [Research selection metadata](RESEARCH_SELECTION.json) — does not authorize trading.


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


See [role-to-ticker hypotheses](ROLE_MAPPING.md). The reproducible job compares gold, semiconductor, biotech, and FANG+ priority-pair branches on identical historical periods. Any selector based on these returns is in-sample only.

## Execution-timing and cost sensitivity

The historical daily-close backtests assume signals calculated at close `t` can earn the move from close `t` to `t+1`. This is generally **not an executable fill assumption** without an advance order. A second, delayed test calculates the signal at close `t`, assumes execution at the **next day's closing price `t+1`**, and realizes returns starting `t+1→t+2`. It tests 5- and 20-basis-point turnover costs over the same one-year period for the matched priority-pair candidates. Neither test includes real bid-ask fills, spread, market impact or slippage, and a next-close order can still differ from live execution.

The delayed test is a sensitivity check, not proof of profitability or a substitute for market-open/executable quote data. Future out-of-sample validation is still required.
