#!/usr/bin/env python3
"""
profile-io read: profile.json 읽기 + 스키마 검증.

사용법:
    python read.py [profile_path] [--no-validate]

종료 코드:
    0 = 성공 (pass 또는 no-validate)
    1 = 스키마 위반
    2 = 파일 오류
"""
import sys
import json
import argparse
from pathlib import Path

# .claude/docs/schemas/ 위치: 이 스크립트 기준 ../../../docs/schemas/
SKILL_DIR = Path(__file__).parent.parent        # profile-io/
SKILLS_DIR = SKILL_DIR.parent                   # skills/
CLAUDE_DIR = SKILLS_DIR.parent                  # .claude/
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
    """jsonschema로 검증. 패키지 없으면 skipped 반환."""
    if not schema_path.exists():
        return {"result": "skipped", "reason": f"스키마 파일 없음: {schema_path}"}
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        return {"result": "skipped", "reason": "jsonschema 미설치. pip install jsonschema"}

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


def main():
    parser = argparse.ArgumentParser(description="profile.json 읽기 + 스키마 검증")
    parser.add_argument("profile", nargs="?", default="./profile.json",
                        help="profile.json 경로 (기본값: ./profile.json)")
    parser.add_argument("--no-validate", action="store_true", help="스키마 검증 생략")
    args = parser.parse_args()

    profile_path = Path(args.profile)
    data, err = load_json(profile_path)
    if err:
        print(json.dumps({"error": err}, ensure_ascii=False))
        sys.exit(2)

    output = {"profile": data}

    if not args.no_validate:
        validation = validate_schema(data, SCHEMA_PATH)
        output["validation"] = validation
        if validation["result"] == "fail":
            print(json.dumps(output, ensure_ascii=False, indent=2))
            sys.exit(1)

    print(json.dumps(output, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
