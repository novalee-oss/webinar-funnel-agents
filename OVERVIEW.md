# 로켓런칭 AI 에이전트 시스템 — 전체 개요

## 왜 만들었나

지식 창업 런칭(웨비나 퍼널)은 매번 비슷한 작업이 반복된다.
시장 조사 → 상품 기획 → 카피 작성 → CRM 설계 → 강의안 → 상세페이지 → 광고.

매니저가 이 모든 걸 매번 처음부터 하면 시간이 너무 많이 든다.
이 시스템은 **반복 가능한 부분을 AI가 초안으로 처리하고, 판단이 필요한 지점에서만 사람이 개입**하는 구조로 설계됐다.

최종 결정(약속 강도, 가격, 후킹, 콘셉트 라인)은 항상 사람(Nova)이 한다.
AI는 후보와 근거를 제시할 뿐, 자동으로 결정하지 않는다.

---

## 전체 흐름 (Stage 0 → 4 + 후속)

```
[Stage 0]   미팅 노트 분석          context-loader
[Stage 0.5] 시장 조사               market-researcher
[Stage 0.5B] 고객 언어 수집         keyword-researcher
[Stage 0.5C] 매출 시뮬레이션        revenue-checkpoint
[Stage 0.6] 퍼널 적합성 판단        funnel-validator       ← ★★★ go/no-go

[Stage 1A]  타깃 페르소나·페인포인트  paid-planner
[Stage 1B]  약속·가격 설정           paid-planner           ← ★★★ Nova 선택
[Stage 1C]  커리큘럼·사례·FAQ        paid-planner           ← ★★★ 콘셉트 라인 선택

[Stage 2]   후킹·무료/유료 가치 분배  hook-designer          ← ★★★ Nova 선택
[Stage 3]   무료 웨비나 기획         free-webinar-planner
[Stage 4]   최종 기획안 통합         compiler

[후속 — 수동 실행]
            CRM 시퀀스              sequence-planner       ← Stage 4 후 자동
            강의 대본               webinar-script
            상세페이지 요청서        detail-page-designer
            광고 카피               ad-copywriter          ← 상세페이지 후 자동

[품질 검증 — 자동 삽입]
            기획 품질 검토           reviewer
            고객 언어 정합성 검증    voice-validator
            법규·광고 규정 검토      law-checker

[회고 연결]
            회고 인사이트 반영       retrospective-linker
```

★★★ = 사람이 반드시 선택해야 하는 결정점. AI 자동 결정 절대 금지.

---

## 핵심 설계 원칙

**1. 고객 언어 우선**
"우리가 생각하는 고객 문제"와 "고객이 실제로 말하는 문제"는 다를 수 있다.
keyword-researcher가 유튜브·탈잉·크몽에서 실제 고객 언어를 수집하고,
voice-validator가 기획안 언어와 대조해 괴리를 찾는다.
카피는 항상 고객이 쓰는 언어를 우선으로 쓴다.

**2. 단 하나의 콘셉트 라인**
광고·상세페이지·CRM이 각자 다른 표현을 쓰면 메시지가 분산된다.
Stage 1C에서 Core Concept Line 하나를 확정하고,
이후 모든 카피(광고 후킹, 랜딩 히어로, CRM 컨셉)가 이 한 줄을 기준으로 작성된다.

```
공식: [타깃 핵심 문제]를 [방법론]으로 [기간] 안에 해결하는 [법칙/공식/비법 이름]
```

**3. 팔리지 않는 상품은 기획하지 않는다**
Stage 0.6 funnel-validator가 세 가지를 검증한다:

- 단가 적합성: 이 가격대에 실제로 사는 시장이 있는가
- 대체재 강도: 무료로 해결 가능하거나 경쟁이 너무 센가
- USP 명확성: 왜 이 상품이어야 하는지 한 줄로 설명되는가
  세 기준 중 하나라도 적신호면 go/no-go를 Nova에게 명시적으로 제시한다.

**4. 법규 자동 검토**
표시광고법 위반 패턴("반드시", "무조건", "100%", 수익 보장 등)을
law-checker가 자동으로 스캔한다.
기획안이 완성돼도 광고 집행 전에 반드시 통과해야 한다.

**5. 실적 데이터 기반 CRM**
CRM 시퀀스는 실제 운영 데이터를 기반으로 설계됐다:

