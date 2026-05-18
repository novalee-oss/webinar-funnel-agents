# /web-research approve

Stage 1A 또는 1C에서 web search 보조를 명시 승인한다.

## 용도

외부 web search는 Nova 명시 승인 없이 자동 호출 금지. 이 커맨드로 해당 Stage의 web search 사용을 허가.

## 사용법

```
/web-research approve
```

## 제한

- Stage당 최대 5회 호출
- Stage 1A·1C에서만 유효
- 승인은 현재 Stage에 한정 (다른 Stage로 이월 안 됨)

## 동작

1. `state.json`에 web_research_approved: true 및 호출 잔여 횟수(5) 기록
2. web-research-wrapper 스킬 활성화

## TODO

- [ ] 본문 구현 (부록 B 6번)
