# -*- coding: utf-8 -*-
"""沪深300 估值分析：拉取数据、计算分位数与股债性价比，输出 JSON 摘要。"""
import json
import os

import akshare as ak
import pandas as pd

OUT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(OUT, "data")
os.makedirs(DATA, exist_ok=True)

pd.set_option("display.unicode.east_asian_width", True)


def pct_rank(series: pd.Series, value: float) -> float:
    s = series.dropna()
    if len(s) == 0:
        return float("nan")
    return float((s <= value).mean() * 100)


def window_stats(df: pd.DataFrame, col: str, label: str) -> dict:
    s = df[col].astype(float)
    cur = float(s.iloc[-1])
    out = {"current": cur}
    for name, n in (("all", len(s)), ("10y", 120), ("5y", 60)):
        sub = s.iloc[-n:]
        out[f"pct_{name}"] = round(pct_rank(sub, cur), 2)
        out[f"min_{name}"] = round(float(sub.min()), 2)
        out[f"median_{name}"] = round(float(sub.median()), 2)
        out[f"max_{name}"] = round(float(sub.max()), 2)
    return out


def _cached(name: str, fetch):
    """优先读本地缓存，避免重复请求；?refresh=1 时强制刷新。"""
    path = os.path.join(DATA, name)
    if os.path.exists(path) and os.environ.get("REFRESH") != "1":
        return pd.read_csv(path)
    df = fetch()
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return df


def fetch_dividend_yield() -> pd.DataFrame:
    """用沪深300全收益指数 / 价格指数推算近 12 个月股息率。

    R_t = TR_t / P_t 随分红再投资增长，R_t/R_{t-12}-1 ≈ 过去 12 个月股息回报。
    与中证官网“股息率”口径（按最新分红公告/总市值）存在差异，仅用于观察趋势。
    """
    end = pd.Timestamp.today().strftime("%Y%m%d")

    def close_series(code: str) -> pd.Series:
        df = ak.stock_zh_index_hist_csindex(symbol=code, start_date="20140101", end_date=end)
        df = df[["日期", "收盘"]].copy()
        df.columns = ["date", "close"]
        df["date"] = pd.to_datetime(df["date"])
        df = df.drop_duplicates("date", keep="last").sort_values("date")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        return df.set_index("date")["close"]

    tr = close_series("H00300")
    px = close_series("000300")
    df = pd.concat({"tr": tr, "px": px}, axis=1).dropna()
    df = df[df["px"] > 0]
    ratio = df["tr"] / df["px"]
    me = ratio.resample("ME").last()
    dy = (me / me.shift(12) - 1) * 100
    out = pd.DataFrame({
        "ym": me.index.to_period("M").astype(str),
        "dy": dy.values,
    }).dropna()
    return out


def load_index(symbol: str):
    pe = _cached(f"{symbol}_pe.csv", lambda: ak.stock_index_pe_lg(symbol=symbol))
    pb = _cached(f"{symbol}_pb.csv", lambda: ak.stock_index_pb_lg(symbol=symbol))
    for df in (pe, pb):
        df["日期"] = pd.to_datetime(df["日期"])
        df.drop_duplicates(subset="日期", keep="last", inplace=True)
        df.sort_values("日期", inplace=True)
        df.reset_index(drop=True, inplace=True)
    return pe, pb


