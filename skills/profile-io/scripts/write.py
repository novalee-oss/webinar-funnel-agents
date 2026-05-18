#!/usr/bin/env python3
"""
profile-io write: profile.json 갱신 + 스키마 검증 + 차분 리포트 출력.

새 profile 전체를 받아 검증 통과 시에만 기존 파일을 덮어쓴다.
기존 파일은 .bak으로 백업.

사용법:
    python write.py <new_profile_json> [--target profile.json]

    <new_profile_json>: 새 profile 내용이 담긴 JSON 파일 경로
    --target: 쓸 대상 profile.json 경로 (기본값: ./profile.json)

종료 코드:
    0 = 성공
    1 = 스키마 위반 (파일 쓰지 않음)
    2 = 파일 오류
"""
import sys
import json
import shutil
import argparse
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
CLAUDE_DIR = SKILL_DIR.parent.parent
SCHEMA_PATH = CLAUDE_DIR / "docs/schemas/profile.schema.json"


def load_json(path: Path) -> tuple:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"파일 없음: {path}"
    except json.JSONDecodeError as e:
        return None, f"JSON 파싱 실패: {e}"


def validate_schema(data: dict, schema_path: Path) -> dict:
    if not schema_path.exists():
        return {"result": "skipped", "reason": f"스키마 파일 없음: {schema_path}"}
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        return {"result": "skipped", "reason": "jsonschema 미설치"}

    validator = Draft7Validator(json.loads(schema_path.read_text(encoding="utf-8")))
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if not errors:
        return {"result": "pass", "violations": []}
    return {
        "result": "fail",
        "violations": [
            {"path": ".".join(str(p) for p in e.path) or "(root)", "message": e.message}
            for e in errors
        ],
    }


def compute_diff(old: dict | None, new: dict) -> dict:
    """두 dict 간 최상위 레벨 변경 사항 요약."""
    if old is None:
        return {"type": "new_file", "added_keys": list(new.keys())}

    added, removed, changed = [], [], []

    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        if key not in old:
            added.append(key)
        elif key not in new:
            removed.append(key)
        elif old[key] != new[key]:
            changed.append({
                "key": key,
                "before": _summarize(old[key]),
                "after": _summarize(new[key]),
            })

    return {"type": "update", "added": added, "removed": removed, "changed": changed}


def _summarize(value) -> str:
    """값을 짧은 문자열로 요약."""
    if isinstance(value, str):
        return value[:80] + ("..." if len(value) > 80 else "")
    if isinstance(value, list):
        return f"[list, {len(value)}개 항목]"
    if isinstance(value, dict):
        return f"{{dict, 키 {len(value)}개}}"
    return str(value)


def main():
    parser = argparse.ArgumentParser(description="profile.json 갱신 + 검증")
    parser.add_argument("new_profile", help="새 profile 내용 JSON 파일 경로")
    parser.add_argument("--target", default="./profile.json",
                        help="쓸 대상 profile.json 경로 (기본값: ./profile.json)")
    args = parser.parse_args()

    new_path = Path(args.new_profile)
    target_path = Path(args.target)

    new_data, err = load_json(new_path)
    if err:
        print(json.dumps({"error": err}, ensure_ascii=False))
        sys.exit(2)

    # 스키마 검증 (쓰기 전에)
    validation = validate_schema(new_data, SCHEMA_PATH)
    if validation["result"] == "fail":
        print(json.dumps({
            "written": False,
            "reason": "스키마 검증 실패 — 파일 쓰지 않음",
            "validation": validation,
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    # 기존 파일 읽기 (diff용)
    old_data = None
    if target_path.exists():
        old_data, _ = load_json(target_path)
        bak_path = target_path.with_suffix(".json.bak")
        shutil.copy2(target_path, bak_path)

    # updated_at 자동 갱신
    new_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    # 쓰기
    target_path.write_text(
        json.dumps(new_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    diff = compute_diff(old_data, new_data)

    print(json.dumps({
        "written": True,
        "target": str(target_path),
        "backup": str(target_path.with_suffix(".json.bak")) if old_data is not None else None,
        "validation": validation,
        "diff": diff,
    }, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
