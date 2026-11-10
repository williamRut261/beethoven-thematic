"""Research invariants: strategy structure, no leverage borrowing, causal overlay and drawdown baseline."""
import json, numpy as np, pandas as pd
from pathlib import Path
from src.engine import walk,Evaluator
from src.overlay import hedge_portfolio
from src.research import backtest
P=Path(__file__).resolve().parents[1]
old=json.loads((P/"data/original.json").read_text())
role=json.loads((P/"data/role_v2.json").read_text())
v3=json.loads((P/"data/thematic_v3.json").read_text())
cat=json.loads((P/"catalog/thematic_v3.json").read_text())
def shape(n):
    ignored={"ticker","name","exchange","lhs-val","rhs-val","price","dollarVolume","hasMarketcap"}
    return {k:([shape(c) for c in v] if k=="children" else v) for k,v in n.items() if k not in ignored}
def test_source_tree_identical_except_tickers():
    assert shape(old)==shape(role)==shape(v3)
    for r in (old,role,v3):
        counts={step:sum(n["step"]==step for n in walk(r)) for step in ("if","filter","asset")}
        assert counts=={"if":67,"filter":9,"asset":177}
def test_roles_and_55_symbol_coverage():
    oldHold={n["ticker"] for n in walk(old) if n["step"]=="asset"}
    assert len(oldHold)==55 and set(cat["mapping"])==oldHold
    assert cat["mapping"]["GDXU"]=="FNGU" and cat["mapping"]["GDXD"]=="FNGD"
    assert cat["mapping"]["AGQ"]=="LABU"
    for s in ("BIL","BTAL","TLT","TMF","UVXY","PSQ","SQQQ","SRTY","WEBS"):
        assert cat["mapping"][s]==s
def test_risk_overlay_funds_bil_no_hidden_margin():
    frame=pd.DataFrame({"SPY":[100+.1*i for i in range(250)],
       "NVDL":[100+.2*i for i in range(250)],"LABU":[100+.3*i for i in range(250)],"BIL":[100+.001*i for i in range(250)]},
       index=pd.bdate_range("2025-01-01",periods=250))
    for style in ("half","regime_vol40","regime_vol30"):
        weights=hedge_portfolio({"NVDL":.75,"LABU":.25},frame,style)
        assert 0<=weights["BIL"]<=1
        assert sum(w for s,w in weights.items() if s!="BIL") <= (.50 if style=="half" else .75)+1e-9
        assert max(weights.values())<=1
        assert abs(sum(weights.values())-1)<1e-10
def test_early_drawdown_includes_initial_equity():
    root={"step":"root","children":[{"step":"asset","ticker":"X"}]}
    dates=pd.bdate_range("2024-01-01",periods=225)
    series=[100.0]*201+[20.0]*24
    frame=pd.DataFrame({"X":series,"BIL":[100.0]*225,"SPY":[100.0]*225},index=dates)
    result,_=backtest(root,frame,dates[200],"original",0)
    assert result["max_drawdown_pct"]<=-79.9

from src.candidates import generate,BASE,CANDIDATES,ROLES,transform

def test_source_baseline_can_be_exactly_recreated():
    rebuilt=transform(old,BASE)
    assert rebuilt==role
    assert len(CANDIDATES)==5

def test_every_role_variant_has_identical_logic_and_directional_bull_bear_pair():
    matched=generate()
    pairs={
        "gold_gate":("GDXU","GDXD"),
        "gold_precious":("GDXU","GDXD"),
        "semis_gate":("SOXL","SOXS"),
        "biotech_gate":("LABU","LABD"),
        "fang_gate":("FNGU","FNGD"),
    }
    for name,(tree,mapping) in matched.items():
        assert shape(old)==shape(tree)
        assert (mapping["GDXU"], mapping["GDXD"]) == pairs[name]
        held={n["ticker"] for n in walk(tree) if n["step"]=="asset"}
        assert len(held)>=40
        assert (mapping["BIL"],mapping["BTAL"],mapping["TLT"],mapping["UVXY"])==("BIL","BTAL","TLT","UVXY")
        assert len([n for n in walk(tree) if n["step"]=="if"])==67
        assert len([n for n in walk(tree) if n["step"]=="filter"])==9
    assert matched["gold_precious"][1]["AGQ"]=="AGQ"
    assert matched["gold_gate"][1]["AGQ"]=="URAA"

def test_top_tier_gold_gate_preserves_original_gold_rsi_thresholds():
    gold=generate()["gold_gate"][0]
    def top(tree):
        return tree["children"][0]["children"][0]
    for new,src in zip(top(gold)["children"],top(old)["children"]):
        if not new.get("is-else-condition?"):
            assert new["lhs-val"]==src["lhs-val"]=="GDXU"
            assert new["rhs-val"]==src["rhs-val"]=="79"
            assert new["lhs-fn-params"]==src["lhs-fn-params"]

def test_delay_prevents_same_close_signal_fill_on_overnight_jump():
    root={"step":"root","children":[{"step":"asset","ticker":"X"}]}
    dates=pd.bdate_range("2025-01-02",periods=220)
    arr=np.full(220,100.0)
    arr[201:]=150.0
    df=pd.DataFrame({"X":arr, "SPY":np.full(220,100.0), "BIL":np.full(220,100.0)},index=dates)
    immediate,_=backtest(root,df,dates[200],"original",0,execution_delay_days=0)
    delayed,_=backtest(root,df,dates[200],"original",0,execution_delay_days=1)
    assert immediate["period_return_pct"] > 49.9
    assert delayed["period_return_pct"] == 0.0
    assert delayed["execution_delay_days"]==1
