#!/usr/bin/env python3
"""
case-validator check: 사례 후보 리스트에서 consent 메타데이터를 검증.
consent 없는 사례는 자동 탈락. 통과 사례만 다음 단계에서 사용 가능.

사용법:
    python check.py <cases_json_file> [--min-approved N]

    <cases_json_file>: 사례 후보가 담긴 JSON 파일
    --min-approved N: 통과 사례 최소 요구 수 (기본값: 3, Stage 1C 기준)

종료 코드:
    0 = 검증 완료 + 최소 요구 수 충족
    1 = 검증 완료이나 통과 사례 부족 (Nova 에스컬레이션 필요)
    2 = 입력 오류
"""
import sys
import json
import argparse
from pathlib import Path

# consent_meta 유효 scope 값 (profile.schema.json $defs.consent_meta 기준)
VALID_SCOPES = {"full", "anonymized", "excerpt_only"}


def load_json(path: str) -> tuple:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"파일 없음: {path}"
    except json.JSONDecodeError as e:
        return None, f"JSON 파싱 실패: {e}"


def check_consent(case: dict) -> tuple[bool, str]:
    """
    단일 사례의 consent 검증.
    (통과 여부, 탈락 사유) 반환.
    """
    case_id = case.get("id", "(id 없음)")
    consent = case.get("consent")

    # consent 필드 자체가 없음
    if consent is None:
        return False, "consent_missing"

    # consent가 dict가 아님
    if not isinstance(consent, dict):
        return False, "consent_invalid_type"

    # granted 필드 없음
    if "granted" not in consent:
        return False, "consent_granted_missing"

    # granted가 명시적으로 false
    if consent["granted"] is False:
        return False, "consent_not_granted"

    # granted가 true가 아닌 다른 값
    if consent["granted"] is not True:
        return False, "consent_granted_not_boolean"

    # scope 필드 없음
    if "scope" not in consent:
        return False, "consent_scope_missing"

    # scope 유효하지 않은 값
    if consent["scope"] not in VALID_SCOPES:
        return False, f"consent_scope_invalid (값: {consent['scope']}, 허용: {sorted(VALID_SCOPES)})"

    return True, ""


def validate_cases(cases: list, min_approved: int) -> dict:
    approved = []
    rejected = []

    for case in cases:
        case_id = case.get("id", f"(index {cases.index(case)})")
        passed, reason = check_consent(case)

        if passed:
            approved.append({
                "id": case_id,
                "scope": case["consent"]["scope"],
                # 원본 사례 데이터 그대로 포함 (에이전트가 이후 사용)
                "data": case,
            })
        else:
            rejected.append({
                "id": case_id,
                "reason": reason,
                # 에이전트·Nova에게 참고용 원본 포함
                "data": case,
            })

    approved_count = len(approved)
    sufficient = approved_count >= min_approved

    result = {
        "approved_count": approved_count,
        "rejected_count": len(rejected),
        "sufficient": sufficient,
        "min_required": min_approved,
        "approved": approved,
        "rejected": rejected,
    }

    if not sufficient:
        result["escalation_required"] = True
        result["escalation_message"] = (
            f"consent 통과 사례 {approved_count}건 — 최소 {min_approved}건 필요. "
            "Nova 에스컬레이션: 추가 사례 확보 또는 최소 요구 수 조정 결정 필요."
        )

    return result


def main():
    parser = argparse.ArgumentParser(
        description="사례 consent 메타데이터 검증",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
입력 JSON 형식 (배열 또는 {cases: [...]}):
  [
    {
      "id": "case-001",
      "summary": "...",
      "consent": { "granted": true, "scope": "anonymized" }
    },
    {
      "id": "case-002",
      "summary": "...",
      "consent": null
    }
  ]

예시:
  python check.py inputs/cases.json
  python check.py inputs/cases.json --min-approved 2
        """,
    )
    parser.add_argument("cases_file", help="사례 후보 JSON 파일 경로")
    parser.add_argument(
        "--min-approved",
        type=int,
        default=3,
        help="통과 사례 최소 요구 수 (기본값: 3, SPEC Stage 1C 기준)",
    )
    args = parser.parse_args()

    raw, err = load_json(args.cases_file)
    if err:
        print(json.dumps({"error": err}, ensure_ascii=False))
        sys.exit(2)

    # 배열 또는 {cases: [...]} 두 형식 모두 허용
    if isinstance(raw, list):
        cases = raw
    elif isinstance(raw, dict) and "cases" in raw:
        cases = raw["cases"]
    else:
        print(json.dumps({
            "error": "입력 형식 오류: 배열 또는 {\"cases\": [...]} 형식이어야 함"
        }, ensure_ascii=False))
        sys.exit(2)

    result = validate_cases(cases, args.min_approved)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    sys.exit(0 if result["sufficient"] else 1)


if __name__ == "__main__":
    main()
