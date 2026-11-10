# 400% CAGR / below-50% max drawdown research target

**Status: target NOT met. No live trading authorization.** This is retrospective, optimized-in-sample research, not an independent strategy edge.

## Reproducible GitHub result
- [Completed GitHub Actions run](https://github.com/williamRut261/beethoven-thematic/actions/runs/42819593532)
- [Source and tests](src/grid_search.py)
- [Full grid and market-data artifact](https://github.com/williamRut261/beethoven-thematic/actions/runs/42819593532/artifacts/13766198532)

All **324 fixed parameter combinations** were tested on three role-matched Beethoven priority-pair branches: gold miners (GDXU/GDXD), semiconductors (SOXL/SOXS), and biotech (LABU/LABD). There were 108 risk overlays per branch: bull market exposure caps [0.65,0.85,1], bear market exposure caps [0.35,0.60,1], individual instrument caps [0.5,0.75,1], and annualized 20-day volatility targets [0.3,0.6,1.2,none].

All use a 200-day SPY regime indicator, signal observations through close t, assumed execution at the NEXT closing price t+1, and return recognition from t+1 to t+2. Transaction cost is 20 basis points of modeled one-way turnover. No broker orders or margin loans are used; leverage exists inside ETFs/ETNs.

## Best in-sample return with less than 50% modeled maximum drawdown

| Branch | Simulated CAGR | Simulated period return | Maximum drawdown | Configuration |
|---|---:|---:|---:|---|
| **Gold GDXU/GDXD** | **+251.09%** | **+248.39%** | **−49.79%** | Bull cap 65%; bear cap 100%; one-name cap 100%; no volatility cap |
| Semiconductor SOXL/SOXS | +96.16% | +95.35% | −45.87% | Same caps |
| Biotech LABU/LABD | +85.40% | +84.69% | −42.48% | Same caps |

**0/324 tested combinations achieved 400% or greater annualized return AND maximum drawdown strictly below 50%.** The best gold configuration exceeded the risk threshold only by 0.21 percentage points and is therefore fragile to execution differences and stress conditions.

Gold's best configuration returned approximately +85.23% in the first segment and +88.09% in the second. These are NOT validation periods because the original rules and pair selection were already evaluated against the full one-year span.

## Conservative reference

Prior **gold_gate + regime_vol30** research result with next-close execution and 20bps cost:
- Simulated period return +62.36%
- Simulated max drawdown −16.14%
- This candidate remains the previous lower-risk research hypothesis, not a LIVE configuration.

## Next scientific check

Do not keep tuning this same year and label the highest return as reliable. Before deployment:
1. Independent Composer-equivalence tests on allocation and indicator computations, and reproduce a range of actual daily decisions.
2. Investigate stale data, inception issues, adjusted close versus real executable orders, ETF/ETN spreads, slippage and reset/issuer risks.
3. Reserve future untouched forward data or a genuinely new historical market regime for walk-forward testing. An in-sample maximum drawdown of −49.79% does not meet a robust risk constraint; real losses could exceed 50%.
4. Evaluate which of GDXU/GDXD top-priority branches contributes to return versus drawdown.

**No accounts, A15, FSupertrend, LIVE trading services or orders were modified.**
