# copy-linter

클라이언트 도메인 금기어 사전 기반으로 카피 텍스트를 자동 검사하는 결정론적 스킬.
금기어 0개 = pass. 1개 이상 = fail. **금기어 포함 카피 자동 통과 절대 금지.**

## 의존성

없음 (표준 라이브러리만 사용).

---

## 사용법

```bash
python .claude/skills/copy-linter/scripts/lint.py <text_or_file> [--lexicon 경로] [--fatal-only]
```

| 인자           | 기본값                           | 설명                                                        |
| -------------- | -------------------------------- | ----------------------------------------------------------- |
| `text`         | 필수                             | 검사할 텍스트, 파일 경로(`.txt/.md/.json`), 또는 `-`(stdin) |
| `--lexicon`    | `./lexicon/forbidden-terms.json` | 금기어 사전 경로 (작업 디렉토리 기준)                       |
| `--fatal-only` | —                                | `fatal` 심각도만 검사                                       |

### 종료 코드

| 코드 | 의미                                  |
| ---- | ------------------------------------- |
| `0`  | pass — 금기어 없음                    |
| `1`  | fail — 금기어 검출                    |
| `2`  | 입력 오류 (파일 없음, 사전 로드 실패) |

---

## I/O 스키마

### 출력 (stdout, JSON)

**pass**

```json
{
  "pass": true,
  "fatal_count": 0,
  "warn_count": 0,
  "hits": [],
  "lexicon": {
    "client_id": "wuduri",
    "version": "1.0",
    "total_terms_checked": 12
  }
}
```

**fail**

```json
{
  "pass": false,
  "fatal_count": 1,
  "warn_count": 1,
  "hits": [
    {
      "term": "치료",
      "severity": "fatal",
      "category": "medical_claim",
      "reason": "의료법상 의료인만 사용 가능한 표현",
      "alternatives": ["개선", "변화", "관리"],
      "positions": [
        { "offset": 42, "context": "...12주 안에 치료 가능한 과..." }
      ],
      "hit_count": 1
    },
    {
      "term": "무조건",
      "severity": "warn",
      "category": "exaggeration",
      "reason": "과장 표현. 브랜드 톤 위반.",
      "alternatives": ["대부분의 경우"],
      "positions": [{ "offset": 87, "context": "...무조건 성공하는..." }],
      "hit_count": 1
    }
  ],
  "lexicon": {
    "client_id": "patientfunnel",
    "version": "1.0",
    "total_terms_checked": 18
  }
}
```

---

## 금기어 사전 형식

`lexicon/forbidden-terms.json` 형식은 `references/lexicon-format.md` 참고.

핵심 구조:

```json
{
  "version": "1.0",
  "client_id": "string",
  "terms": [
    {
      "term": "치료",
      "severity": "fatal",
      "category": "medical_claim",
      "reason": "의료법상 의료인만 사용 가능",
      "alternatives": ["개선", "변화"]
    }
  ]
}
```

---

## 에이전트별 호출 시점

| 에이전트                       | 시점                     | 검사 대상                |
| ------------------------------ | ------------------------ | ------------------------ |
| paid-planner (Stage 1B)        | 약속·결과 카피 산출 직후 | `01b_promise.json` 전문  |
| free-webinar-planner (Stage 3) | 웨비나 카피 산출 직후    | `03_free_full.json` 전문 |

---

## 예시

```bash
# Stage 1B: 약속 카피 검사
python .claude/skills/copy-linter/scripts/lint.py \
  working/01b_promise.json

# 텍스트 직접 입력
python .claude/skills/copy-linter/scripts/lint.py \
  "12주 안에 첫 시술이 가능한 두피문신 전문가 양성 과정"

# fatal만 검사 (warn 무시)
python .claude/skills/copy-linter/scripts/lint.py \
  working/03_free_full.json --fatal-only

# 다른 클라이언트 사전 지정
python .claude/skills/copy-linter/scripts/lint.py \
  working/01b_promise.json \
  --lexicon ~/로켓런칭/페이션트퍼널/lexicon/forbidden-terms.json
```

---

## 실패 시 처리 (SYSTEM.md §8)

1. 금기어 검출 → 에이전트가 카피 수정 후 재생성 → 재검사 (1회)
2. 재검출 → **Nova 에스컬레이션. 통과 강요 금지.**
3. "컨텍스트상 괜찮다"는 에이전트 판단으로 금기어 묵인 금지. 항상 Nova 확인.

## 주의사항

- 검사는 **단순 문자열 포함 검사** (부분 일치 허용). "치료"는 "치료법", "치료 과정"에서도 검출됨.
- 금기어 사전이 없으면 오류 종료(exit 2). 클라이언트 폴더에 반드시 `lexicon/forbidden-terms.json` 구비.
- JSON 파일을 검사할 경우 파일 전체 텍스트를 검사하므로 필드명·키도 검사 대상에 포함됨. 필요 시 검사 대상 텍스트만 추출 후 전달.
