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
