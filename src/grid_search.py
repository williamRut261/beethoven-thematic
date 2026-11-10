"""Reproducible, research-only leverage/exposure grid on pre-existing role-matched Beethoven trees.

No brokers, keys, intraday lookahead or assumed pre-listing returns.
Training/test splits are DESCRIPTIVE ONLY because the underlying rule set was previously
evaluated on the entire sample. Never claim the second half is untouched OOS.
"""
import csv
import itertools
import json
import math
from dataclasses import dataclass,asdict
from pathlib import Path
import numpy as np
import pandas as pd
from src.engine import Evaluator
from src.candidates import generate
from src.research import needed,download

BASE=Path(__file__).resolve().parents[1]
OUT=BASE/"evidence"/"grid"
START="2025-11-10"
COST_BPS=20.0
BRANCHES=("gold_gate","semis_gate","biotech_gate")
# Predeclared finite grid. 3 * 3 * 3 * 4 = 108 overlays per branch.
BULL_CAPS=(0.65,0.85,1.00)
BEAR_CAPS=(0.35,0.60,1.00)
NAME_CAPS=(0.50,0.75,1.00)
VOL_TARGETS=(0.30,0.60,1.20,None)
SPLIT_DATE=pd.Timestamp("2026-05-11")

@dataclass(frozen=True)
class Config:
    bull:float
    bear:float
    per_name:float
    vol:float|None
    def id(self):
        return "bull%.2f_bear%.2f_name%.2f_vol%s"%(self.bull,self.bear,self.per_name,"none" if self.vol is None else ("%.2f"%self.vol))

def configs():
    return [Config(*p) for p in itertools.product(BULL_CAPS,BEAR_CAPS,NAME_CAPS,VOL_TARGETS)]

def prepare(root,prices,start=START):
    """Calculate all signals using history through day t, executed at close t+1."""
    dates=prices.index
    if len(dates)<202: raise ValueError("At least 202 chronological rows required")
    rows=[]
    for i in range(200,len(dates)-2):
        if dates[i]<pd.Timestamp(start):
            continue
        hist=prices.iloc[:i+1]
        raw=Evaluator(root,hist).evaluate()
        raw={k:float(v) for k,v in raw.items() if v>0}
        if not math.isclose(sum(raw.values()),1.0,abs_tol=1e-8):
            raise ValueError("Unnormalized Composer tree targets")
        risky={s:w for s,w in raw.items() if s!="BIL"}
        # Same historical portfolio volatility calculation as src.overlay, without future data.
        if risky:
            x=hist[sorted(risky)].iloc[-21:].pct_change().iloc[1:]
            if x.isna().any().any() or not np.isfinite(x.to_numpy()).all():
                raise ValueError("Insufficient 20-day history for risky holdings")
            weights=np.array([risky[s] for s in sorted(risky)])
            vol=float(np.std(x.to_numpy(dtype=float)@weights,ddof=1)*np.sqrt(252))
        else: vol=0.0
        spy=hist["SPY"].iloc[-200:]
        bil=hist["BIL"].iloc[-200:]
        if spy.isna().any() or len(spy)!=200 or bil.isna().any():
            raise ValueError("Incomplete market-regime lookback")
        bull=bool(spy.iloc[-1]>spy.mean())
        fwd={}
        for ticker in set(raw)|{"BIL"}:
            if ticker not in prices:raise ValueError("Missing trade symbol "+ticker)
            a,b=prices[ticker].iloc[i+1:i+3].to_numpy(dtype=float)
            if not(np.isfinite(a) and np.isfinite(b) and a>0 and b>0):
                raise ValueError("Bad t+1 or t+2 trade prices: "+ticker)
            fwd[ticker]=float(b/a)
        rows.append({"date":dates[i+2],"signals_asof":dates[i],"raw":raw,
                     "risky":risky,"vol":vol,"bull":bull,"returns":fwd})
    if not rows: raise ValueError("No valid days")
    return rows

