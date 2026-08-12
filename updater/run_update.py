#!/usr/bin/env python
"""월 1회 듀얼 모멘텀 신호/백테스트를 계산해 Supabase에 upsert.

사용 예:
  # DB 없이 수치만 검증
  python run_update.py --etf-dir D:/develop/WorkerAI/output/etf_history --dry-run

  # 실제 upsert (updater/.env 에 service_role 필요)
  python run_update.py --etf-dir ./data/etf_history

개인 계좌 정보(잔고/보유수량/실거래)는 절대 다루지 않는다.
WorkerAI 코드를 import하지 않는다.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dual_momentum import (  # noqa: E402
    DEFAULT_ONE_WAY_COST,
    UNIVERSE,
)
from dual_momentum.backtest import run_backtest  # noqa: E402
from dual_momentum.db import make_client, upsert_all, upsert_payload  # noqa: E402
from dual_momentum.prices import load_price_frame  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="듀얼 모멘텀 공개 DB 업데이트")
    p.add_argument(
        "--etf-dir",
        required=True,
        help="ETF 일봉 CSV 디렉터리 (069500.csv, 114260.csv)",
    )
    p.add_argument("--capital", type=float, default=1_000_000)
    p.add_argument("--start", default="2018-01-01", help="성과 집계 시작일")
    p.add_argument("--wf-start-year", type=int, default=2018)
    p.add_argument("--wf-end-year", type=int, default=2026)
    p.add_argument("--haven", choices=["cash", "bond"], default="cash")
    p.add_argument(
        "--one-way-cost",
        type=float,
        default=DEFAULT_ONE_WAY_COST,
        help="편도 거래비용(수수료+슬리피지)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="DB에 쓰지 않고 계산 결과만 출력",
    )
    p.add_argument(
        "--signal-history-months",
        type=int,
        default=12,
        help="monthly_signals 테이블에 채울 최근 월말 신호 개수(사이트의 "
        "'최근 12개월 비교' 섹션이 쓰는 행 수)",
    )
    p.add_argument(
        "--env-file",
        default=str(ROOT / ".env"),
        help="SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 가 있는 env 파일",
    )
    return p.parse_args()


def print_report(result: dict) -> None:
    st = result["stats"]
    latest = result["latest_signal"]
    print("=" * 60)
    print("듀얼 모멘텀 (kospi + bond, haven=cash)")
    print(
        f"기간 {st['start'].date()} ~ {st['end'].date()} "
        f"({st['n_years']:.1f}년)"
    )
    print(
        f"CAGR {st['ann']:+.1%} | MDD {st['mdd']:.1%} | "
        f"총수익 {st['total_return']:+.1%} | 최종 {st['final']:,.0f}원"
    )
    print(f"판정: {result['verdict']} — {result['verdict_note']}")
    if latest:
        print(
            f"최신 신호 {latest['signal_date']}: "
            f"kospi {latest['kospi_return_12m']:+.1%}, "
            f"bond {latest['bond_return_12m']:+.1%} → "
            f"{latest['selected_asset']}"
        )
    print("워크포워드:")
    for row in result["walk_forward"]:
        tag = f" [{row['note']}]" if row["note"] else ""
        print(
            f"  {row['year']}: {row['annual_return']:+.1%} "
            f"(MDD {row['mdd']:.1%}) "
            f"{'상회' if row['beats_savings_bank'] else '미달'}{tag}"
        )


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = parse_args()
    etf_dir = Path(args.etf_dir)
    prices = load_price_frame(etf_dir, UNIVERSE)
    for k, sym in UNIVERSE.items():
        s = prices[k]
        print(
            f"로드 {k}({sym}): {s.index.min().date()}~{s.index.max().date()} "
            f"({len(s)}일)"
        )

    result = run_backtest(
        prices,
        capital=float(args.capital),
        one_way_cost=float(args.one_way_cost),
        start=pd.Timestamp(args.start),
        haven=args.haven,
        wf_start=int(args.wf_start_year),
        wf_end=int(args.wf_end_year),
    )
    print_report(result)

    payload = upsert_payload(result, signal_history_months=args.signal_history_months)
    print(
        f"\n--- upsert 페이로드(미리보기, monthly_signals {len(payload['monthly_signals'])}행) ---"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))

    if args.dry_run:
        print("\n[dry-run] DB 쓰기를 건너뜁니다.")
        return 0

    load_dotenv(args.env_file)
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        print(
            f"\n오류: {args.env_file} 에 SUPABASE_URL / "
            "SUPABASE_SERVICE_ROLE_KEY 가 없습니다.",
            file=sys.stderr,
        )
        return 1

    client = make_client(url, key)
    upsert_all(client, result, signal_history_months=args.signal_history_months)
    print(
        f"\n✅ Supabase upsert 완료 (monthly_signals {len(payload['monthly_signals'])}행 / "
        "backtest_summaries / walk_forward_results)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
