# Role-to-ticker experiments (frozen before backtesting)

The highest-priority GDXU/GDXD branches select one instrument at a time. Switching them changes the strategy's **market signal**, not just a component of a conventional portfolio. Use matched daily leveraged bull/bear products and do not replace cash or long-duration Treasury holdings with high-volatility growth stocks.

| Beethoven branch | Original | Thematically suitable instrument or control | Why |
|---|---|---|---|
| Top overbought RSI10 >79 and short-term RSI3 <30 | GDXU/GDXD | **GDXU/GDXD** retained for highest fidelity | Thresholds originally calibrated to gold miners |
| Equivalent momentum/mean reversion test, AI semiconductors | GDXU/GDXD | SOXL/SOXS | Matched daily +3x/-3x semiconductor index; technology theme |
| Equivalent momentum/mean reversion test, biotech | GDXU/GDXD | LABU/LABD | Matched daily +3x/-3x biotech industry; biotechnology theme |
| Equivalent technology basket test | GDXU/GDXD | FNGU/FNGD | Matched daily +3x/-3x FANG+ exposure, but ETN issuer credit risk |
| Commodity/metal momentum candidate | AGQ | AGQ (precious metals) or URAA (uranium) | Separate experimental branch; not a matched inverse pair |
| Macro bear/volatility protection | BIL, BTAL, TLT, TMF, UVXY | Same original instruments | These are distinct hedge/duration/cash roles |
| Nasdaq trend/inverse | TQQQ/SQQQ | Same original instruments | Preserve daily triple exposure and matched benchmark |
| Broad equity / inverse | SPXL/UPRO and related | SPXL/SPXS (theme-wide core ranking); UPRO intact | Crossover applies to broad basket, not a single AI stock |
| Technology bull/inverse | TECL/TECS | SOXL/SOXS | Semiconductors +3x/-3x, but narrower than technology |
| Defense, nuclear, AI, robotics and long-term stock candidate pool | Various leveraged stocks / quality stocks | DFEN, PTIR, URAA, OKLL, NVDL, AMDL, AVGU, ISUL, IONL and 16 core blue-chip/defense/medical stocks | A distinct ranked universe; not used to replace risk-off products |

Source: original Beethoven Composer JSON `data/original.json`, mapping in `catalog/thematic_v3.json`. Issuer evidence: [MicroSectors GDXU/GDXD](https://microsectors.com/goldminers/), [Direxion SOXL/SOXS](https://www.direxion.com/product/daily-semiconductor-bull-bear-3x-etfs). Other pairs and availability require separate listing/issuer validation. The original rank windows, node orders and thresholds are unchanged in these experiments.

## Precommitted variants

`src/candidates.py` defines the only role substitutions. `gold_gate` retains the source GDXU/GDXD +3x/-3x pair while keeping nuclear URAA in the AGQ candidate slot. `gold_precious` further restores the original AGQ silver exposure. `semis_gate` uses SOXL/SOXS in the priority pair; `biotech_gate` reproduces V2; `fang_gate` reproduces the top pair from V3 (but preserves V2's uranium AGQ slot).

All variants use the previously chosen 30% trailing annualized volatility target overlay as one **separate** comparison, leaving all formula thresholds and branch structure unchanged. These are retrospective exploratory comparisons, not out-of-sample confirmation of superior future returns. New symbols can prevent earlier backtests. No synthetic pre-inception prices are allowed. No real orders or credentials.
