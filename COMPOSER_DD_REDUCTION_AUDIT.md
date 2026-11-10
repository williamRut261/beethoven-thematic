# Beethoven Composer drawdown reduction — experimental analysis (2026-11-10)

## Inputs and scope
- Composer user-exported **daily allocations**, 375 trading days, 2025-05-14 through 2026-11-09; user screenshot window 2025-09-30 through 2026-11-09.
- Public adjusted historical price data from existing repository GitHub Action artifact `13766198532` (`public_closes.csv`). This is *not* Composer's proprietary price feed.
- Original Composer screenshot: **461.9% annualized**, **-57.4% maximum drawdown**, 1bps slippage, date window 2025-09-30 through 2026-11-09.
- Reconstructed baseline by using position weights reported at close t for next session close-to-close return t→t+1, approximately 1bp modeled one-way turnover cost: **480.38% CAGR, -57.41% MDD**, period return **602.80%**. Matching MDD is meaningful but the return mismatch shows reconstruction is *not* Composer-exact.

## Concentration and losses
- 354/375 (94.4%) historical allocation days include a SOXL or SOXS position; 348/375 (92.8%) days have one 100%-weight asset.
- Worst baseline drawdown: July 22 through October 16, 2026; approx. **-57.41%** in reconstructed equity. In this peak-to-trough period, SOXL dominated the negative returns.
- Worst reconstructed daily move: approximately **-38.7%** on November 5, 2026. Leveraged exposure and daily-reset decay are material. A static 400% CAGR target is not a defensible future projection.

## Limited policy comparisons (same screenshot-window prices)
| Risk rule applied only when selected holding is SOXL or SOXS | Modeled CAGR | Modeled MDD | Worst modeled day |
|---|---:|---:|---:|
| Original exported allocations | +480.38% | -57.41% | -38.72% |
| SOXL 85%, SOXS 75%, remainder BIL | +410.97% | -49.12% | -32.91% |
| SOXL 80%, SOXS 80%, remainder BIL | +394.20% | -47.38% | -30.97% |
| SOXL 85%, SOXS 80%, remainder BTAL | +412.78% | -48.61% | -32.30% |
| **If SOXL close below SOXL SMA100 → 60% selected SOXL/SOXS + 40% BIL; else → 90% selected SOXL/SOXS + 10% BIL** | **+460.52%** | **-48.05%** | **-23.23%** |

The dynamic policy was selected after exploring multiple regimes, windows, and exposure levels, and is **in-sample optimized**. A nearby 50-day SMA policy with 90%/60% caps returned ~380.2% CAGR / -48.1% DD; a 200-day policy gave ~355.6% CAGR / -56.1% DD. This parameter sensitivity is a major robustness warning.

In a secondary, earlier 2025-05-15 through 2025-09-29 window:
- Baseline reconstructed annualized +10.9%, MDD -42.6%.
- Static 85/75 BIL: annualized +19.6%, MDD -34.8%.
- Dynamic SMA100 90/60: annualized +20.1%, MDD -37.4%.
This is only a **retrospective check**, not an untouched future validation period.

Dynamic SMA100 90/60 slippage-cost sensitivity over screenshot window:
| Cost per unit of modeled one-way turnover | Modeled CAGR | MDD |
|---|---:|---:|
| 1bp | 460.52% | -48.05% |
| 5bps | 449.02% | -48.14% |
| 10bps | 434.98% | -48.24% |
| 20bps | 407.94% | -48.45% |

## Import candidates (research-only)
- [Adaptive SMA100 90/60 BIL, 191 counted nodes](strategies/beethoven_6_6_semis_dd_sma100_90_60_bil_191.json).
- [Static 85/75 BIL, 193 counted nodes](strategies/beethoven_6_6_semis_dd_soxl85_soxs75_bil_193.json).
- [Static 80/80 BIL, 193 counted nodes](strategies/beethoven_6_6_semis_dd_soxl80_soxs80_bil_193.json).
- [Static 85/80 BTAL, 193 counted nodes](strategies/beethoven_6_6_semis_dd_soxl85_soxs80_btal_193.json).

Changes: preserve all 29 existing conditions and nine ranking filters of the previous 194-node compact strategy; collapse mathematically redundant single-child equal-weight blocks (15 for static; 52 for adaptive) and apply risk-specific weighted holdings. Existing 434-node Composer JSON and original 194-node compact file are **unchanged**. Both specified-weight sums and unique IDs were checked; **Composer import, exact allocation parity, and new platform backtests are NOT independently confirmed**.

## Proper next test
1. Import each candidate into Composer and set *identical* screenshot-window dates, 1bp slippage and fees. Record actual Composer CAGR / DD and inspect historical allocations for 60/90 split on days when SOXL is below/above its 100-day SMA.
2. Test with 10-20bp slippage, several years / alternative market regimes if inception dates permit, and check extreme single-day losses.
3. Do not further optimize those same dates and call the result OOS. Hold a future untouched paper period, and reject policies that only succeed for narrow moving-average windows.
4. No broker connections, orders, or live configurations were modified.
