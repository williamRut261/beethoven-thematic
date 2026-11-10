"""One-shot public-data research. Zero broker or order APIs, no schedules."""
import json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from src.engine import Evaluator,walk
from src.overlay import hedge_portfolio

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"evidence"
ROOTS={
"original":ROOT/"data/original.json",
"prior_role_v2":ROOT/"data/role_v2.json",
"thematic_v3":ROOT/"data/thematic_v3.json",
}
from src.candidates import generate as generate_role_candidates

SCENARIOS=[
("original","original"),
("prior_role_v2","original"),
("prior_role_v2","half"),
("prior_role_v2","regime_vol40"),
("prior_role_v2","regime_vol30"),
("thematic_v3","original"),
("thematic_v3","half"),
("thematic_v3","regime_vol40"),
("thematic_v3","regime_vol30"),
("gold_gate","original"),
("gold_gate","half"),
("gold_gate","regime_vol30"),
("gold_precious","original"),
("gold_precious","regime_vol30"),
("semis_gate","original"),
("semis_gate","regime_vol30"),
("biotech_gate","regime_vol30"),
("fang_gate","regime_vol30"),
]
WINDOWS=["2024-11-10","2025-11-10","2026-05-10","2026-10-01"]

def needed(root):
    names={x["ticker"] for x in walk(root) if x["step"]=="asset"}
    for x in walk(root):
        if x["step"]=="if-child" and not x.get("is-else-condition?"):
            names.add(x["lhs-val"])
            if not x.get("rhs-fixed-value?"):
                names.add(x["rhs-val"])
    return names|{"BIL","SPY"}

def download(names):
    import yfinance as yf
    aliases={s:("BRK-B" if s=="BRK.B" else s) for s in names}
    bars=yf.download(tickers=list(sorted(set(aliases.values()))),
        period="5y",interval="1d",group_by="ticker",
        auto_adjust=True,threads=False,progress=False)
    if bars.empty:
        raise RuntimeError("Yahoo Finance returned no historical data")
    result={}
    failures=[]
    for symbol,vendor in aliases.items():
        try:
            one=bars[vendor] if isinstance(bars.columns,pd.MultiIndex) else bars
            series=pd.to_numeric(one["Close"],errors="coerce")
            if series.dropna().empty:
                failures.append(symbol)
            else:
                result[symbol]=series
        except (KeyError,ValueError,TypeError):
            failures.append(symbol)
    df=pd.DataFrame(result).sort_index()
    if df.index.tz is not None: df.index=df.index.tz_localize(None)
    if df.index.has_duplicates or not df.index.is_monotonic_increasing:
        raise RuntimeError("Malformed time index")
    if (pd.Timestamp.utcnow().tz_localize(None)-df.index[-1]).days>7:
        raise RuntimeError("Public price series is stale")
    return df,sorted(failures)

def backtest(root,prices,start,style,cost_bps=5.0,execution_delay_days=0):
    if execution_delay_days not in (0,1):
        raise ValueError("Delay must be zero or one full trading day")
    dates=prices.index
    if len(dates)<202:
        raise ValueError("Missing 200-day warmup")
    begin=pd.Timestamp(start)
    values=[1.0]; observations=[]; previous={}
    turnover_sum=0.0
    for i in range(200,len(dates)-1-execution_delay_days):
        if dates[i]<begin: continue
        hist=prices.iloc[:i+1]
        proposed=Evaluator(root,hist).evaluate()
        weights=hedge_portfolio(proposed,hist,style)
        if not math.isclose(sum(weights.values()),1.0,abs_tol=1e-8):
            raise ValueError("Weights not normalized")
        turnover=sum(abs(weights.get(s,0)-previous.get(s,0)) for s in set(weights)|set(previous))
        profit=0.0
        realized={}
        trade_index=i+execution_delay_days
        for s,w in weights.items():
            if s not in prices: raise ValueError("Missing execution symbol "+s)
            a,b=prices[s].iloc[trade_index:trade_index+2].to_numpy(dtype=float)
            if not (np.isfinite(a) and np.isfinite(b) and a>0 and b>0):
                raise ValueError("Historical price missing on selected day: "+s+" "+str(dates[i].date()))
            realized[s]=b/a
            profit+=w*(b/a-1)
        net=1.0+profit-turnover*cost_bps/10000
        if not np.isfinite(net) or net<=0:
            raise ValueError("Nonpositive portfolio value")
        values.append(values[-1]*net)
        previous={s:w*realized[s]/net for s,w in weights.items()}
        turnover_sum+=turnover
        observations.append(dates[trade_index+1])
    if len(observations)<10: raise ValueError("Fewer than 10 realized return observations")
    equity=np.array(values)
    peaks=np.maximum.accumulate(equity)
    dd=float(np.min(equity/peaks-1))
    if dd>0 or dd< -1:raise ValueError("Invalid drawdown")
    curve=pd.Series(equity[1:],index=pd.DatetimeIndex(observations),name="equity")
    return {
        "observations":len(observations),"first":str(observations[0].date()),"last":str(observations[-1].date()),
        "period_return_pct":round((equity[-1]-1)*100,4),
        "max_drawdown_pct":round(dd*100,4),
        "turnover_one_way":round(turnover_sum,3),
        "annualized_return_pct":round((equity[-1]**(365.25/max(1,(observations[-1]-observations[0]).days))-1)*100,4),
        "qualifies_under_50_in_sample":dd > -0.50,
        "status":"PRELIMINARY", "execution_delay_days":execution_delay_days,
    },curve

