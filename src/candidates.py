"""Reproducible role-matched ticker experiments; NO holdings outside reviewed source map.
One change at a time relative to role-v2 unless specifically noted."""
import copy
import json
from pathlib import Path
from src.engine import walk
ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT/"catalog/thematic_v3.json").read_text())
BASE = dict(CATALOG["mapping"])
BASE.update({"GDXU":"LABU","GDXD":"LABD","AGQ":"URAA"})
OVERRIDES = CATALOG.get("signal_overrides", {})

# Frozen candidates selected for analogous *roles*, before calculating this experiment's returns.
CANDIDATES = {
    "gold_gate": {"GDXU":"GDXU","GDXD":"GDXD","AGQ":"URAA"},
    "gold_precious": {"GDXU":"GDXU","GDXD":"GDXD","AGQ":"AGQ"},
    "semis_gate": {"GDXU":"SOXL","GDXD":"SOXS","AGQ":"URAA"},
    "biotech_gate": {"GDXU":"LABU","GDXD":"LABD","AGQ":"URAA"},
    "fang_gate": {"GDXU":"FNGU","GDXD":"FNGD","AGQ":"LABU"},
}
ROLES = {
    "GDXU":"Top-level 3x bull mean-reversion and 60d/90d trend-comparison signal",
    "GDXD":"Top-level inverse 3x gold miners following RSI10>79",
    "AGQ":"Lower-level commodity/uranium/precious-metal momentum rank candidate",
    "BIL":"Short Treasury capital-preservation sleeve",
    "BTAL":"Market-neutral low-beta relative performance sleeve",
    "TLT":"Long-duration Treasury signal/asset",
    "TMF":"Long-duration Treasury +3x leveraged asset",
    "UVXY":"Volatility shock hedge candidate; not risk-free",
    "TQQQ":"Leveraged Nasdaq trend",
    "SQQQ":"Inverse leveraged Nasdaq regime",
    "SPXL":"Leveraged broad-equity trend",
    "UPRO":"Leveraged broad-equity trend",
    "TECL":"Original technology bull sleeve, redirected to SOXL",
    "TECS":"Original technology inverse sleeve, redirected to SOXS",
    "FAS":"Original finance bull sleeve, redirected to SPXL when ranking thematic core stocks",
    "FAZ":"Original finance inverse sleeve, redirected to SPXS",
    "BABA":"High-beta tech candidate, redirected to defense DFEN",
    "PLTR":"Defense/AI single-stock leverage, PTIR; signal uses PLTR",
    "OKLL":"Leveraged early-stage nuclear technology",
    "CONL":"Leveraged high-beta growth candidate, redirected to cybersecurity CRWL",
    "BITX":"Leveraged frontier technology, redirected to quantum IONL",
}

def transform(original, mapping, overrides=OVERRIDES):
    source={n["ticker"] for n in walk(original) if n["step"]=="asset"}
    if set(mapping)!=source or len(source)!=55:
        raise ValueError("All 55 original holding tickers must be mapped exactly once")
    tree=copy.deepcopy(original)
    for n in walk(tree):
        if n["step"]=="asset":
            n["ticker"]=mapping[n["ticker"]]
            n["name"]="Research replacement: "+n["ticker"]
            for field in ("exchange","price","dollarVolume","hasMarketcap"):
                n.pop(field,None)
        if n["step"]=="if-child" and not n.get("is-else-condition?"):
            for field in ("lhs-val","rhs-val"):
                v=n.get(field)
                if isinstance(v,str):
                    n[field]=overrides.get(v,mapping.get(v,v))
    return tree

def generate():
    source=json.loads((ROOT/"data/original.json").read_text())
    baseline=transform(source,BASE)
    expected=json.loads((ROOT/"data/role_v2.json").read_text())
    if baseline!=expected:
        raise ValueError("Existing V2 cannot be rebuilt bit-for-bit; abort experiments")
    trees={}
    for name,changes in CANDIDATES.items():
        mapping=dict(BASE)
        mapping.update(changes)
        tree=transform(source,mapping)
        trees[name]=(tree,mapping)
    return trees

if __name__=="__main__":
    for label,(tree,mapping) in generate().items():
        print(label,"held_tickers",len({n["ticker"] for n in walk(tree) if n["step"]=="asset"}),
              "top_pair",mapping["GDXU"],mapping["GDXD"],"commodity",mapping["AGQ"])
