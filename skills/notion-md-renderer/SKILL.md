# notion-md-renderer — Skill Placeholder

> 산출물 JSON → Notion 붙여넣기용 마크다운 렌더
> 본문은 부록 B 이후 단계에서 작성 예정.

## 역할

paid_plan.json / free_plan.json을 Notion에 붙여넣기 가능한 마크다운으로 변환. Stage 4 컴파일에서만 호출.

## 트리거

Stage 4: 컴파일 단계.

## 스크립트

- `scripts/render.py` — JSON 입력, Notion 호환 마크다운 출력

## references/

- `references/notion-md-spec.md` — Notion 호환 마크다운 규칙 (헤딩 레벨, 콜아웃 블록 등)

## I/O 개요

- **입력**: `paid_plan.json` 또는 `free_plan.json` 경로
- **출력**: `*.notion.md` 파일 (Notion 붙여넣기 호환)

## 자동 거부

- Notion 자동 쓰기 불가 — `/sync-notion` 명시 명령에서만 실제 업로드.

## TODO

- [ ] SKILL.md 본문 사용법·예시 작성
- [ ] scripts/render.py 구현
- [ ] references/notion-md-spec.md 작성
