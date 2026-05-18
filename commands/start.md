# /start product-planning {product}

신규 상품 기획 작업을 시작한다.

## 용도

클라이언트 폴더(`~/로켓런칭/{client}/`)에서 실행. 지정한 상품 이름으로 작업 폴더를 초기화하고 Stage 0(context-loader)을 호출한다.

## 사용법

```
/start product-planning {상품명}
```

## 동작 순서

1. `{상품명}/inputs/meeting_notes.md` 존재 여부 확인
2. `{상품명}/working/` 및 `{상품명}/output/` 디렉토리 생성
3. `state.json` 초기화 (stage: "0", approved: [], stale: [])
4. context-loader 호출

## TODO

- [ ] 본문 구현 (부록 B 6번)