def main():
    OUT.mkdir(exist_ok=True)
    roots={name:json.loads(path.read_text()) for name,path in ROOTS.items()}
    roots.update({name:tree for name,(tree,_mapping) in generate_role_candidates().items()})
    required={name:needed(root) for name,root in roots.items()}
    report={"objective":"Frozen role-matched ticker swaps vs original and prior V2; exploratory, not return-optimized",
            "method":"Daily adjusted close, close-to-next-close 5 bps per unit turnover; no live orders",
            "data":"Yahoo Finance public historical prices; no pre-inception synthetic backfills",
            "limits":"Signal-engine parity with Composer, slippage, real fills, corporate actions, spreads and issuer credit risks not independently validated; no OOS guarantee.",
            "scenarios":SCENARIOS,"results":{},"status":"BLOCKED"}
    try:
        prices,missing=download(set().union(*required.values()))
        report["history_start"]=str(prices.index[0].date())
        report["history_end"]=str(prices.index[-1].date())
        report["missing_symbols"]=missing
        report["coverage"]={s:{"first":str(prices[s].first_valid_index().date()),
          "count":int(prices[s].count())} for s in prices.columns}
        prices.to_csv(OUT/"public_closes.csv")
        for root_name,style in SCENARIOS:
            label=root_name+"__"+style
            report["results"][label]={}
            absent=sorted(required[root_name]-set(prices))
            for start in WINDOWS:
                try:
                    if absent: raise ValueError("Missing symbols: "+",".join(absent))
                    result,curve=backtest(roots[root_name],prices,start,style)
                    report["results"][label][start]=result
                    curve.to_csv(OUT/(label+"_"+start+".csv"))
                except (ValueError,KeyError,RuntimeError,IndexError,TypeError) as exc:
                    report["results"][label][start]={"status":"BLOCKED","reason":str(exc)}
        if any(x["status"]=="PRELIMINARY" for d in report["results"].values() for x in d.values()):
            report["status"]="PRELIMINARY"
    except Exception as exc:
        report["failure"]=str(exc)
    # Execution timing sensitivity: signal at close t, buy at NEXT close t+1,
    # then earn t+1 to t+2. A stricter (but still simplified) executable delay check.
    report["execution_sensitivity"]={}
    if report["status"]=="PRELIMINARY":
        for name,style in (
            ("gold_gate","regime_vol30"),
            ("gold_gate","half"),
            ("semis_gate","regime_vol30"),
            ("biotech_gate","regime_vol30"),
            ("fang_gate","regime_vol30"),
        ):
            key=name+"__"+style
            report["execution_sensitivity"][key]={}
            for bps in (5.0,20.0):
                try:
                    missing=sorted(required[name]-set(prices.columns))
                    if missing:
                        raise ValueError("Missing symbols: "+",".join(missing))
                    result,curve=backtest(roots[name],prices,"2025-11-10",style,
                                          cost_bps=bps,execution_delay_days=1)
                    report["execution_sensitivity"][key][str(int(bps))+"bps"]=result
                    curve.to_csv(OUT/(key+"_delay1_"+str(int(bps))+"bps.csv"))
                except (ValueError,KeyError,RuntimeError,IndexError,TypeError) as exc:
                    report["execution_sensitivity"][key][str(int(bps))+"bps"]={"status":"BLOCKED","reason":str(exc)}
    (OUT/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print("STATUS:",report["status"],"DATA:",report.get("history_start"),"to",report.get("history_end"))
    if report.get("failure"):print("FAILURE:",report["failure"])
    for start in WINDOWS:
        print("WINDOW:",start)
        for label,window in report["results"].items():
            x=window[start]
            print(label,x["status"],x.get("period_return_pct",x.get("reason")),
                  "DD",x.get("max_drawdown_pct"),"N",x.get("observations"))
    print("EXECUTION DELAYED ONE CLOSE, 1Y:")
    for name,by_cost in report.get("execution_sensitivity",{}).items():
        for cost,results in by_cost.items():
            print(name,cost,results.get("status"),results.get("period_return_pct",results.get("reason")),
                  "DD",results.get("max_drawdown_pct"))
    if report["status"]=="BLOCKED": raise SystemExit(1)

if __name__=="__main__":
    main()
