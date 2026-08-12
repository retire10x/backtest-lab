from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from supabase import Client, create_client

from . import STRATEGY_SLUG


def make_client(url: str, service_role_key: str) -> Client:
    return create_client(url, service_role_key)


def monthly_signal_rows(signals_df, limit: int = 12) -> list[dict[str, Any]]:
    """월말 신호 DataFrame(result["signals"]) → 최근 N개월 upsert 행 목록.

    `signals_df`는 `strategy.month_end_signals()`가 만든, 전체 기간의
    월말 신호(2018년부터 전부)다. 여기서 최근 `limit`개월만 잘라
    `monthly_signals` 테이블 행으로 변환한다 — 사이트의 "최근 12개월
    비교" 섹션이 실제로 12행을 보여주려면 이게 필요하다.
    """
    if signals_df is None or signals_df.empty:
        return []
    tail = signals_df.tail(limit)
    rows: list[dict[str, Any]] = []
    for _, row in tail.iterrows():
        rows.append(
            {
                "strategy_slug": STRATEGY_SLUG,
                "signal_date": row["signal_date"].date().isoformat()
                if hasattr(row["signal_date"], "date")
                else str(row["signal_date"]),
                "kospi_return_12m": float(row.get("ret_kospi", float("nan"))),
                "bond_return_12m": float(row.get("ret_bond", float("nan"))),
                "selected_asset": str(row["hold"]),
            }
        )
    return rows


def upsert_payload(result: dict, *, signal_history_months: int = 12) -> dict[str, Any]:
    """백테스트 결과 → 테이블별 upsert 페이로드 (계좌 정보 없음)."""
    st = result["stats"]
    latest = result["latest_signal"]
    if latest is None:
        raise RuntimeError("최신 신호 없음 — upsert 중단")

    signal_rows = monthly_signal_rows(result.get("signals"), limit=signal_history_months)
    if not signal_rows:
        # signals DataFrame이 없는 옛 결과 대비 폴백 — 최신 1건만.
        signal_rows = [
            {
                "strategy_slug": STRATEGY_SLUG,
                "signal_date": latest["signal_date"],
                "kospi_return_12m": latest["kospi_return_12m"],
                "bond_return_12m": latest["bond_return_12m"],
                "selected_asset": latest["selected_asset"],
            }
        ]

    summary_row = {
        "strategy_slug": STRATEGY_SLUG,
        "period_start": st["start"].date().isoformat(),
        "period_end": st["end"].date().isoformat(),
        "cagr": st["ann"],
        "mdd": st["mdd"],
        "total_return": st["total_return"],
        "savings_bank_rate": result["savings_bank"],
        "beats_savings_bank": st["ann"] > result["savings_bank"],
        "passive_benchmark_cagr": result["passive_ann"],
        "passive_benchmark_mdd": result["passive_mdd"],
        "verdict": result["verdict"],
        "verdict_note": result["verdict_note"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    wf_rows = [
        {
            "strategy_slug": STRATEGY_SLUG,
            "year": row["year"],
            "annual_return": row["annual_return"],
            "mdd": row["mdd"],
            "beats_savings_bank": row["beats_savings_bank"],
            "note": row["note"] or None,
        }
        for row in result["walk_forward"]
    ]
    return {
        "monthly_signals": signal_rows,
        "backtest_summaries": summary_row,
        "walk_forward_results": wf_rows,
    }


def upsert_all(client: Client, result: dict, *, signal_history_months: int = 12) -> None:
    payload = upsert_payload(result, signal_history_months=signal_history_months)

    sig_rows = payload["monthly_signals"]
    if sig_rows:
        r1 = (
            client.table("monthly_signals")
            .upsert(sig_rows, on_conflict="strategy_slug,signal_date")
            .execute()
        )
        if getattr(r1, "error", None):
            raise RuntimeError(f"monthly_signals upsert 실패: {r1.error}")

    # backtest_summaries 는 unique 키가 없어 최신 행을 update, 없으면 insert
    existing = (
        client.table("backtest_summaries")
        .select("id")
        .eq("strategy_slug", STRATEGY_SLUG)
        .order("updated_at", desc=True)
        .limit(1)
        .execute()
    )
    summary = payload["backtest_summaries"]
    if existing.data:
        rid = existing.data[0]["id"]
        r2 = (
            client.table("backtest_summaries")
            .update(summary)
            .eq("id", rid)
            .execute()
        )
    else:
        r2 = client.table("backtest_summaries").insert(summary).execute()
    if getattr(r2, "error", None):
        raise RuntimeError(f"backtest_summaries 저장 실패: {r2.error}")

    wf = payload["walk_forward_results"]
    if wf:
        r3 = (
            client.table("walk_forward_results")
            .upsert(wf, on_conflict="strategy_slug,year")
            .execute()
        )
        if getattr(r3, "error", None):
            raise RuntimeError(f"walk_forward_results upsert 실패: {r3.error}")
