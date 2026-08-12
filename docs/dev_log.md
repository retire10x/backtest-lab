# 개발 로그 — Cowork ↔ Claude Code 우편함

새 항목은 이 파일 맨 위(이 안내 바로 아래)에 추가합니다. 작업을
시작하기 전 맨 위 항목부터 읽고, 남겨진 질문/요청이 있으면 먼저
처리하세요. 형식은 `CLAUDE.md`의 "로그 작성 규칙" 참고.

---

## 2026-08-12 13:35 (작성자: Claude Code)
**한 일**: Vercel 배포 실패(`_render` runtime `nodejs18.x` invalid) 수정.
- 원인: `@astrojs/vercel@7`가 Node 18로 폴백하는데 Vercel이 18 런타임 폐기.
- `astro@^5` + `@astrojs/vercel@^9`로 업그레이드, adapter import를
  `@astrojs/vercel`로 정리, `engines.node >=22` 추가.
- 로컬 빌드 확인: `.vc-config.json` runtime = `nodejs22.x`.

**왜**: 배포 로그에 invalid runtime으로 막혀 프로덕션 URL이 안 나옴.

**결과/남은 이슈**: 수정분 푸시 후 Vercel 재배포하면 됨. 환경변수
(`PUBLIC_SUPABASE_*`)가 Production에 들어갔는지 배포 URL에서
`/#history` 12행으로 확인.

---

## 2026-08-12 13:15 (작성자: Claude Code)
**한 일**: Cowork 쉬운 문구 변경분 확인 후, 홈 통합·updater 12개월·문구
수정·dev_log를 한 커밋으로 푸시. 배포 준비까지 진행.
- 확인: 홈 한 페이지 스크롤, `#history` 12개월 표, Disclaimer 유지, `npm run build` 성공
- 규제 톤: 라벨 "지금 사면 좋은 쪽" → "이번 달 선택"으로만 완화(나머지 쉬운 말투 유지)
- Vercel CLI는 미로그인 상태 — 디바이스 로그인 필요

**왜**: 지인용 쉬운 문구를 원격에 올리고, 배포만 하면 되게 만들기.

**결과/남은 이슈**: 코드는 GitHub `main`에 올림. Vercel 프로젝트 연결·
환경변수(`PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_ANON_KEY`)·배포는
Vercel 로그인 후 이어서 하면 됨. secret 키는 Vercel에 넣지 말 것.

**다음 담당자에게 / 사용자**: `npx vercel login` 후 Import(GitHub
`retire10x/backtest-lab`) 또는 `npx vercel --prod` 로 배포.

---

## 2026-08-12 (작성자: Cowork) — 문구 쉽게 다시 쓰기

**한 일**: 사용자가 지인들에게 공유했는데 "어려워서" 반응이 없었다고
해서, `src/pages/index.astro` 문구를 전부 쉬운 말로 다시 썼다.
"듀얼 모멘텀", "CAGR", "MDD", "워크포워드", "절대모멘텀" 같은 용어를
제목/라벨에서 빼고 "이번 달엔 뭘 살까?", "1년에 평균 몇 % 벌었나",
"가장 크게 떨어졌을 때", "해마다 다시 시작했다면?" 식으로 바꿈. 맨
위에 "왜 이렇게 할까요?" 문단을 추가해 모멘텀 개념을 비유로 설명.
데이터 로직/컴포넌트 구조는 그대로(같은 쿼리, 같은 섹션 id) — 텍스트만
교체. `BaseLayout` 상단 메뉴 문구도 맞춰서 변경.

**왜**: 내용이 정확해도 안 읽히면 소용없다는 사용자 피드백.

**결과/남은 이슈**: 로컬 빌드·렌더링 확인 완료(텍스트 교체만, 스키마·쿼리
변경 없음). 위 Claude Code 항목의 "홈 통합·updater 수정분 커밋/푸시"
할 때 이번 문구 변경분도 같이 커밋해야 함 — 아직 uncommitted 상태.

**다음 담당자에게**: 다음 커밋 때 이 변경분도 같이 올리고 Vercel
재배포. 실제 배포본에서 지인들 반응이 나아졌는지는 사용자가 직접
확인해야 함.

---

## 2026-08-12 13:05 (작성자: Claude Code)
**한 일**: Cowork 요청대로 `updater/run_update.py`를 재실행해
`monthly_signals` 최근 12개월을 실제 Supabase에 upsert했다.
- ETF: `WorkerAI/output/etf_history`
- 적재 기간: 2025-09-30 ~ 2026-08-10 (12행), 전부 selected=kospi
- publishable 키 SELECT로 12건 확인
- 로컬 `npm run dev` 후 `/` `#history` HTML에서 history-table 데이터 행 12개
  (날짜 12개) 렌더 확인

**왜**: 사이트 "최근 12개월 비교"가 DB에 1건만 있어 표가 비어 보이는
문제를 해소.

**결과/남은 이슈**: DB/로컬 렌더는 OK. Vercel 미배포면 프로덕션에는
아직 구코드·구데이터가 남을 수 있음 — 사이트의 홈 통합 커밋이 원격에
없다면 푸시+재배포 필요. (로컬 working tree에 Cowork 변경이 아직
uncommitted로 남아 있음)

**다음 담당자에게**: 홈 통합·updater 12개월 수정분이 아직 커밋/푸시
전이면 커밋 후 Vercel 재배포. 배포 후 `/#history` 12행 한 번 더 확인.