def main():
    symbols = ["沪深300", "上证50", "中证500", "中证1000", "中证800"]
    summary = {"as_of": None, "indices": {}, "peers": {}, "bond": {}}

    print("[1/4] 沪深300 PE/PB ...", flush=True)
    pe300, pb300 = load_index("沪深300")
    print("      完成", flush=True)
    summary["as_of"] = str(pe300["日期"].iloc[-1].date())
    summary["index_close"] = float(pe300["指数"].iloc[-1])

    summary["indices"]["pe_ttm"] = window_stats(pe300, "滚动市盈率", "PE-TTM")
    summary["indices"]["pe_static"] = window_stats(pe300, "静态市盈率", "PE-static")
    summary["indices"]["pe_median"] = window_stats(pe300, "滚动市盈率中位数", "PE-median")
    summary["indices"]["pb"] = window_stats(pb300, "市净率", "PB")

    # 同花顺/乐咕的等权口径也保留，便于对照
    summary["indices"]["pe_equal_weight"] = window_stats(pe300, "等权滚动市盈率", "PE-equal")

    print("[2/5] 10年期国债收益率 ...", flush=True)
    # 10 年期国债收益率
    bond = _cached("bond_yield.csv",
                   lambda: ak.bond_zh_us_rate(start_date="20050101"))
    bond["日期"] = pd.to_datetime(bond["日期"])
    bond = bond[["日期", "中国国债收益率10年"]].dropna()
    bond.sort_values("日期", inplace=True)
    bond.rename(columns={"中国国债收益率10年": "y10"}, inplace=True)

    print("[3/5] 股息率历史（全收益指数推算）...", flush=True)
    dy = _cached("dividend_yield.csv", fetch_dividend_yield)
    dy["ym"] = dy["ym"].astype(str)

    # 月末 PE、PB 与当日/最近可得国债收益率对齐
    m = pe300[["日期", "指数", "滚动市盈率", "静态市盈率", "滚动市盈率中位数"]].copy()
    m = pd.merge_asof(m.sort_values("日期"), bond.sort_values("日期"),
                      on="日期", direction="backward")
    m = m.merge(pb300[["日期", "市净率"]], on="日期", how="left")
    m["ym"] = m["日期"].dt.to_period("M").astype(str)
    m = m.merge(dy[["ym", "dy"]], on="ym", how="left")

    m["earnings_yield"] = 100.0 / m["滚动市盈率"]
    m["erp"] = m["earnings_yield"] - m["y10"]
    m["eps_ttm"] = m["指数"] / m["滚动市盈率"]
    m["roe"] = m["市净率"] / m["滚动市盈率"] * 100

    # 当前 PE 在“过去 120 个月”中的分位（滚动近十年分位）
    p = m["滚动市盈率"]
    m["pe_pct_10y"] = [
        round(float((p.iloc[max(0, i - 119):i + 1] <= p.iloc[i]).mean() * 100), 2)
        for i in range(len(p))
    ]

    m.to_csv(os.path.join(DATA, "csi300_valuation_history.csv"),
             index=False, encoding="utf-8-sig")

    cur_y10 = float(bond["y10"].iloc[-1])
    summary["bond"] = {
        "date": str(bond["日期"].iloc[-1].date()),
        "y10": cur_y10,
        "y10_pct_all": round(pct_rank(bond["y10"], cur_y10), 2),
    }
    summary["indices"]["erp"] = window_stats(m, "erp", "ERP")
    summary["indices"]["earnings_yield"] = window_stats(m, "earnings_yield", "E/P")
    summary["indices"]["dividend_yield_derived"] = window_stats(m, "dy", "DY")
    summary["indices"]["roe"] = window_stats(m, "roe", "ROE")
    summary["indices"]["pe_pct_10y_current"] = float(m["pe_pct_10y"].iloc[-1])

    # 盈利与回撤：EPS = 指数点位 / PE-TTM
    pe300["eps_ttm"] = pe300["指数"] / pe300["滚动市盈率"]
    pe300["eps_yoy"] = pe300["eps_ttm"].pct_change(12) * 100
    last = pe300.iloc[-1]
    peak_idx = pe300["指数"].idxmax()
    summary["earnings"] = {
        "eps_ttm": round(float(last["eps_ttm"]), 2),
        "eps_yoy_pct": round(float(last["eps_yoy"]), 1),
        "roe_current": round(float(m["roe"].iloc[-1]), 2),
        "roe_pct_10y": round(float(summary["indices"]["roe"]["pct_10y"]), 1),
        "index_peak": float(pe300.loc[peak_idx, "指数"]),
        "peak_date": str(pe300.loc[peak_idx, "日期"].date()),
        "drawdown_from_peak_pct": round((float(last["指数"]) / float(pe300.loc[peak_idx, "指数"]) - 1) * 100, 1),
    }
    for n, label in ((120, "10y"), (60, "5y")):
        sub = pe300.iloc[-n:]
        summary.setdefault("bands", {})[f"pe_{label}"] = {
            f"p{int(q*100)}": round(float(sub["滚动市盈率"].quantile(q)), 2)
            for q in (.1, .2, .4, .5, .6, .8, .9)
        }
        subp = pb300.iloc[-n:]
        summary["bands"][f"pb_{label}"] = {
            f"p{int(q*100)}": round(float(subp["市净率"].quantile(q)), 3)
            for q in (.1, .2, .4, .5, .6, .8, .9)
        }
        sube = m.iloc[-n:]
        summary["bands"][f"erp_{label}"] = {
            f"p{int(q*100)}": round(float(sube["erp"].quantile(q)), 2)
            for q in (.1, .2, .4, .5, .6, .8, .9)
        }

    print("[4/5] 同业指数对比 ...", flush=True)
    # 同业指数对比（PE-TTM 与 PB 当前值及全历史分位）
    for sym in symbols[1:]:
        try:
            pe, pb = load_index(sym)
            summary["peers"][sym] = {
                "date": str(pe["日期"].iloc[-1].date()),
                "close": float(pe["指数"].iloc[-1]),
                "pe_ttm": round(float(pe["滚动市盈率"].iloc[-1]), 2),
                "pe_ttm_pct_all": round(pct_rank(pe["滚动市盈率"], float(pe["滚动市盈率"].iloc[-1])), 2),
                "pb": round(float(pb["市净率"].iloc[-1]), 2),
                "pb_pct_all": round(pct_rank(pb["市净率"], float(pb["市净率"].iloc[-1])), 2),
            }
        except Exception as e:  # 单个指数失败不影响整体
            summary["peers"][sym] = {"error": f"{type(e).__name__}: {e}"}

    print("[5/5] 中证指数官网口径 ...", flush=True)
    # 中证指数官网口径（整体法，含股息率）
    try:
        cs = ak.stock_zh_index_value_csindex(symbol="000300")
        cs["日期"] = pd.to_datetime(cs["日期"])
        cs.sort_values("日期", inplace=True)
        last = cs.iloc[-1]
        summary["csindex"] = {
            "date": str(last["日期"].date()),
            "pe1": float(last["市盈率1"]),
            "pe2": float(last["市盈率2"]),
            "dy1": float(last["股息率1"]),
            "dy2": float(last["股息率2"]),
        }
    except Exception as e:
        summary["csindex"] = {"error": f"{type(e).__name__}: {e}"}

    pe300.to_csv(os.path.join(DATA, "csi300_pe.csv"), index=False, encoding="utf-8-sig")
    pb300.to_csv(os.path.join(DATA, "csi300_pb.csv"), index=False, encoding="utf-8-sig")

    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
