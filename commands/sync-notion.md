# /sync-notion

output/\*.notion.md를 Notion에 명시적으로 업로드한다.

## 용도

Notion 자동 쓰기는 금지. 이 커맨드를 명시 실행해야만 산출물이 Notion에 기록됨.

## 사용법

```
/sync-notion
```

## 전제 조건

- Stage 4 컴파일 완료 (output/\*.notion.md 존재)
- 클라이언트 CLAUDE.md에 Notion page_id 설정됨

## 동작

1. `output/paid_plan.notion.md` → 클라이언트 Notion 페이지에 업로드
2. `output/free_plan.notion.md` → 클라이언트 Notion 페이지에 업로드
3. 업로드 결과(page_id·타임스탬프) 보고

## TODO

- [ ] 본문 구현 (부록 B 6번)
- [ ] notion-fetcher·Notion API 연동 확인