def allocation(row,cfg):
    """Leverage is inside the ETF. Gross portfolio weights never exceed 100%."""
    risky=row["risky"]
    cap=cfg.bull if row["bull"] else cfg.bear
    scale=min(1.0,cap/max(sum(risky.values()),1e-12))
    if cfg.vol is not None and row["vol"]>0:
        scale=min(scale,cfg.vol/row["vol"])
    position={s:min(w*scale,cfg.per_name) for s,w in risky.items()}
    gross=sum(position.values())
    if gross>1.0+1e-10:raise ValueError("Invalid gross exposure")
    position["BIL"]=max(0.0,1.0-gross)
    if abs(sum(position.values())-1)>1e-10:raise ValueError("Weights not normalized")
    return position

def metrics(equity,dates):
    arr=np.asarray(equity,dtype=float)
    if len(arr)<2 or np.any(arr<=0) or not np.isfinite(arr).all():
        raise ValueError("Invalid equity")
    dd=float((arr/np.maximum.accumulate(arr)-1).min())
    days=max(1,(dates[-1]-dates[0]).days)
    return {"return_pct":round(float((arr[-1]-1)*100),4),
            "cagr_pct":round(float((arr[-1]**(365.25/days)-1)*100),4),
            "max_dd_pct":round(dd*100,4),
            "obs":len(arr)-1}

def simulate(rows,cfg,bps=COST_BPS):
    """Signals through t, trade at t+1 close, earn t+1->t+2 price move."""
    previous={}
    equity=[1.0]
    turnovers=0.0
    dates=[rows[0]["date"]-pd.Timedelta(days=1)]
    for row in rows:
        w=allocation(row,cfg)
        trade=sum(abs(w.get(s,0)-previous.get(s,0)) for s in set(w)|set(previous))
        pnl=sum(wt*(row["returns"][s]-1.0) for s,wt in w.items())
        net=1+pnl-bps/10000.0*trade
        if not np.isfinite(net) or net<=0:
            raise ValueError("Non-positive account value")
        equity.append(equity[-1]*net)
        gross=sum(w[s] for s in w if s!="BIL")
        previous={s:w[s]*row["returns"][s]/net for s in w}
        turnovers+=trade
        dates.append(row["date"])
    allstat=metrics(equity,dates)
    # Subwindow metrics from common equity curve. No reset trades or hindsight rebalancing.
    df=pd.DataFrame({"value":equity[1:]},index=[r["date"] for r in rows])
    first=df.loc[df.index<SPLIT_DATE,"value"]
    second=df.loc[df.index>=SPLIT_DATE,"value"]
    def segment(s):
        if len(s)<10:return {"return_pct":None,"max_dd_pct":None,"obs":len(s)}
        base=float(df["value"].loc[:s.index[0]].iloc[-2]) if df.index.get_loc(s.index[0])>0 else 1.0
        vals=np.array([base,*s.to_numpy()])/base
        return {"return_pct":round((vals[-1]-1)*100,4),
                "max_dd_pct":round((vals/np.maximum.accumulate(vals)-1).min()*100,4),
                "obs":len(s)}
    return {"whole":allstat,"first":segment(first),"second":segment(second),
            "turnover":round(turnovers,3),"curve":df}

