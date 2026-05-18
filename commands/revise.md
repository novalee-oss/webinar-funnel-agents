# /revise stage-N --reason "..."

지정 단계를 재실행하고 이후 산출물을 stale 마킹한다.

## 용도

특정 Stage 산출물에 문제가 있을 때 해당 단계부터 다시 작업. 이후 단계 산출물은 자동으로 stale 마킹되며 자동 재실행은 없음.

## 사용법

```
/revise stage-1 --reason "페르소나 타깃이 실제 클라이언트와 다름"
/revise 1b --reason "가격 후보 근거 불충분"
```

## 동작

1. 지정 단계 이후의 모든 working/\*.json에 stale 플래그 설정
2. `state.json` 업데이트
3. `checkpoints.log`에 revise 이벤트 + reason 기록
4. 해당 단계 에이전트 재호출

## TODO

- [ ] 본문 구현 (부록 B 6번)
