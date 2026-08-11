"""공개 사이트용 듀얼 모멘텀 계산 (신호 + 백테스트).

WorkerAI와 코드/실행환경을 공유하지 않는다. 규칙은 동일하되 여기서 새로 구현한다.
개인 계좌 정보(잔고/보유수량/실거래)는 다루지 않는다.
"""

STRATEGY_SLUG = "dual-momentum-kospi-bond"
LOOKBACK_MONTHS = 12
UNIVERSE = {
    "kospi": "069500",  # KODEX 200
    "bond": "114260",  # KODEX 국고채3년
}
SAVINGS_BANK_ANNUAL = 0.04
PASSIVE_BENCHMARK_ANN = 0.108
PASSIVE_BENCHMARK_MDD = -0.506
DEFAULT_ONE_WAY_COST = 0.00065  # fee 0.015% + slip 0.05%