def build_report():
    OUT.mkdir(exist_ok=True,parents=True)
    candidates=generate()
    wanted=set().union(*(needed(candidates[n][0]) for n in BRANCHES))
    prices,missing=download(wanted)
    report={"status":"BLOCKED","goal":{"cagr_pct":400,"max_dd_pct_above":-50},
            "execution":"next-close (signal close t; trade close t+1; earn close t+1 to close t+2)",
            "modeled_cost_bps":COST_BPS,"trading":"NONE",
            "candidates":BRANCHES,"finite_grid_per_candidate":len(configs()),
            "signal_window_start":START,"data_last":str(prices.index[-1].date()),
            "prelisted_price_synthesis":"NONE","unavailable_tickers":missing,
            "period_split":str(SPLIT_DATE.date()),
            "interpretation":"Retrospective parameter search. Both split periods previously observed while designing the initial strategy; neither an independent untouched OOS. 400% is aspirational, not a projected ROI.",
            "results":{}}
    summaries=[]
    for name in BRANCHES:
        report["results"][name]={"status":"BLOCKED"}
        required=needed(candidates[name][0])
        absent=sorted(required-set(prices))
        if absent:
            report["results"][name]["reason"]="Missing symbols: "+", ".join(absent)
            continue
        try:
            rows=prepare(candidates[name][0],prices)
            records=[]
            for c in configs():
                sim=simulate(rows,c)
                stat={**asdict(c),"id":c.id(),**sim["whole"],
                      "first_return_pct":sim["first"]["return_pct"],
                      "first_dd_pct":sim["first"]["max_dd_pct"],
                      "second_return_pct":sim["second"]["return_pct"],
                      "second_dd_pct":sim["second"]["max_dd_pct"],
                      "turnover":sim["turnover"],"candidate":name}
                stat["passes_in_sample"]=stat["cagr_pct"]>=400 and stat["max_dd_pct"]> -50
                records.append(stat)
                summaries.append(stat)
            best=sorted(records,key=lambda x:x["cagr_pct"],reverse=True)
            feasible=[x for x in best if x["max_dd_pct"]>-50]
            hits=[x for x in feasible if x["cagr_pct"]>=400]
            report["results"][name]={"status":"PRELIMINARY","observation_days":len(rows),
                "grid":len(records),"highest_cagr_any_dd":best[0],
                "best_under_50_dd":feasible[0] if feasible else None,
                "solutions_over_400_under_50":len(hits),
                "top_three_feasible":feasible[:3]}
        except (ValueError,KeyError,RuntimeError,TypeError) as exc:
            report["results"][name]={"status":"BLOCKED","reason":str(exc)}
    if summaries:
        with (OUT/"all_grid_results.csv").open("w",newline="") as out:
            writer=csv.DictWriter(out,fieldnames=list(summaries[0]))
            writer.writeheader();writer.writerows(summaries)
        passing=[x for x in summaries if x["passes_in_sample"]]
        report["status"]="PRELIMINARY"
        report["total_parameter_tests"]=len(summaries)
        report["count_meeting_target_in_sample"]=len(passing)
        report["best_under_dd_50_any_pair"]=sorted(
            [x for x in summaries if x["max_dd_pct"]>-50],key=lambda x:x["cagr_pct"],reverse=True
        )[:10]
        report["all_target_hitting_in_sample"]=sorted(passing,key=lambda x:x["cagr_pct"],reverse=True)[:15]
    (OUT/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print("RESEARCH_GRID",report["status"],"cost",COST_BPS,
          "tests",report.get("total_parameter_tests",0),
          "400+CAGR_and_DD_below50",report.get("count_meeting_target_in_sample",0))
    for name,record in report["results"].items():
        b=record.get("best_under_50_dd")
        print("PAIR",name,"STATUS",record["status"],"BEST_WITH_DD_BELOW_50",
              None if b is None else {
                "cagr":b["cagr_pct"],"return":b["return_pct"],"max_dd":b["max_dd_pct"],
                "configuration":b["id"],"first_half":b["first_return_pct"],
                "second_half":b["second_return_pct"]},
              record.get("reason",""))
    for v in report.get("all_target_hitting_in_sample",[])[:5]:
        print("TARGET_HIT_IN_SAMPLE",v["candidate"],v["id"],v["cagr_pct"],v["max_dd_pct"])
    return report

if __name__=="__main__":
    r=build_report()
    if r["status"]=="BLOCKED":raise SystemExit(1)
