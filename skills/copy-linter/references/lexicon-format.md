# 금기어 사전 파일 형식 (lexicon-format)

클라이언트별 `lexicon/forbidden-terms.json` 파일의 스키마 정의.
`copy-linter`가 이 파일을 읽어 카피 텍스트를 검사한다.

---

## 파일 위치

```
~/로켓런칭/{client}/lexicon/forbidden-terms.json
```

copy-linter는 **작업 디렉토리 기준** `./lexicon/forbidden-terms.json`을 기본 경로로 읽는다.

---

## JSON 스키마

```json
{
  "version": "1.0",
  "client_id": "string",
  "updated_at": "YYYY-MM-DD",
  "terms": [
    {
      "term": "string (검사할 단어 또는 구)",
      "severity": "fatal | warn",
      "category": "string",
      "reason": "string (왜 금기어인지)",
      "alternatives": ["string", "..."]
    }
  ]
}
```

### severity 기준

| 값      | 의미                                               | copy-linter 처리                                                   |
| ------- | -------------------------------------------------- | ------------------------------------------------------------------ |
| `fatal` | 절대 사용 불가. 법적 리스크 또는 강한 도메인 규제. | 검출 즉시 `pass: false`. 재시도 1회 → 재검출 시 Nova 에스컬레이션. |
| `warn`  | 사용 지양. 브랜드 톤 위반 또는 약한 규제.          | 검출 시 `pass: false`이나 컨텍스트에 따라 Nova가 허용 판단 가능.   |

### category 예시

| 카테고리           | 설명                              | 도메인 예시  |
| ------------------ | --------------------------------- | ------------ |
| `medical_claim`    | 의료적 효능 주장                  | 페이션트퍼널 |
| `guarantee`        | 성과 보장 표현 (의도치 않은 강도) | 공통         |
| `exaggeration`     | 과장 표현                         | 공통         |
| `prohibited_title` | 사용 불가 직함                    | 도메인별     |
| `brand_tone`       | 브랜드 톤 위반 어휘               | 클라이언트별 |

---

## 예시 파일

### 페이션트퍼널 (의료법 적용)

```json
{
  "version": "1.0",
  "client_id": "patientfunnel",
  "updated_at": "2026-05-12",
  "terms": [
    {
      "term": "치료",
      "severity": "fatal",
      "category": "medical_claim",
      "reason": "의료법상 의료인만 사용 가능한 표현",
      "alternatives": ["개선", "변화", "관리"]
    },
    {
      "term": "완치",
      "severity": "fatal",
      "category": "medical_claim",
      "reason": "의료적 효능 보장 표현",
      "alternatives": ["호전", "개선 경험"]
    },
    {
      "term": "100% 효과",
      "severity": "fatal",
      "category": "guarantee",
      "reason": "근거 없는 효과 보장",
      "alternatives": ["실제 경험 기반", "다수 사례에서"]
    },
    {
      "term": "의사 추천",
      "severity": "warn",
      "category": "prohibited_title",
      "reason": "사실 확인 없이 사용 시 문제",
      "alternatives": ["전문가 검토", "사례 기반"]
    }
  ]
}
```

### 우두머리 (두피문신 도메인)

```json
{
  "version": "1.0",
  "client_id": "wuduri",
  "updated_at": "2026-05-12",
  "terms": [
    {
      "term": "문신 제거",
      "severity": "fatal",
      "category": "out_of_scope",
      "reason": "상품 범위 외 서비스 암시",
      "alternatives": ["시술 조정", "수정 시술"]
    },
    {
      "term": "무조건",
      "severity": "warn",
      "category": "exaggeration",
      "reason": "과장 표현. 브랜드 톤 위반.",
      "alternatives": ["대부분의 경우", "실제 수강생 기준"]
    }
  ]
}
```

---

## 검색 방식

copy-linter는 **단순 문자열 포함 검사**를 기본으로 한다.

- 대소문자 무시 (한국어는 해당 없음)
- 부분 일치 허용 (예: "치료"는 "치료법", "치료 과정"에서도 검출)
- 검출 위치(character offset)를 함께 반환해 컨텍스트 확인 가능하게 함
