from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import LOOKBACK_MONTHS


@dataclass(frozen=True)
class MomentumSignal:
    as_of: pd.Timestamp
    hold: str  # kospi | bond | cash
    candidate: str
    cand_ret: float
    rets: dict[str, float]
    haven: str


def returns_as_of(
    prices: pd.DataFrame,
    as_of: pd.Timestamp,
    *,
    lookback_months: int = LOOKBACK_MONTHS,
) -> dict[str, float] | None:
    """as_of 시점 12개월 수익률. 워밍업 부족 시 None."""
    as_of = pd.Timestamp(as_of)
    if as_of not in prices.index:
        hist_all = prices.loc[:as_of]
        if hist_all.empty:
            return None
        as_of = hist_all.index[-1]
    lookback = as_of - pd.DateOffset(months=lookback_months)
    rets: dict[str, float] = {}
    for k in prices.columns:
        hist = prices.loc[:as_of, k]
        p0 = hist.asof(lookback)
        p1 = hist.loc[as_of]
        if pd.isna(p0) or p0 <= 0 or pd.isna(p1):
            return None
        rets[k] = float(p1 / p0 - 1.0)
    return rets


def signal_as_of(
    prices: pd.DataFrame,
    as_of: pd.Timestamp | None = None,
    *,
    haven: str = "cash",
    lookback_months: int = LOOKBACK_MONTHS,
) -> MomentumSignal | None:
    """단일 시점 신호."""
    if prices.empty:
        return None
    as_of = pd.Timestamp(as_of) if as_of is not None else prices.index[-1]
    rets = returns_as_of(prices, as_of, lookback_months=lookback_months)
    if rets is None:
        return None

    asset_keys = list(prices.columns)
    if haven == "bond" and "bond" not in asset_keys:
        raise ValueError("haven=bond 인데 bond 자산 없음")
    compete = (
        [k for k in asset_keys if k != "bond"]
        if haven == "bond"
        else list(asset_keys)
    )
    best_k = max(compete, key=lambda k: rets[k])
    best_ret = rets[best_k]
    hold = best_k if best_ret > 0 else ("bond" if haven == "bond" else "cash")
    hist = prices.loc[:as_of]
    used = hist.index[-1]
    return MomentumSignal(
        as_of=used,
        hold=hold,
        candidate=best_k,
        cand_ret=best_ret,
        rets=rets,
        haven=haven,
    )


def month_end_signals(
    prices: pd.DataFrame,
    *,
    haven: str = "cash",
    lookback_months: int = LOOKBACK_MONTHS,
) -> pd.DataFrame:
    """매월 마지막 거래일마다 signal_as_of → DataFrame."""
    month_ends = prices.groupby(prices.index.to_period("M")).tail(1).index
    rows = []
    for me in month_ends:
        sig = signal_as_of(
            prices, me, haven=haven, lookback_months=lookback_months,
        )
        if sig is None:
            continue
        row = {
            "signal_date": sig.as_of,
            "candidate": sig.candidate,
            "cand_ret": sig.cand_ret,
            "hold": sig.hold,
        }
        for k, v in sig.rets.items():
            row[f"ret_{k}"] = v
        rows.append(row)
    return pd.DataFrame(rows)
