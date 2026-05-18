# web-research-wrapper — Skill Placeholder

> web search 호출 한도·출처 메타데이터 부착
> 본문은 부록 B 이후 단계에서 작성 예정.

## 역할

외부 web search 호출 횟수를 추적하고 출처 메타데이터를 결과에 부착. Nova 명시 승인 없이는 실행 불가.

## 트리거

Stage 1A·1C에서 Nova가 `/web-research approve` 명시 승인한 경우에만.

## 스크립트

- `scripts/wrapper.py` — 검색어 수신, 호출 횟수 체크(Stage당 최대 5회), 출처 메타데이터 부착

## I/O 개요

- **입력**: 검색어 문자열, 현재 Stage 식별자
- **출력**: `[{ "url": "...", "snippet": "...", "fetched_at": "..." }]`

## 자동 거부

- Stage당 호출 횟수 초과 시 자동 거부
- Nova 승인 없이 호출 시 자동 거부

## TODO

- [ ] SKILL.md 본문 사용법·예시 작성
- [ ] scripts/ 구현
