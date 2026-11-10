# Beethoven 6.6 — semiconductor priority pair (SOXL / SOXS)

- **[Full Composer-style strategy JSON](beethoven_6_6_semis_gate.json)** — ticker-mapped original tree, preserving **67 conditional nodes, 9 ranking filters, 177 asset leaves**. Top original GDXU bullish/gold signal replaced by SOXL; top GDXD inverse replaced by SOXS, including the later GDXU lookback indicators. The other original tickers use the existing thematic V2 mapping.
- **[Backtest allocation settings JSON](semis_gate_backtest_config.json)** — separate risk controls that were applied by the Python simulator. Those controls are **NOT encoded in the Composer strategy JSON** and cannot be assumed to transfer through Composer import.
- **[Backtest evidence](https://github.com/williamRut261/beethoven-thematic/actions/runs/42819593532)** — 96.16% simulated annualized return with −45.87% simulated maximum drawdown under next-day closing-price execution and 20bps per unit of modeled turnover (Nov 2025–Nov 2026). In-sample and not independent parity verified.

**No live orders or brokerage connections.** This is a research strategy; the plain strategy JSON without the Python allocation overlay does not correspond to the displayed backtest performance.
