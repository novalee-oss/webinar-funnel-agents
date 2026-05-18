#!/usr/bin/env python3
"""
profile-io diff: 두 profile.json 간 구조적 차분 계산.

Stage 0에서 profile 업데이트 후 Nova에게 보고하는 차분 리포트 생성에 사용.

사용법:
    python diff.py <old_profile.json> <new_profile.json>

종료 코드:
    0 = 성공 (차분 없어도 0)
    2 = 파일 오류
"""
import sys
import json
import argparse
from pathlib import Path


def load_json(path: Path) -> tuple:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"파일 없음: {path}"
    except json.JSONDecodeError as e:
        return None, f"JSON 파싱 실패: {e}"


def deep_diff(old, new, path: str = "") -> list:
    """재귀적 차분. 변경 항목을 [{path, before, after}] 리스트로 반환."""
    changes = []

    if type(old) != type(new):
        changes.append({"path": path or "(root)", "before": _fmt(old), "after": _fmt(new)})
        return changes

    if isinstance(old, dict):
        all_keys = set(old) | set(new)
        for key in sorted(all_keys):
            child_path = f"{path}.{key}" if path else key
            if key not in old:
                changes.append({"path": child_path, "before": None, "after": _fmt(new[key]), "type": "added"})
            elif key not in new:
                changes.append({"path": child_path, "before": _fmt(old[key]), "after": None, "type": "removed"})
            else:
                changes.extend(deep_diff(old[key], new[key], child_path))
        return changes

    if isinstance(old, list):
        # 리스트는 길이 변화 + 전체 내용 변화만 보고 (항목별 추적은 id 기반으로 별도 처리)
        if old != new:
            changes.append({
                "path": path or "(root)",
                "before": f"[{len(old)}개 항목]",
                "after": f"[{len(new)}개 항목]",
                "type": "list_changed",
            })
        return changes

    # 스칼라
    if old != new:
        changes.append({
            "path": path or "(root)",
            "before": _fmt(old),
            "after": _fmt(new),
            "type": "changed",
        })
    return changes


def _fmt(value) -> str:
    if value is None:
        return "(없음)"
    if isinstance(value, str):
        return value[:120] + ("..." if len(value) > 120 else "")
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)[:120]
    return str(value)


def main():
    parser = argparse.ArgumentParser(description="두 profile.json 간 차분 계산")
    parser.add_argument("old", help="이전 profile.json 경로")
    parser.add_argument("new", help="새 profile.json 경로")
    parser.add_argument("--summary-only", action="store_true",
                        help="변경된 최상위 키 목록만 출력")
    args = parser.parse_args()

    old_data, err = load_json(Path(args.old))
    if err:
        print(json.dumps({"error": err}, ensure_ascii=False))
        sys.exit(2)

    new_data, err = load_json(Path(args.new))
    if err:
        print(json.dumps({"error": err}, ensure_ascii=False))
        sys.exit(2)

    changes = deep_diff(old_data, new_data)

    if args.summary_only:
        top_level = sorted({c["path"].split(".")[0] for c in changes})
        print(json.dumps({
            "changed_keys": top_level,
            "total_changes": len(changes),
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({
            "total_changes": len(changes),
            "changes": changes,
            "no_changes": len(changes) == 0,
        }, ensure_ascii=False, indent=2))

    sys.exit(0)


if __name__ == "__main__":
    main()
