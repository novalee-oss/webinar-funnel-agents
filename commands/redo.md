# /redo paid | free

paid-planner 또는 free-webinar-planner 전체를 재실행한다.

## 용도

유료 또는 무료 기획안 전체를 처음부터 다시 빚어야 할 때.

## 사용법

```
/redo paid    # paid-planner 전체(1A~1C) 재실행. Hook 재사용 여부 별도 확인.
/redo free    # free-webinar-planner 전체 재실행. Hook은 그대로 사용.
```

## 동작 — /redo paid

1. 1A/1B/1C 및 이후 모든 산출물 stale 마킹
2. Hook 재사용 여부 Nova에게 명시 확인 (자동 결정 금지)
3. paid-planner 1A부터 재호출

## 동작 — /redo free

1. Stage 3 산출물 stale 마킹
2. free-webinar-planner 재호출 (02_hook.json은 그대로 사용)

## TODO

- [ ] 본문 구현 (부록 B 6번)
- [ ] /redo paid 시 hook 재사용 디폴트 결정 (§4.2 미해결 항목)
