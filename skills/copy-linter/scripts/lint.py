#!/usr/bin/env python3
"""
copy-linter lint: 카피 텍스트에서 도메인 금기어를 검사.
금기어 0개 = pass. 1개 이상 = fail.

사용법:
    python lint.py <text_or_file> [--lexicon lexicon/forbidden-terms.json]
    echo "카피 텍스트" | python lint.py - [--lexicon ...]

종료 코드:
    0 = pass (금기어 없음)
    1 = fail (금기어 검출)
    2 = 입력 오류
"""
import sys
import json
import argparse
from pathlib import Path

DEFAULT_LEXICON = "./lexicon/forbidden-terms.json"


def load_json(path: str) -> tuple:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"파일 없음: {path}"
    except json.JSONDecodeError as e:
        return None, f"JSON 파싱 실패: {e}"


def load_text(source: str) -> tuple:
    """텍스트 소스 읽기: 파일 경로, '-'(stdin), 또는 그대로 문자열."""
    if source == "-":
        return sys.stdin.read(), None
    p = Path(source)
    if p.exists() and p.suffix in (".txt", ".md", ".json"):
        try:
            return p.read_text(encoding="utf-8"), None
        except Exception as e:
            return None, str(e)
    # 짧은 문자열은 그대로 텍스트로 취급
    return source, None


def lint(text: str, terms: list) -> list:
    """
    금기어 검사. 검출 항목 리스트 반환.
    각 항목: {term, severity, category, reason, alternatives, positions}
    """
    hits = []
    for entry in terms:
        term = entry.get("term", "")
        if not term:
            continue

        positions = []
        start = 0
        while True:
            idx = text.find(term, start)
            if idx == -1:
                break
            # 앞뒤 20자 컨텍스트
            ctx_start = max(0, idx - 20)
            ctx_end = min(len(text), idx + len(term) + 20)
            context = text[ctx_start:ctx_end].replace("\n", " ")
            positions.append({"offset": idx, "context": f"...{context}..."})
            start = idx + 1

        if positions:
            hits.append({
                "term": term,
                "severity": entry.get("severity", "warn"),
                "category": entry.get("category", ""),
                "reason": entry.get("reason", ""),
                "alternatives": entry.get("alternatives", []),
                "positions": positions,
                "hit_count": len(positions),
            })

    return hits


def main():
    parser = argparse.ArgumentParser(
        description="카피 텍스트 금기어 검사",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python lint.py working/01b_promise.json
  python lint.py "12주 안에 치료 가능한 과정"
  echo "카피 텍스트" | python lint.py - --lexicon ./lexicon/forbidden-terms.json
        """,
    )
    parser.add_argument("text", help="검사할 텍스트, 파일 경로, 또는 '-'(stdin)")
    parser.add_argument(
        "--lexicon",
        default=DEFAULT_LEXICON,
        help=f"금기어 사전 경로 (기본값: {DEFAULT_LEXICON})",
    )
    parser.add_argument(
        "--fatal-only",
        action="store_true",
        help="fatal 심각도만 검사 (warn 무시)",
    )
    args = parser.parse_args()

    # 텍스트 로드
    text, err = load_text(args.text)
    if err:
        print(json.dumps({"error": err}, ensure_ascii=False))
        sys.exit(2)

    # 사전 로드
    lexicon, err = load_json(args.lexicon)
    if err:
        print(json.dumps({"error": f"금기어 사전 로드 실패: {err}"}, ensure_ascii=False))
        sys.exit(2)

    terms = lexicon.get("terms", [])
    if args.fatal_only:
        terms = [t for t in terms if t.get("severity") == "fatal"]

    hits = lint(text, terms)

    fatal_hits = [h for h in hits if h["severity"] == "fatal"]
    warn_hits = [h for h in hits if h["severity"] == "warn"]
    passed = len(hits) == 0

    result = {
        "pass": passed,
        "fatal_count": len(fatal_hits),
        "warn_count": len(warn_hits),
        "hits": hits,
        "lexicon": {
            "client_id": lexicon.get("client_id", ""),
            "version": lexicon.get("version", ""),
            "total_terms_checked": len(terms),
        },
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
