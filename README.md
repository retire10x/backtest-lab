# backtest-lab

소액(100만원 단위) 개인 투자자를 위한 검증 중심의 정직한 투자 정보 사이트.
코스피200 vs 국채3년물 듀얼 모멘텀 전략의 신호와 백테스트 성과를
보여주는 **무료, 정보 제공 전용** 사이트입니다. 1:1 상담·실시간 매매
추천·자동매매 대행은 하지 않습니다 (자세한 규제 배경은
`신규프로젝트_개미투자정보사이트_킥오프프롬프트.md` 참고).

## 구조

```
supabase/schema.sql   DB 스키마 (테이블 3개 + 읽기전용 RLS)
supabase/seed.sql      로컬 미리보기용 예시 데이터 (실제 운영 값 아님)
src/lib/supabase.ts    DB 조회 함수 (전부 SELECT, anon 키만 사용)
src/pages/             홈 / 전략 소개 / 이번 달 신호 / 백테스트 성과
src/layouts, components 공통 레이아웃 + 법적 면책 문구 컴포넌트
```

이 사이트는 **데이터를 쓰지 않습니다.** DB는 별도의 업데이트 프로그램이
채웁니다 (아래 "데이터 업데이트" 참고). 사이트는 Supabase anon 키로
SELECT만 하며, RLS가 anon의 쓰기를 원천 차단합니다.

## 1. Supabase 프로젝트 준비

1. [supabase.com](https://supabase.com) 에서 무료 프로젝트 생성.
2. SQL Editor에서 `supabase/schema.sql` 내용을 실행 (테이블 3개 + RLS 정책 생성).
3. (선택, 로컬 미리보기용) `supabase/seed.sql` 실행 — 화면 확인용 예시 값이며
   실제 서비스에 쓸 수치는 아닙니다.
4. Project Settings → API 에서 `Project URL`과 `anon public` 키를 복사.

## 2. 로컬 개발

```bash
npm install
cp .env.example .env
# .env에 PUBLIC_SUPABASE_URL / PUBLIC_SUPABASE_ANON_KEY 채우기
npm run dev
```

Supabase 키를 아직 설정하지 않아도 빌드는 됩니다 — 페이지에 "데이터
없음" 문구가 뜹니다.

## 3. 배포 (Vercel)

1. 이 저장소를 GitHub에 올리고 Vercel에서 Import.
2. Vercel 프로젝트 환경변수에 `PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_ANON_KEY` 추가.
3. `@astrojs/vercel` 서버리스 어댑터를 쓰므로 별도 빌드 설정 없이 자동 인식됩니다.
4. 각 데이터 페이지(`/signal`, `/backtest`)는 `Cache-Control: s-maxage=3600`
   로 응답하므로, DB를 갱신해도 재배포 없이 최대 1시간 내로 반영됩니다.

## 4. 데이터 업데이트 (`updater/`)

사이트와 분리된 Python 스크립트입니다. WorkerAI 로직만 참고해 **이
저장소 안에서 새로 구현**했으며, WorkerAI를 import하지 않습니다.

```bash
cd updater
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY

# 수치 검증만
python run_update.py --etf-dir path/to/etf_history --dry-run

# DB upsert
python run_update.py --etf-dir path/to/etf_history
```

ETF CSV는 종목코드 파일명(`069500.csv`, `114260.csv`)에 `date,close` 열이
있으면 됩니다.

- 실거래 계좌 정보(잔고, 보유수량 등)는 **절대** 이 DB에 넣지 않습니다.
- `service_role` 키는 `updater/.env` 에만 두고, 사이트/Vercel에는 넣지 않습니다.

| 테이블 | 주기 | 내용 |
|---|---|---|
| `monthly_signals` | 매월 1회 | 이번 달 12개월 수익률 비교 + 선택 자산 |
| `backtest_summaries` | 신호와 같이 | 전체 기간 CAGR/MDD/총수익률/벤치마크 비교 |
| `walk_forward_results` | 신호 갱신 시 | 연도별 수익률/MDD/저축은행 상회 여부 |

## 5. 콘텐츠 관련 주의

- 백테스트 수치를 사이트에 올리기 전, 최신 실행 결과로 재검증할 것
  (`WorkerAI/output/dual_momentum/summary.csv`와 `docs/track_b_strategy_brief.md`
  간 수치가 실행 시점에 따라 다를 수 있음 — 반드시 최신 값 기준으로 통일).
- 모든 성과 관련 페이지에는 `Disclaimer` 컴포넌트가 자동으로 붙습니다.
  새 페이지를 추가할 때도 성과/신호를 다룬다면 반드시 포함할 것.
