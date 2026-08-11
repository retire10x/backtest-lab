-- backtest-lab 공개 데이터 스키마
--
-- 이 DB는 "공개 표시용" 데이터만 담는다. 개인 계좌 잔고/보유수량/실거래 기록은
-- 절대 이 DB에 넣지 않는다 (그건 WorkerAI 쪽 별도 DB에서만 관리).
--
-- 쓰기(INSERT/UPDATE)는 별도의 업데이트 프로그램이 service_role 키로 수행한다.
-- 사이트(Astro)는 anon 키로 SELECT만 한다 — RLS로 강제한다.

-- ============================================================
-- 1. 이번 달(또는 특정 시점) 신호 히스토리
-- ============================================================
create table if not exists monthly_signals (
    id                bigint generated always as identity primary key,
    strategy_slug     text not null default 'dual-momentum-kospi-bond',
    signal_date       date not null,              -- 신호 산출 기준일(월말 거래일)
    kospi_return_12m  numeric not null,            -- 코스피200 12개월 수익률
    bond_return_12m   numeric not null,            -- 국채3년물 12개월 수익률
    selected_asset    text not null check (selected_asset in ('kospi', 'bond', 'cash')),
    created_at        timestamptz not null default now(),
    unique (strategy_slug, signal_date)
);

create index if not exists idx_monthly_signals_date
    on monthly_signals (strategy_slug, signal_date desc);

-- ============================================================
-- 2. 백테스트 종합 성과 (전략별로 최신 1건이 "현재 대표 성과")
-- ============================================================
create table if not exists backtest_summaries (
    id                     bigint generated always as identity primary key,
    strategy_slug          text not null default 'dual-momentum-kospi-bond',
    period_start           date not null,
    period_end             date not null,
    cagr                   numeric not null,        -- 연환산 수익률
    mdd                    numeric not null,         -- 최대낙폭 (음수)
    total_return           numeric not null,         -- 누적 총수익률
    savings_bank_rate      numeric not null default 0.04,
    beats_savings_bank     boolean not null,
    passive_benchmark_cagr numeric,
    passive_benchmark_mdd  numeric,
    verdict                text,                     -- useful | bank_only | fail
    verdict_note           text,                     -- 한글 설명
    updated_at             timestamptz not null default now()
);

create index if not exists idx_backtest_summaries_strategy
    on backtest_summaries (strategy_slug, updated_at desc);

-- ============================================================
-- 3. 연도별 워크포워드 결과
-- ============================================================
create table if not exists walk_forward_results (
    id                   bigint generated always as identity primary key,
    strategy_slug        text not null default 'dual-momentum-kospi-bond',
    year                 int not null,
    annual_return        numeric not null,
    mdd                  numeric not null,
    beats_savings_bank   boolean not null,
    note                 text,                        -- 예: "워밍업(전구간현금)"
    unique (strategy_slug, year)
);

create index if not exists idx_walk_forward_strategy_year
    on walk_forward_results (strategy_slug, year);

-- ============================================================
-- RLS: 누구나 읽기 가능, 쓰기는 anon 불가 (service_role만 가능)
-- ============================================================
alter table monthly_signals enable row level security;
alter table backtest_summaries enable row level security;
alter table walk_forward_results enable row level security;

drop policy if exists "public read monthly_signals" on monthly_signals;
create policy "public read monthly_signals"
    on monthly_signals for select
    to anon
    using (true);

drop policy if exists "public read backtest_summaries" on backtest_summaries;
create policy "public read backtest_summaries"
    on backtest_summaries for select
    to anon
    using (true);

drop policy if exists "public read walk_forward_results" on walk_forward_results;
create policy "public read walk_forward_results"
    on walk_forward_results for select
    to anon
    using (true);

-- anon에는 insert/update/delete 정책을 만들지 않는다 = 기본적으로 전부 거부.
-- 별도 업데이트 프로그램은 service_role 키(비밀키, 사이트에는 절대 넣지 않음)로 접속해서 씀.
