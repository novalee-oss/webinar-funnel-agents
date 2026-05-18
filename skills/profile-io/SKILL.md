# profile-io

클라이언트 누적 컨텍스트 `profile.json`의 읽기·쓰기·차분 계산을 담당하는 결정론적 스킬.
항상 **작업 디렉토리(클라이언트 폴더) 기준 상대 경로**로 동작한다.

## 의존성

```bash
pip install jsonschema   # 스키마 검증용 (read.py, write.py)
```

---

## read.py — profile.json 읽기 + 스키마 검증

### 사용법

```bash
python .claude/skills/profile-io/scripts/read.py [profile_path] [--no-validate]
```

| 인자            | 기본값           | 설명                   |
| --------------- | ---------------- | ---------------------- |
| `profile_path`  | `./profile.json` | 읽을 profile.json 경로 |
| `--no-validate` | —                | 스키마 검증 생략       |

### 출력 (stdout, JSON)

**성공 (스키마 통과)**

```json
{
  "profile": { "client_id": "wuduri", ... },
  "validation": { "result": "pass", "violations": [] }
}
```

**실패 (스키마 위반)**

```json
{
  "profile": { ... },
  "validation": {
    "result": "fail",
    "violations": [
      { "path": "revenue_target", "message": "'amount' is a required property" }
    ]
  }
}
```

### 종료 코드

| 코드 | 의미                       |
| ---- | -------------------------- |
| `0`  | 성공                       |
| `1`  | 스키마 위반                |
| `2`  | 파일 없음 / JSON 파싱 실패 |

---

## write.py — profile.json 갱신 + 검증

스키마 통과 시에만 파일을 쓴다. 기존 파일은 `.json.bak`으로 백업.

### 사용법

```bash
python .claude/skills/profile-io/scripts/write.py <new_profile.json> [--target profile.json]
```

| 인자               | 기본값           | 설명                      |
| ------------------ | ---------------- | ------------------------- |
| `new_profile.json` | 필수             | 새 profile 내용 JSON 파일 |
| `--target`         | `./profile.json` | 쓸 대상 파일 경로         |

### 출력 (stdout, JSON)

**성공**

```json
{
  "written": true,
  "target": "./profile.json",
  "backup": "./profile.json.bak",
  "validation": { "result": "pass", "violations": [] },
  "diff": {
    "type": "update",
    "added": [],
    "removed": [],
    "changed": [
      {
        "key": "revenue_target",
        "before": "{dict, 키 3개}",
        "after": "{dict, 키 3개}"
      }
    ]
  }
}
```

**실패 (스키마 위반 — 파일 쓰지 않음)**

```json
{
  "written": false,
  "reason": "스키마 검증 실패 — 파일 쓰지 않음",
  "validation": { "result": "fail", "violations": [...] }
}
```

### 종료 코드

| 코드 | 의미                         |
| ---- | ---------------------------- |
| `0`  | 성공 (파일 쓰기 완료)        |
| `1`  | 스키마 위반 (파일 쓰지 않음) |
| `2`  | 파일 오류                    |

---

## diff.py — 두 profile 간 차분 계산

Stage 0 완료 후 Nova에게 보고하는 차분 리포트 생성에 사용.

### 사용법

```bash
python .claude/skills/profile-io/scripts/diff.py <old.json> <new.json> [--summary-only]
```

| 인자             | 설명                          |
| ---------------- | ----------------------------- |
| `old.json`       | 이전 profile (또는 .bak 파일) |
| `new.json`       | 새 profile                    |
| `--summary-only` | 변경된 최상위 키 목록만 출력  |

### 출력 예시

```json
{
  "total_changes": 2,
  "changes": [
    {
      "path": "revenue_target.amount",
      "before": "5000000",
      "after": "8000000",
      "type": "changed"
    },
    {
      "path": "past_plans",
      "before": "[2개 항목]",
      "after": "[3개 항목]",
      "type": "list_changed"
    }
  ],
  "no_changes": false
}
```

---

## 호출 순서 — Stage 0 전형적 패턴

```bash
# 1. 기존 profile 읽기 + 검증
python .claude/skills/profile-io/scripts/read.py

# 2. (LLM이 미팅 노트 분석 후 new_profile.json 생성)

# 3. 새 profile 쓰기
python .claude/skills/profile-io/scripts/write.py /tmp/new_profile.json

# 4. 차분 리포트 생성 (Nova에게 보고)
python .claude/skills/profile-io/scripts/diff.py profile.json.bak profile.json
```

## 주의사항

- `write.py`는 스키마 통과 시에만 파일을 쓴다. 실패 시 기존 파일 변경 없음.
- `updated_at` 필드는 `write.py`가 현재 시각(UTC ISO 8601)으로 자동 갱신한다.
- profile.json에 PII(개인 연락처 등)를 직접 저장하지 않는다. `profile.pii.json`으로 분리 권장(§부록 D.4).
