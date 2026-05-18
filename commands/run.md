# /run reviewer [stage-N | all]

reviewer 에이전트를 명시 호출해 비판적 검토를 실행한다.

## 용도

특정 Stage 산출물 또는 전체 산출물에 대한 비판적 검토 요청. 자동 호출 없음 — 항상 명시 호출만.

## 사용법

```
/run reviewer stage-1    # Stage 1 산출물 검토
/run reviewer stage-2    # Stage 2 산출물 검토
/run reviewer all        # 전체 산출물 검토
```

## 동작

1. 지정 대상 산출물 경로를 reviewer에게 전달
2. reviewer가 `working/review_notes.md` 생성
3. Nova에게 결과 보고 (수정 여부는 Nova 결정)

## TODO

- [ ] 본문 구현 (부록 B 6번)
