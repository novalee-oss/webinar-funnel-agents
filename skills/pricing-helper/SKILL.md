# pricing-helper — 가격 시나리오 시뮬레이션

## 역할

매출 목표·CAC 추정·전환율을 입력받아 저·중·고 가격 후보 3개의 시나리오 표를 생성한다.
가격 **선택**은 paid-planner의 Nova 결정 — 이 스킬은 수치 시뮬레이션만 한다.

## 트리거

Stage 1B: paid-planner가 가격 후보 3개를 제시하기 전.

## 스크립트

- `scripts/simulate.py` — 매출목표·CAC·전환율 인자를 받아 시나리오 표 출력

## 사용법

```bash
python .claude/skills/pricing-helper/scripts/simulate.py \
  --revenue-target 30000000 \
  --cac 200000 \
  --conversion-rates "0.01,0.02,0.03" \
  --target-students 20
```

### 인자

| 인자                 | 필수 | 기본값           | 설명                                   |
| -------------------- | ---- | ---------------- | -------------------------------------- |
| `--revenue-target`   | 필수 | —                | 캠페인 매출 목표 (원, 정수)            |
| `--cac`              | 선택 | 200000           | 예상 고객 획득 비용 (원, 정수)         |
| `--conversion-rates` | 선택 | "0.01,0.02,0.03" | 전환율 3개, 쉼표 구분                  |
| `--target-students`  | 선택 | 20               | 목표 수강생 수 (가격 앵커 계산에 사용) |

## 출력 (JSON)

```json
{
  "revenue_target": 30000000,
  "cac_assumption": 200000,
  "target_students_assumption": 20,
  "candidates": [
    {
      "level": "low",
      "amount": 1350000,
      "cac_assumption": 200000,
      "conversion_rate": 0.01,
      "required_leads": 2223,
      "required_students": 23,
      "projected_revenue": 31050000,
      "margin_per_student": 1150000
    },
    {
      "level": "mid",
      "amount": 1500000,
      "cac_assumption": 200000,
      "conversion_rate": 0.02,
      "required_leads": 1000,
      "required_students": 20,
      "projected_revenue": 30000000,
      "margin_per_student": 1300000
    },
    {
      "level": "high",
      "amount": 1750000,
      "cac_assumption": 200000,
      "conversion_rate": 0.03,
      "required_leads": 572,
      "required_students": 18,
      "projected_revenue": 31500000,
      "margin_per_student": 1550000
    }
  ]
}
```

### 출력 필드 설명

| 필드                 | 설명                                                   |
| -------------------- | ------------------------------------------------------ |
| `level`              | low / mid / high                                       |
| `amount`             | 해당 가격 (원)                                         |
| `conversion_rate`    | 적용된 전환율                                          |
| `required_leads`     | 매출 목표 달성을 위한 필요 리드 수 (신청 랜딩 유입 수) |
| `required_students`  | 매출 목표 달성을 위한 필요 결제 수강생 수              |
| `projected_revenue`  | 예상 매출 (원)                                         |
| `margin_per_student` | 학생 1인당 마진 (amount - cac)                         |

## 종료 코드

| 코드 | 의미                                      |
| ---- | ----------------------------------------- |
| 0    | 성공                                      |
| 2    | 입력 오류 (conversion-rates 형식 오류 등) |

## paid-planner에서 사용하는 방식

1. `profile.json`의 `revenue_target.amount`, `estimated_cac` 읽기
2. 전환율은 도메인·과거 데이터 기반으로 3개 설정 (없으면 0.01/0.02/0.03 기본값)
3. `simulate.py` 실행 → JSON 파싱
4. `candidates` 배열을 `01b_promise.json`의 `price_candidates`에 매핑
5. Nova에게 3개 후보 표로 보고 → Nova가 선택

## 주의

- 시뮬레이션 결과는 참고 수치다. 시장 상황·계절성·경쟁 상품에 따라 실제 전환율은 달라진다.
- `margin_per_student`가 음수인 경우(CAC > price) 반드시 Nova에게 보고한다.
- `required_leads`가 현실적으로 불가능한 수준(예: 10,000명 이상)이면 Nova에게 에스컬레이션한다.
