"""No future-price signal leakage, no margin from the overlay, and reproducible grid."""
import numpy as np
import pandas as pd
import pytest
from src.grid_search import Config,configs,allocation,simulate,metrics,prepare

def test_fixed_grid_has_expected_size_and_no_posthoc_dynamic_tuning():
    assert len(configs())==3*3*3*4
    assert len({x.id() for x in configs()})==len(configs())
    assert len(configs())==108

def test_allocation_respects_risk_budget():
    row={"risky":{"GDXU":1.0},"bull":True,"vol":0.5}
    for cap in configs():
        w=allocation(row,cap)
        assert 0<=w["GDXU"]<=cap.per_name+1e-10
        assert w["GDXU"]<=cap.bull+1e-10
        assert abs(sum(w.values())-1)<1e-10
    assert allocation(row,Config(1,1,1,None))["GDXU"]==1.0

def test_max_drawdown_includes_starting_capital():
    dates=pd.bdate_range("2026-01-01",periods=3)
    stats=metrics([1.0,0.2,0.5],dates)
    assert stats["max_dd_pct"]==-80.0

def test_signal_uses_only_t_data_not_future_t1_t2():
    dates=pd.bdate_range("2024-01-02",periods=206)
    f=lambda x: np.full(206,x,dtype=float)
    prices=pd.DataFrame({"SPY":f(100),"BIL":f(100),"X":f(100)},index=dates)
    root={"step":"root","children":[{"step":"if","children":[
        {"step":"if-child","lhs-val":"X","lhs-fn":"current-price","lhs-fn-params":{},"rhs-fixed-value?":True,"rhs-val":"110","comparator":"gt","children":[{"step":"asset","ticker":"X"}]},
        {"step":"if-child","is-else-condition?":True,"children":[{"step":"asset","ticker":"BIL"}]}
    ]}]}
    before=prepare(root,prices,start=str(dates[200].date()))
    changed=prices.copy()
    changed.loc[dates[-1],"X"]=1000.
    after=prepare(root,changed,start=str(dates[200].date()))
    assert before[0]["raw"]==after[0]["raw"]
    assert before[0]["signals_asof"]==after[0]["signals_asof"]
    assert before[0]["signals_asof"]<before[0]["date"]

def test_delayed_price_jump_yields_zero_if_exit_price_reverts():
    dates=pd.bdate_range("2025-01-02",periods=4)
    rows=[{"date":dates[i],"signals_asof":dates[i-2] if i>1 else dates[0],
           "risky":{"X":1.},"bull":True,"vol":0.1,"returns":{"X":1.0,"BIL":1.0}} for i in range(1,4)]
    result=simulate(rows,Config(1,1,1,None),bps=0)
    assert result["whole"]["return_pct"]==0.0
