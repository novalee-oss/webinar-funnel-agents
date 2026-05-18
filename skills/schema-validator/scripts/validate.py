#!/usr/bin/env python3
"""
schema-validator: JSON 파일이 지정 스키마를 통과하는지 검증.
각 Stage 종료 직전 + Stage 4 컴파일 시 자동 호출.

사용법:
    python validate.py <data_file> <schema_file> [--quiet]

종료 코드:
    0 = pass
    1 = fail (위반 항목 있음)
    2 = 입력 오류 (파일 없음, JSON 파싱 실패 등)
"""
import sys
import json
import argparse
from pathlib import Path

try:
    from jsonschema import Draft7Validator
except ImportError:
    print(json.dumps({
        "result": "error",
        "violations": [{"path": "", "message": "jsonschema 패키지 필요: pip install jsonschema"}]
    }, ensure_ascii=False))
    sys.exit(2)


def load_json(path: str, label: str) -> tuple:
    """JSON 파일 읽기. (data, error_dict) 반환."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, {"path": "", "message": f"{label} 파일 없음: {path}"}
    except json.JSONDecodeError as e:
        return None, {"path": "", "message": f"{label} JSON 파싱 실패: {e}"}


def validate(data_path: str, schema_path: str) -> dict:
    data, err = load_json(data_path, "데이터")
    if err:
        return {"result": "fail", "violations": [err]}

    schema, err = load_json(schema_path, "스키마")
    if err:
        return {"result": "fail", "violations": [err]}

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    if not errors:
        return {"result": "pass", "violations": [], "data_file": data_path}

    violations = []
    for error in errors:
        path = ".".join(str(p) for p in error.path) or "(root)"
        violations.append({
            "path": path,
            "message": error.message,
            "schema_path": ".".join(str(p) for p in error.schema_path),
        })

    return {
        "result": "fail",
        "violations": violations,
        "violation_count": len(violations),
        "data_file": data_path,
    }


def main():
    parser = argparse.ArgumentParser(
        description="JSON 스키마 검증",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python validate.py working/01a_persona.json .claude/docs/schemas/paid_plan.schema.json
  python validate.py profile.json .claude/docs/schemas/profile.schema.json --quiet
        """,
    )
    parser.add_argument("data", help="검증할 JSON 파일 경로")
    parser.add_argument("schema", help="스키마 JSON 파일 경로")
    parser.add_argument("--quiet", action="store_true", help="pass 시 출력 생략")
    args = parser.parse_args()

    result = validate(args.data, args.schema)

    if not (args.quiet and result["result"] == "pass"):
        print(json.dumps(result, ensure_ascii=False, indent=2))

    sys.exit(0 if result["result"] == "pass" else 1)


if __name__ == "__main__":
    main()