- 라이브 중 30분 후 발송이 전체 입장 클릭의 34.6% 차지
- 노션 집약 허브가 결제 직접 링크보다 2.7배 클릭 효과적
- 다음날 오전 카카오가 전체 구간 중 클릭 1위

---

## 에이전트별 역할 한 줄 요약

| 에이전트             | 역할                                                   |
| -------------------- | ------------------------------------------------------ |
| context-loader       | 미팅 노트를 구조화된 데이터로 변환                     |
| market-researcher    | 경쟁 상품 조사 + 단가·인지 가치 계산                   |
| keyword-researcher   | 유튜브·탈잉·크몽에서 고객 실제 언어 수집 (PQR2 프레임) |
| revenue-checkpoint   | 매출 시뮬레이터 입력값 3개 시나리오 제안               |
| funnel-validator     | 단가·대체재·USP 3기준으로 go/no-go 판단                |
| paid-planner         | 유료 상품 기획 전체 (페르소나 → 약속/가격 → 커리큘럼)  |
| hook-designer        | 무료/유료 가치 분배 + 후킹 카피 후보 3개               |
| free-webinar-planner | 무료 웨비나 2시간 기획 (강의 + 세일즈)                 |
| compiler             | 모든 working 파일을 최종 기획안 JSON으로 통합          |
| reviewer             | 기획 품질·논리·설득력 비판적 검토                      |
| voice-validator      | 기획안 언어 vs 고객 실제 언어 정합성 검증              |
| law-checker          | 표시광고법 + 도메인 규제 위반 스캔                     |
| sequence-planner     | 웨비나 D-11~D+2 CRM 시퀀스 18개 메시지 작성            |
| webinar-script       | 무료 웨비나 실제 발표 대본 12섹션                      |
| detail-page-designer | 유료/무료 상세페이지 요청서 (섹션 0~8)                 |
| ad-copywriter        | 릴스 스크립트 + 메타 이미지 광고 카피 3각도            |
| retrospective-linker | 회고 인사이트를 다음 기획에 자동 반영                  |

---

## 에이전트 간 데이터 흐름

```
meeting_notes.md
    │
    ▼
00_context.json          (context-loader)
    │
    ▼
00b_market.json          (market-researcher)
    │
    ▼
00c_keywords.json        (keyword-researcher)  ← 고객 실제 언어
    │
    ▼
00d_revenue_sim.json     (revenue-checkpoint)
    │
    ▼
00e_funnel_fit.json      (funnel-validator)    ← go/no-go
    │
    ▼
01a_persona.json         (paid-planner 1A)     ← 페르소나·페인포인트
01b_promise.json         (paid-planner 1B)     ← 약속·가격 [Nova 선택]
01c_paid_full.json       (paid-planner 1C)     ← 커리큘럼·Core Concept Line [Nova 선택]
    │
    ▼
02_hook.json             (hook-designer)       ← 후킹 [Nova 선택]
    │
    ▼
03_free_full.json        (free-webinar-planner)
    │
    ▼
paid_plan.json           (compiler)            ← 최종 유료 기획안
free_plan.json           (compiler)            ← 최종 무료 기획안
    │
    ├── sequence_plan.md     (sequence-planner)
    ├── webinar_script.md    (webinar-script)
    ├── detail_page_paid.md  (detail-page-designer)
    ├── detail_page_free.md  (detail-page-designer)
    ├── ad_copy_paid.md      (ad-copywriter)
    └── ad_copy_free.md      (ad-copywriter)
```

자동 검증 에이전트는 각 단계에 삽입됨:

- 1A 완료 후: reviewer + voice-validator 동시 실행
- 1C 완료 후: reviewer + law-checker 동시 실행
- Stage 2 완료 후: law-checker 실행

---

## 이 시스템이 커버하지 않는 것

- 라이브 세일즈 현장 운영 전략
- 웨비나 이탈을 줄이는 콘텐츠 내부 구성 감각
- 고객사별 세일즈 방식 판단
- 셀프런칭 부적합 고객 유형 판단
- 실제 성과 사례·실패 사례 경험
- 강의안 작성 방식을 고객사에게 요청하는 방법

위 내용은 매니저(Nova)의 직접 경험에서 나온 것으로, 별도 문서로 보완됩니다.
