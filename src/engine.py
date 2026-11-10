"""Read-only Composer-style research evaluator. No broker access or order writes."""
import math
from collections import defaultdict
from pathlib import Path
import json
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent

def walk(node):
    yield node
    for child in node.get("children", []):
        yield from walk(child)

def load(path=None):
    return json.loads(Path(path or (HERE.parent / "data" / "thematic_v3.json")).read_text())

def window(node, side):
    value = node.get(side + "-fn-params", {}).get("window", node.get(side + "-window-days"))
    if value is None and node.get(side + "-fn") == "current-price":
        return 1
    if value is None:
        raise ValueError("Indicator window missing")
    result = int(value)
    if result < 1 or result > 1000 or float(value) != result:
        raise ValueError("Invalid indicator window")
    return result

def indicator(prices, fn, days):
    p = np.asarray(prices, dtype=float)
    required = 1 if fn == "current-price" else days if fn == "moving-average-price" else days + 1
    if len(p) < required or not np.isfinite(p).all() or np.any(p <= 0):
        raise ValueError(f"Insufficient/invalid price history for {fn}: {days}")
    if fn == "current-price":
        return float(p[-1])
    if fn == "moving-average-price":
        return float(p[-days:].mean())
    if fn == "relative-strength-index":
        delta = np.diff(p[-1001:])
        gains, losses = np.maximum(delta, 0), np.maximum(-delta, 0)
        g, l = gains[:days].mean(), losses[:days].mean()
        for up, down in zip(gains[days:], losses[days:]):
            g, l = (g * (days - 1) + up) / days, (l * (days - 1) + down) / days
        return 50.0 if g == l == 0 else 100.0 if l == 0 else float(100 - 100 / (1 + g / l))
    returns = p[-days:] / p[-days - 1:-1] - 1
    if fn == "cumulative-return":
        return float(100 * (p[-1] / p[-days-1] - 1))
    if fn == "moving-average-return":
        return float(100 * returns.mean())
    if fn == "standard-deviation-return":
        if days < 2:
            raise ValueError("Volatility needs 2+ daily returns")
        return float(100 * returns.std(ddof=1))
    raise ValueError("Unsupported indicator: " + fn)

class Evaluator:
    def __init__(self, root, closes):
        if not isinstance(closes, pd.DataFrame) or closes.empty:
            raise ValueError("Price frame required")
        self.root, self.closes, self.cache = root, closes, {}

    def metric(self, symbol, fn, days):
        key = (symbol, fn, days)
        if key not in self.cache:
            if symbol not in self.closes:
                raise ValueError("Missing signal symbol " + symbol)
            series = self.closes[symbol]
            first = series.first_valid_index()
            if first is None:
                raise ValueError("No history for " + symbol)
            series = series.loc[first:]
            length = 1001 if fn == "relative-strength-index" else days+1
            self.cache[key] = indicator(series.iloc[-length:], fn, days)
        return self.cache[key]

    def condition(self, n):
        lhs = self.metric(n["lhs-val"], n["lhs-fn"], window(n, "lhs"))
        rhs = (float(n["rhs-val"]) if n.get("rhs-fixed-value?")
               else self.metric(n["rhs-val"], n["rhs-fn"], window(n, "rhs")))
        if n["comparator"] == "gt":
            return lhs > rhs
        if n["comparator"] == "lt":
            return lhs < rhs
        raise ValueError("Unsupported comparator")

    def evaluate(self, n=None):
        n = self.root if n is None else n
        children = n.get("children", [])
        step = n["step"]
        if step == "asset":
            return {n["ticker"]: 1.0}
        if not children:
            raise ValueError("Empty strategy block")
        if step == "if":
            for c in children:
                if c.get("is-else-condition?") or self.condition(c):
                    return self.evaluate(c)
            raise ValueError("Missing else branch")
        if step == "filter":
            symbols = list(dict.fromkeys(s for c in children for s in self.evaluate(c)))
            scores = {s: self.metric(s, n["sort-by-fn"], window(n, "sort-by")) for s in symbols}
            ordered = sorted(symbols, key=lambda s: scores[s], reverse=n["select-fn"] == "top")
            selected = ordered[:int(n["select-n"])]
            if not selected:
                raise ValueError("Empty filter result")
            return {s: 1 / len(selected) for s in selected}
        if step == "wt-cash-specified":
            weights = [float(c["weight"]["num"])/float(c["weight"]["den"]) for c in children]
            if not math.isclose(sum(weights), 1.0, abs_tol=1e-9):
                raise ValueError("Invalid specified weights")
        elif step == "wt-inverse-vol":
            if len(children) == 1:
                weights = [1.0]
            else:
                v = [self.metric(c["ticker"], "standard-deviation-return", int(n["window-days"])) for c in children]
                zero = [i for i,x in enumerate(v) if x == 0]
                if zero:
                    weights = [1 / len(zero) if i in zero else 0 for i in range(len(v))]
                else:
                    inverse = [1/x for x in v]
                    weights = [x/sum(inverse) for x in inverse]
        else:
            if step not in ("root", "group", "wt-cash-equal", "if-child"):
                raise ValueError("Unknown step " + step)
            weights = [1 / len(children)] * len(children)
        out = defaultdict(float)
        for child, w in zip(children, weights):
            if w == 0:
                continue
            for symbol, portion in self.evaluate(child).items():
                out[symbol] += w * portion
        if not math.isclose(sum(out.values()), 1.0, abs_tol=1e-8):
            raise ValueError("Invalid total target weights")
        return dict(out)

