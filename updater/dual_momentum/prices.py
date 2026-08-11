from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_price_frame(etf_dir: Path | str, universe: dict[str, str]) -> pd.DataFrame:
    """symbol별 CSV(date,close,…) → 공통 거래일 DataFrame(columns=asset keys)."""
    etf_dir = Path(etf_dir)
    cols: dict[str, pd.Series] = {}
    for key, sym in universe.items():
        path = etf_dir / f"{sym}.csv"
        if not path.exists():
            raise FileNotFoundError(f"ETF CSV 없음: {path}")
        df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
        cols[key] = df["close"].astype(float)
    prices = pd.DataFrame(cols).dropna().sort_index()
    if prices.empty:
        raise RuntimeError("공통 거래일 없음")
    return prices
