# /approve stage-N | 1a | 1b | 1c

현재 단계 산출물을 승인하고 다음 단계로 진행을 허가한다.

## 용도

각 Stage 또는 paid-planner 내부 단계(1a/1b/1c) 산출물을 Nova가 확인 후 명시 승인. 승인 없이는 다음 단계 자동 진행 금지.

## 사용법

```
/approve stage-0
/approve stage-1
/approve 1a
/approve 1b
/approve 1c
/approve stage-2
/approve stage-3
/approve stage-4
```

## 동작

1. `state.json`의 `approved` 배열에 해당 단계 + 타임스탬프 기록
2. `checkpoints.log`에 승인 이벤트 추가
3. 메인 오케스트레이터에 다음 단계 호출 허가

## TODO

- [ ] 본문 구현 (부록 B 6번)
