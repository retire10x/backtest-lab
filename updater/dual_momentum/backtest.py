from __future__ import annotations

import pandas as pd

from . import (
    PASSIVE_BENCHMARK_ANN,
    PASSIVE_BENCHMARK_MDD,
    SAVINGS_BANK_ANNUAL,
)
from .strategy import month_end_signals


def simulate(
    prices: pd.DataFrame,
    signals: pd.DataFrame,
    *,
    capital: float,
    one_way_cost: float,
    start: pd.Timestamp,
) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    """일별 자산곡선. 월말 신호 → 다음 거래일 종가에 전환."""
    aligned = prices.sort_index()
    if signals.empty:
        raise RuntimeError("신호 없음 — ETF 이력/워밍업 부족")

    all_days = aligned.index
    exec_rows = []
    for _, row in signals.iterrows():
        sig_d = row["signal_date"]
        future = all_days[all_days > sig_d]
        if len(future) == 0:
            continue
        exec_rows.append({**row.to_dict(), "exec_date": future[0]})
    exec_df = pd.DataFrame(exec_rows)
    if exec_df.empty:
        raise RuntimeError("체결 가능일 없음")

    target = pd.Series("cash", index=all_days, dtype=object)
    dates = exec_df["exec_date"].tolist()
    holds = exec_df["hold"].tolist()
    for i, (ed, h) in enumerate(zip(dates, holds)):
        if i + 1 < len(dates):
            mask = (all_days >= ed) & (all_days < dates[i + 1])
        else:
            mask = all_days >= ed
        target.loc[mask] = h

    pct = aligned.pct_change().fillna(0.0)
    asset_ret = pd.Series(0.0, index=all_days)
    for col in aligned.columns:
        asset_ret = asset_ret.mask(target == col, pct[col])

    prev = target.shift(1)
    switched = target.ne(prev) & prev.notna()
    daily = asset_ret.copy()
    daily.loc[switched] = (1.0 + daily.loc[switched]) * (1.0 - one_way_cost) - 1.0

    daily = daily.loc[daily.index >= start]
    target = target.loc[daily.index]
    if daily.empty:
        raise RuntimeError("start 이후 데이터 없음")

    equity = capital * (1.0 + daily).cumprod()
    return equity, target, exec_df


def stats(equity: pd.Series, capital: float) -> dict:
    total_return = equity.iloc[-1] / capital - 1.0
    n_years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1e-9)
    ann = (1.0 + total_return) ** (1.0 / n_years) - 1.0
    mdd = (equity / equity.cummax() - 1.0).min()
    return {
        "final": float(equity.iloc[-1]),
        "total_return": float(total_return),
        "ann": float(ann),
        "mdd": float(mdd),
        "n_years": float(n_years),
        "start": equity.index[0],
        "end": equity.index[-1],
    }


def year_fold(equity: pd.Series, year: int, capital: float) -> dict | None:
    w = equity[(equity.index >= f"{year}-01-01") & (equity.index < f"{year + 1}-01-01")]
    if len(w) < 5:
        return None
    scaled = capital * (w / w.iloc[0])
    return stats(scaled, capital) | {"year": year, "n_days": len(w)}


def verdict_of(st: dict) -> tuple[str, str]:
    mdd_better = st["mdd"] > PASSIVE_BENCHMARK_MDD
    bank_ok = st["ann"] > SAVINGS_BANK_ANNUAL
    if bank_ok and mdd_better:
        return (
            "useful",
            "저축은행은 넘고 패시브 대비 낙폭은 얕음 — 존재 이유에 부합.",
        )
    if bank_ok and not mdd_better:
        return "bank_only", "저축은행은 넘지만 낙폭 개선이 불명확."
    return "fail", "저축은행조차 미달."


def run_backtest(
    prices: pd.DataFrame,
    *,
    capital: float,
    one_way_cost: float,
    start: pd.Timestamp,
    haven: str,
    wf_start: int,
    wf_end: int,
) -> dict:
    signals = month_end_signals(prices, haven=haven)
    equity, holdings, trades = simulate(
        prices,
        signals,
        capital=capital,
        one_way_cost=one_way_cost,
        start=start,
    )
    st = stats(equity, capital)

    wf_rows = []
    for y in range(wf_start, wf_end + 1):
        r = year_fold(equity, y, capital)
        if r is None:
            continue
        h_y = holdings[
            (holdings.index >= f"{y}-01-01") & (holdings.index < f"{y + 1}-01-01")
        ]
        all_cash = (not h_y.empty) and (h_y == "cash").all()
        note = "워밍업(전구간현금)" if all_cash else ""
        # 연중 불완전 구간(해당 연도 거래일 부족) 표시
        if y == equity.index[-1].year and r["n_days"] < 200:
            note = (note + " · " if note else "") + "연중 데이터(불완전)"
        beat = r["total_return"] > SAVINGS_BANK_ANNUAL
        wf_rows.append(
            {
                "year": y,
                "annual_return": r["total_return"],
                "mdd": r["mdd"],
                "beats_savings_bank": beat,
                "note": note,
            }
        )

    latest = None
    if not signals.empty:
        last = signals.iloc[-1]
        latest = {
            "signal_date": pd.Timestamp(last["signal_date"]).date().isoformat(),
            "kospi_return_12m": float(last.get("ret_kospi", float("nan"))),
            "bond_return_12m": float(last.get("ret_bond", float("nan"))),
            "selected_asset": str(last["hold"]),
        }

    verdict, verdict_note = verdict_of(st)
    return {
        "stats": st,
        "trades": trades,
        "signals": signals,
        "latest_signal": latest,
        "walk_forward": wf_rows,
        "verdict": verdict,
        "verdict_note": verdict_note,
        "passive_ann": PASSIVE_BENCHMARK_ANN,
        "passive_mdd": PASSIVE_BENCHMARK_MDD,
        "savings_bank": SAVINGS_BANK_ANNUAL,
    }
