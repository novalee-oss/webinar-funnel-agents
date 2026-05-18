# schema-validator

모든 산출물 JSON이 정의된 스키마를 통과하는지 자동 검증하는 결정론적 스킬.
스키마 미통과 산출물은 다음 단계 입력으로 사용할 수 없다.

## 의존성

```bash
pip install jsonschema
```

## 사용법

```bash
python .claude/skills/schema-validator/scripts/validate.py <data_file> <schema_file> [--quiet]
```

| 인자          | 설명                                                 |
| ------------- | ---------------------------------------------------- |
| `data_file`   | 검증할 JSON 파일 경로 (작업 디렉토리 기준 상대 경로) |
| `schema_file` | 스키마 JSON 파일 경로                                |
| `--quiet`     | pass 시 출력 생략 (CI 스크립트용)                    |

## 종료 코드

| 코드 | 의미                                             |
| ---- | ------------------------------------------------ |
| `0`  | pass — 스키마 통과                               |
| `1`  | fail — 위반 항목 있음                            |
| `2`  | error — 파일 없음 / JSON 파싱 실패 / 의존성 없음 |

## I/O 스키마

### 출력 (stdout, JSON)

**pass**

```json
{
  "result": "pass",
  "violations": [],
  "data_file": "working/01a_persona.json"
}
```

**fail**

```json
{
  "result": "fail",
  "violations": [
    {
      "path": "target_problem.painpoints",
      "message": "[{'who': '...', ...}] is too short",
      "schema_path": "properties.target_problem.properties.painpoints.minItems"
    }
  ],
  "violation_count": 1,
  "data_file": "working/01a_persona.json"
}
```

## 스키마 파일 위치

| 스키마    | 경로                                         |
| --------- | -------------------------------------------- |
| profile   | `.claude/docs/schemas/profile.schema.json`   |
| state     | `.claude/docs/schemas/state.schema.json`     |
| paid_plan | `.claude/docs/schemas/paid_plan.schema.json` |
| free_plan | `.claude/docs/schemas/free_plan.schema.json` |

## 에이전트별 호출 시점

| 에이전트                       | 검증 대상                                        | 스키마                  |
| ------------------------------ | ------------------------------------------------ | ----------------------- |
| context-loader (Stage 0)       | `profile.json`                                   | `profile.schema.json`   |
| paid-planner 1C (Stage 1C)     | `working/01c_paid_full.json`                     | `paid_plan.schema.json` |
| free-webinar-planner (Stage 3) | `working/03_free_full.json`                      | `free_plan.schema.json` |
| compiler (Stage 4)             | `output/paid_plan.json`, `output/free_plan.json` | 각 스키마               |

## 예시

```bash
# Stage 4: 유료 기획안 최종 검증
python .claude/skills/schema-validator/scripts/validate.py \
  output/paid_plan.json \
  .claude/docs/schemas/paid_plan.schema.json

# profile.json 갱신 후 검증
python .claude/skills/schema-validator/scripts/validate.py \
  profile.json \
  .claude/docs/schemas/profile.schema.json --quiet
```

## 실패 시 처리 (SYSTEM.md §8)

1. 재시도 1회 (에이전트가 산출물 수정 후 재생성)
2. 재시도 후도 실패 → Nova 에스컬레이션. 통과 강요 금지.
