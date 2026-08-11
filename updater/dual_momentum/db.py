from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from supabase import Client, create_client

from . import STRATEGY_SLUG


def make_client(url: str, service_role_key: str) -> Client:
    return create_client(url, service_role_key)


def upsert_payload(result: dict) -> dict[str, Any]:
    """백테스트 결과 → 테이블별 upsert 페이로드 (계좌 정보 없음)."""
    st = result["stats"]
    latest = result["latest_signal"]
    if latest is None:
        raise RuntimeError("최신 신호 없음 — upsert 중단")

    signal_row = {
        "strategy_slug": STRATEGY_SLUG,
        "signal_date": latest["signal_date"],
        "kospi_return_12m": latest["kospi_return_12m"],
        "bond_return_12m": latest["bond_return_12m"],
        "selected_asset": latest["selected_asset"],
    }

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
        "monthly_signals": signal_row,
        "backtest_summaries": summary_row,
        "walk_forward_results": wf_rows,
    }


def upsert_all(client: Client, result: dict) -> None:
    payload = upsert_payload(result)

    sig = payload["monthly_signals"]
    r1 = (
        client.table("monthly_signals")
        .upsert(sig, on_conflict="strategy_slug,signal_date")
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
