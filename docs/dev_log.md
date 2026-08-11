# 개발 로그 — Cowork ↔ Claude Code 우편함

새 항목은 이 파일 맨 위(이 안내 바로 아래)에 추가합니다. 작업을
시작하기 전 맨 위 항목부터 읽고, 남겨진 질문/요청이 있으면 먼저
처리하세요. 형식은 `CLAUDE.md`의 "로그 작성 규칙" 참고.

---

## 2026-08-11 16:55 (작성자: Claude Code)
**한 일**: 로컬 git 초기화 후 GitHub 공개 저장소에 최초 푸시.
  https://github.com/retire10x/backtest-lab (`main`, commit `20a3275`).
  `.env` / `updater/.env` / `node_modules` / venv 는 커밋하지 않음.

**왜**: 사용자 요청 — 배포·협업 전에 원격 백업부터.

**결과/남은 이슈**: Supabase 프로젝트 생성·키 연결은 여전히 사용자 작업 대기.

---

## 2026-08-11 16:30 (작성자: Claude Code)
**한 일**: Cowork가 남긴 다음 작업 중 (2)(3)을 처리했다.
- `updater/` 신규: WorkerAI 로직만 참고해 듀얼 모멘텀 신호·백테스트·워크포워드를
  재구현하고, Supabase 3테이블 upsert CLI(`run_update.py`) 작성. WorkerAI import/복사 없음.
  계좌 정보 필드는 넣지 않음. 쓰기는 `SUPABASE_SERVICE_ROLE_KEY`만 사용.
- 수치 검증(`--dry-run`, ETF=`WorkerAI/output/etf_history`): CAGR **+15.2%**,
  MDD **−40.8%**, 총수익 **+238.2%**, 최신신호 2026-08-10 kospi(+128.4%)/bond(−0.6%)→kospi.
  `summary.csv`(15.2%)와 일치. `track_b_strategy_brief.md`의 16.4%는 과거 스냅샷으로
  사이트/시드 기준에서 제외. `supabase/seed.sql` 기간·수치를 이 기준으로 맞춤.
- README §4를 `updater/` 사용법으로 갱신. `.gitignore`에 `updater/.env` 추가.

**왜**: 공개 DB에 넣을 대표 수치를 최신 실행으로 통일하고, 사이트와 분리된
업데이트 경로를 먼저 확보해야 Supabase 연결 직후 바로 채울 수 있다.

**결과/남은 이슈**:
- Supabase 프로젝트 생성·`schema.sql` 적용·루트 `.env`(anon) /
  `updater/.env`(service_role) 키 연결은 **사용자 계정 작업이 필요**해 미완료.
  CLI/로그인 정보가 이 환경에 없음.
- Vercel 배포·도메인·SEO 확장은 아직 미착수.

**다음 담당자에게**:
1. (사용자) supabase.com에서 무료 프로젝트 생성 → SQL Editor에
   `supabase/schema.sql` 실행 → Project Settings > API의 URL / anon /
   service_role 키를 알려주면, 루트 `.env`와 `updater/.env` 채우고
   `python run_update.py --etf-dir …` 로 최초 upsert까지 이어서 하겠다.
2. (선택) seed.sql은 로컬 미리보기용 — 운영은 updater 결과만 쓸 것.
3. brief 문서(16.4%)를 나중에 고칠지는 사용자 확인 후(WorkerAI 쪽 문서).

---

## 2026-08-11 (작성자: Cowork)

**한 일**: 프로젝트 방향을 사용자와 함께 확정했습니다 — 무료 공개
사이트(광고+후원, 유료는 보류), 신호는 참고용으로만 제공하고 실행은
사용자가 본인 계좌에서 직접. WorkerAI 폴더에서 이미 완성된 듀얼모멘텀
로직(`src/strategy/dual_momentum.py`)과 전략 문서
(`docs/track_b_strategy_brief.md`)를 확인했습니다. 기술스택을
Astro + Supabase + Vercel로 확정하고, 사이트 1차 스캐폴딩을
구현했습니다: `supabase/schema.sql`(테이블 3개 + RLS), 페이지 4개
(홈/전략소개/이번달신호/백테스트성과), `README.md`. 로컬에서 빌드 및
4개 라우트 렌더링(200 응답, 면책문구·데이터없음 폴백 정상)까지
확인했습니다.

**왜**: 사용자가 WorkerAI에서 검증한 전략을 공개하고 싶어했고, 규제
검토 결과 "불특정 다수에게 동일 정보 공개 + 실행은 본인 책임" 구조가
안전한 것으로 확인됐습니다(유사투자자문업 신고는 무료 단계에서는
불필요할 가능성이 높지만, 유료 전환 시 재검토 필요).

**결과/남은 이슈**:
- Supabase 프로젝트가 아직 실제로 생성되지 않아, 사이트는 현재
  "데이터 없음" 폴백만 보여줍니다(정상 동작).
- WorkerAI의 `output/dual_momentum/summary.csv`와
  `docs/track_b_strategy_brief.md` 간 수치가 실행 시점에 따라 약간
  다릅니다(CAGR 15.2% vs 16.4%) — 실제 서비스에 올리기 전 최신
  실행 결과로 통일 필요.
- 로컬 빌드 중 Windows 마운트 드라이브에서 `node_modules` 삭제가 잘
  안 되는 이슈가 있었음(파일 자체엔 문제 없음, 무시해도 됨).

**다음 담당자에게 (Claude Code)**:
1. 사용자와 함께 Supabase 프로젝트를 생성하고 `supabase/schema.sql`을
   적용해줘. `.env`에 `PUBLIC_SUPABASE_URL`/`PUBLIC_SUPABASE_ANON_KEY`
   채우는 것까지.
2. `WorkerAI/src/strategy/dual_momentum.py`의 신호 계산 로직을
   **참고해서** (import/복사 금지) 월 1회 실행해 `monthly_signals`,
   `backtest_summaries`, `walk_forward_results` 테이블에 upsert하는
   업데이트 스크립트를 새로 작성해줘. 개인 계좌 정보(잔고/보유수량
   등)는 이 DB에 절대 넣지 마.
3. 배포 전에 백테스트 수치를 최신 실행 기준으로 다시 검증해줘(위
   "결과/남은 이슈" 참고).
4. 진행하다가 전략 방향을 바꾸는 판단(자산군 변경, 유료화 시점 등)이
   필요하면 사용자에게 먼저 물어보고, 끝나면 이 로그 맨 위에 새 항목을
   추가해줘.
