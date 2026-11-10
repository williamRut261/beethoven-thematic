"""Static, causal research risk controls. Only allocates to traded leveraged assets and BIL."""
import math
import numpy as np
import pandas as pd

def hedge_portfolio(raw, closes, style):
    """Returns fully invested weights. Uses ONLY data through signal close t."""
    if style == "original":
        return dict(raw)
    if style not in {"half", "regime_vol40", "regime_vol30"}:
        raise ValueError("Unknown risk style: "+style)
    if "BIL" not in closes:
        raise ValueError("BIL cash-proxy series is necessary")
    risky={s:float(w) for s,w in raw.items() if s!="BIL" and w>0}
    exposure=sum(risky.values())
    if exposure<1e-12:
        return {"BIL":1.0}
    if style=="half":
        cap=0.50
        target_vol=None
        per_name_cap=0.40
    else:
        if "SPY" not in closes:
            raise ValueError("SPY trend proxy is necessary")
        spy=closes["SPY"].iloc[-200:]
        if len(spy)<200 or spy.isna().any() or spy.iloc[-1]<=0:
            raise ValueError("Missing SPY trend history")
        bull=float(spy.iloc[-1])>float(spy.mean())
        cap=0.75 if bull else 0.35
        per_name_cap=0.35
        target_vol=0.40 if style=="regime_vol40" else 0.30
    scale=min(1.0,cap/exposure)
    if target_vol is not None:
        cols=sorted(risky)
        if len(closes)<22 or any(s not in closes for s in cols):
            raise ValueError("Missing volatility history")
        ratios=closes[cols].iloc[-21:].pct_change().iloc[1:]
        if ratios.isna().any().any() or not np.isfinite(ratios.to_numpy()).all():
            raise ValueError("Volatility estimate has missing data")
        port=ratios.to_numpy(dtype=float)@np.array([risky[s] for s in cols])
        vol=float(port.std(ddof=1)*math.sqrt(252))
        if vol>0:
            scale=min(scale,target_vol/vol)
    # Cap risk from any one held leveraged instrument, surplus moves to BIL.
    mapped={s:min(w*scale,per_name_cap) for s,w in risky.items()}
    risky_sum=sum(mapped.values())
    if risky_sum>1.00000001:
        raise ValueError("Risk overlay has gross >100%")
    mapped["BIL"]=max(0.0,1.0-risky_sum)
    if not math.isclose(sum(mapped.values()),1.0,abs_tol=1e-8):
        raise ValueError("Risk overlay failed to sum to 1")
    return mapped
