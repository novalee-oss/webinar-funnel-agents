# notion-fetcher — Skill Placeholder

> Notion page_id → 마크다운 변환
> 본문은 부록 B 이후 단계에서 작성 예정.

## 역할

Notion page_id를 받아 페이지 본문을 마크다운 텍스트로 반환. 과거 기획서·자산 참조에 사용.

## 트리거

- Stage 0: 이전 기획서 링크 정리 시
- Stage 1A·1C: 과거 자산 참조 시

## 스크립트

- `scripts/fetch.py` — page_id 인자, Notion API 호출, 마크다운 반환

## I/O 개요

- **입력**: Notion `page_id` (문자열)
- **출력**: 마크다운 텍스트 문자열

## 자동 거부

- 이전 기획서·과거 자산 **무허가 재사용 불가** — 출처 표기 필수.

## TODO

- [ ] SKILL.md 본문 사용법·예시 작성
- [ ] scripts/fetch.py 구현 (Notion API 키는 환경변수로)