def run_backtest(closes, start_date, cost_bps=5.0, strategy_root=None):
    """Idealized signal at close t, earn t->t+1 close return; NO real fills."""
    if not isinstance(closes.index, pd.DatetimeIndex) or closes.index.has_duplicates or not closes.index.is_monotonic_increasing:
        raise ValueError("Unique increasing date index required")
    if not math.isfinite(cost_bps) or cost_bps < 0:
        raise ValueError("Invalid cost")
    if len(closes) < 202:
        raise ValueError("At least 202 daily rows required, including warmup")
    root = load() if strategy_root is None else strategy_root
    start = pd.Timestamp(start_date)
    dates, equity = [], []
    value, last_weights, summed_turnover = 1.0, {}, 0.0
    for i in range(200, len(closes)-1):
        if closes.index[i] < start:
            continue
        weights = Evaluator(root, closes.iloc[:i+1]).evaluate()
        allsyms = set(weights) | set(last_weights)
        turnover = sum(abs(weights.get(s,0)-last_weights.get(s,0)) for s in allsyms)
        daily = 0.0
        realized = {}
        for symbol,w in weights.items():
            if symbol not in closes:
                raise ValueError("Missing trade price for " + symbol)
            a,b = float(closes[symbol].iloc[i]), float(closes[symbol].iloc[i+1])
            if not math.isfinite(a) or not math.isfinite(b) or min(a,b) <= 0:
                raise ValueError("Missing/invalid daily execution price " + symbol)
            realized[symbol] = b/a
            daily += w*(b/a-1)
        net = 1+daily-turnover*cost_bps/10000
        if net <= 0:
            raise ValueError("Bankrupt/malformed simulation")
        value *= net
        last_weights = {s:w*realized[s]/net for s,w in weights.items()}
        summed_turnover += turnover
        dates.append(closes.index[i+1])
        equity.append(value)
    if not equity:
        raise ValueError("No test dates")
    curve = pd.Series(equity,index=pd.DatetimeIndex(dates),name="equity")
    days = (curve.index[-1]-curve.index[0]).days
    cagr = float(curve.iloc[-1]**(365.25/max(1,days))-1)
    drawdown = float((curve/curve.cummax()-1).min())
    return {"observations":len(curve),"final_multiple":float(curve.iloc[-1]),
            "cagr_idealized":cagr,"max_drawdown":drawdown,
            "summed_one_way_turnover":summed_turnover,"cost_bps":cost_bps,
            "method":"research next-close, point-in-time symbols; NOT fill-accurate"},curve