---

## 2026-08-12 (작성자: Cowork)

**한 일**: `updater/`가 지금까지 `monthly_signals`에 **최신 1건만**
upsert하고 있어서, 사이트 "최근 12개월 비교" 표에 실제로는 1행만
뜨는 문제를 고쳤다.
- `dual_momentum/db.py`: `monthly_signal_rows()` 추가 — 이미
  메모리에 있던 `result["signals"]`(전체 기간 월말 신호 DataFrame,
  `backtest.py`가 항상 계산해두던 값인데 안 쓰고 있었음)의 마지막
  N개월을 `monthly_signals` 행으로 변환. `upsert_payload`/`upsert_all`이
  이제 리스트를 받아 `walk_forward_results`처럼 벌크 upsert.
- `run_update.py`: `--signal-history-months`(기본 12) 옵션 추가.
- dry-run으로 검증: `--etf-dir WorkerAI/output/etf_history
  --signal-history-months 12` → monthly_signals 12행
  (2025-09-30 ~ 2026-08-10) 정상 생성 확인. 스키마/DB 쓰기 방식
  변경 없음(같은 테이블, on_conflict 키도 기존과 동일).

**왜**: 사용자가 "이번 달 신호"뿐 아니라 "최근 12개월 비교"를 보고
싶어했고(사이트에 이미 표는 만들어져 있었음), 실제 DB에 12개월치
데이터가 없어서 표에 1행만 표시되고 있었다.

**결과/남은 이슈**: 이 환경(Cowork)에서는 Supabase로 네트워크가
안 뚫려서 실제 upsert는 못 해봤다(dry-run만 확인). 지난번 최초
데이터 적재는 Claude Code 환경에서 됐으니, 이번에도 거기서 실행해야
할 것 같다.

**다음 담당자에게(Claude Code)**: `updater/.env` 채워진 상태에서
`python run_update.py --etf-dir <ETF CSV 경로>` 한 번만 다시
실행해줘(옵션 기본값이 12개월이라 플래그 안 줘도 됨). 끝나면 사이트
`/`의 "최근 12개월 비교" 표에 12행이 뜨는지 확인 부탁.

---

## 2026-08-11 (작성자: Cowork)

**한 일**: 4개 페이지(`/`, `/strategy/dual-momentum`, `/signal`,
`/backtest`)를 홈(`/`) 한 페이지 스크롤 구조로 통합. 섹션:
이번 달 신호 → 최근 12개월 비교(신규) → 백테스트 성과 → 규칙·한계.
프로즈(탐색 과정 상세 등)는 줄이고 핵심만 남김. 기존 3개 페이지
경로는 삭제 대신 `/#섹션`으로 301 리다이렉트하는 스텁으로 교체(이
환경에서 파일 삭제가 막혀 있어 내용만 리다이렉트로 교체함 — 필요하면
Claude Code가 실제 삭제해도 됨). `BaseLayout` 상단 네비를 페이지
링크에서 앵커 링크로 변경.

**왜**: 사용자가 "4개 페이지를 하나로 합쳐서 스크롤로 보고 싶다",
"12개월 수익률 비교가 매월말 계산되니 최근 12번의 월별 비교도
보여달라"고 요청. 기존 `getSignalHistory(12)`가 이미 그 데이터를
가져오고 있었어서(신호 페이지에 있었음), 홈으로 옮기고 각 자산
수익률을 막대(bar) + %로 같이 보여주도록 보강.

**결과/남은 이슈**: 로컬 빌드/렌더링 확인 완료(env 없이 4개 라우트
정상 — `/`은 200, 기존 3개 경로는 301). 실제 Supabase 데이터로는
이 환경에서 네트워크 제약 때문에 확인 못 함 — Vercel 배포 후
`/#history` 섹션에 12행이 정상적으로 뜨는지 눈으로 한 번 확인
필요.

**다음 담당자에게**: Vercel에 재배포하면 반영됨(코드만 바뀜, 스키마
변경 없음). 여유 있으면 `src/pages/signal.astro`,
`src/pages/backtest.astro`, `src/pages/strategy/dual-momentum.astro`
리다이렉트 스텁을 실제 삭제해서 정리해도 됨(선택, 안 지워도 동작엔
지장 없음).

---

## 2026-08-11 17:20 (작성자: Claude Code)
**한 일**: 사용자가 Supabase URL/키를 채운 뒤 최초 데이터 적재까지 완료.
- `updater/run_update.py`로 3테이블 upsert 성공 (신호 2026-08-10 kospi, CAGR 15.2%).
- publishable(anon) 키로 SELECT 검증 통과 (signal/summary/wf 9건).
- 루트 `.env`에 있던 DB 비밀번호 항목은 사이트에 불필요해 제거(로컬만, 커밋 안 함).

**왜**: 공개 사이트 연결용 키 세팅 후 DB를 비워 두면 페이지가 "데이터 없음"만 보임.

**결과/남은 이슈**: Vercel 배포·도메인·SEO 미착수. Secret 키가 대화/파일 맥락에
노출됐으므로 여유 있을 때 Supabase에서 secret 키 재발급 권장.

**다음 담당자에게**: Vercel에 `PUBLIC_SUPABASE_URL` / `PUBLIC_SUPABASE_ANON_KEY`만
넣고 배포하면 됨. service_role/secret 은 Vercel에 넣지 말 것.

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
