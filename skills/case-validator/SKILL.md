# case-validator

사례(사회적 증거) 후보 목록에서 consent 메타데이터를 자동 검증하는 결정론적 스킬.
**consent 없는 사례는 자동 탈락. 에이전트가 임의로 통과시킬 수 없다.**

## 의존성

없음 (표준 라이브러리만 사용).

---

## 사용법

```bash
python .claude/skills/case-validator/scripts/check.py <cases_json_file> [--min-approved N]
```

| 인자              | 기본값 | 설명                                      |
| ----------------- | ------ | ----------------------------------------- |
| `cases_json_file` | 필수   | 사례 후보가 담긴 JSON 파일                |
| `--min-approved`  | `3`    | 통과 사례 최소 요구 수 (Stage 1C 기준 ≥3) |

### 종료 코드

| 코드 | 의미                                                  |
| ---- | ----------------------------------------------------- |
| `0`  | 검증 완료 + 최소 요구 수 충족                         |
| `1`  | 검증 완료이나 통과 사례 부족 → Nova 에스컬레이션 필요 |
| `2`  | 입력 오류 (파일 없음, JSON 파싱 실패, 형식 오류)      |

---

## 입력 JSON 형식

배열 또는 `{"cases": [...]}` 두 형식 모두 허용.

```json
[
  {
    "id": "case-001",
    "summary": "12주 수강 후 첫 고객 유치",
    "result": "월 매출 300만 원 달성",
    "consent": {
      "granted": true,
      "scope": "anonymized",
      "granted_at": "2026-03-10",
      "granted_by": "수강생-A"
    }
  },
  {
    "id": "case-002",
    "summary": "...",
    "consent": null
  }
]
```

### consent 필드 검증 기준

| 조건                             | 결과     | 탈락 사유                 |
| -------------------------------- | -------- | ------------------------- |
| `consent` 필드 없음              | 탈락     | `consent_missing`         |
| `consent: null`                  | 탈락     | `consent_missing`         |
| `granted: false`                 | 탈락     | `consent_not_granted`     |
| `granted` 필드 없음              | 탈락     | `consent_granted_missing` |
| `scope` 필드 없음                | 탈락     | `consent_scope_missing`   |
| `scope`가 유효하지 않은 값       | 탈락     | `consent_scope_invalid`   |
| `granted: true` + 유효한 `scope` | **통과** | —                         |

### 유효한 scope 값

| 값             | 의미                   |
| -------------- | ---------------------- |
| `full`         | 원문 그대로 사용 가능  |
| `anonymized`   | 익명 가공 후 사용 가능 |
| `excerpt_only` | 일부 발췌만 사용 가능  |

---

## I/O 스키마

### 출력 (stdout, JSON)

**충분한 통과 사례 (exit 0)**

```json
{
  "approved_count": 4,
  "rejected_count": 1,
  "sufficient": true,
  "min_required": 3,
  "approved": [
    {
      "id": "case-001",
      "scope": "anonymized",
      "data": { "id": "case-001", "summary": "...", "consent": { ... } }
    }
  ],
  "rejected": [
    {
      "id": "case-002",
      "reason": "consent_missing",
      "data": { "id": "case-002", "summary": "...", "consent": null }
    }
  ]
}
```

**통과 사례 부족 (exit 1)**

```json
{
  "approved_count": 1,
  "rejected_count": 3,
  "sufficient": false,
  "min_required": 3,
  "approved": [...],
  "rejected": [...],
  "escalation_required": true,
  "escalation_message": "consent 통과 사례 1건 — 최소 3건 필요. Nova 에스컬레이션: 추가 사례 확보 또는 최소 요구 수 조정 결정 필요."
}
```

---

## 에이전트별 호출 시점

| 에이전트                       | 시점                                  | min-approved |
| ------------------------------ | ------------------------------------- | ------------ |
| paid-planner (Stage 1C)        | 사례 선별 직전                        | `3`          |
| free-webinar-planner (Stage 3) | 1C 통과 사례 재사용 전 consent 재검증 | `2`          |

---

## 예시

```bash
# Stage 1C: 사례 후보 검증 (최소 3건)
python .claude/skills/case-validator/scripts/check.py \
  inputs/cases.json

# Stage 3: 재사용 사례 재검증 (최소 2건)
python .claude/skills/case-validator/scripts/check.py \
  working/selected_cases.json --min-approved 2
```

---

## 실패 시 처리 (SYSTEM.md §8)

**통과 사례 부족 (exit 1)**
→ 재시도 없음. 즉시 Nova 에스컬레이션.
→ 에스컬레이션 메시지: `result.escalation_message` 그대로 보고.
→ Nova 결정 사항: 추가 사례 확보 / `--min-approved` 조정 / 작업 보류.

**consent 없는 사례 통과 요청이 들어올 경우**
→ 거부. "consent 메타데이터 없는 사례는 자동 사용 불가 (SYSTEM.md §4, §5-④)" 안내.
→ Nova가 직접 동의를 받아 `consent` 필드를 추가한 뒤 재검증.
