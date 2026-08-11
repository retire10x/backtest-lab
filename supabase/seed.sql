-- 로컬/개발용 시드 데이터 — 기준 수치는 WorkerAI output/dual_momentum/summary.csv
-- (성과시작 2018-01-01, CAGR≈15.2%) 이다.
-- track_b_strategy_brief.md 의 16.4% 는 과거 스냅샷으로, 사이트/시드에 쓰지 않는다.
-- 실제 운영 DB는 updater/run_update.py 가 최신 ETF로 다시 계산해 넣는다.

insert into backtest_summaries
    (strategy_slug, period_start, period_end, cagr, mdd, total_return,
     savings_bank_rate, beats_savings_bank, passive_benchmark_cagr,
     passive_benchmark_mdd, verdict, verdict_note)
values
    ('dual-momentum-kospi-bond', '2018-01-02', '2026-08-10',
     0.1522, -0.4081, 2.3820,
     0.04, true, 0.108, -0.506,
     'useful', '저축은행은 넘고 패시브 대비 낙폭은 얕음 — 존재 이유에 부합.')
on conflict do nothing;

insert into walk_forward_results
    (strategy_slug, year, annual_return, mdd, beats_savings_bank, note)
values
    ('dual-momentum-kospi-bond', 2018, -0.0576, -0.1082, false, ''),
    ('dual-momentum-kospi-bond', 2019,  0.0966, -0.0478, true,  ''),
    ('dual-momentum-kospi-bond', 2020,  0.4722, -0.0851, true,  ''),
    ('dual-momentum-kospi-bond', 2021,  0.0035, -0.1462, false, ''),
    ('dual-momentum-kospi-bond', 2022, -0.0920, -0.1152, false, ''),
    ('dual-momentum-kospi-bond', 2023,  0.0646, -0.1262, true,  ''),
    ('dual-momentum-kospi-bond', 2024, -0.0849, -0.1974, false, ''),
    ('dual-momentum-kospi-bond', 2025,  0.4920, -0.0955, true,  ''),
    ('dual-momentum-kospi-bond', 2026,  0.5801, -0.4081, true,  '연중 데이터(불완전)')
on conflict do nothing;

insert into monthly_signals
    (strategy_slug, signal_date, kospi_return_12m, bond_return_12m, selected_asset)
values
    ('dual-momentum-kospi-bond', '2026-08-10', 1.284489, -0.005627, 'kospi')
on conflict do nothing;
