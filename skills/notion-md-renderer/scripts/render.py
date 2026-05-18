#!/usr/bin/env python3
"""
notion-md-renderer: render.py
paid_plan.json / free_plan.json → Notion 붙여넣기 호환 마크다운
"""

import argparse
import json
import sys
from pathlib import Path


def render_paid_plan(data: dict) -> str:
    lines = []

    def h(level: int, text: str):
        lines.append(f"{'#' * level} {text}\n")

    def p(text: str):
        if text:
            lines.append(f"{text}\n")

    def hr():
        lines.append("---\n")

    meta = data.get("meta", {})
    h(1, data.get("course_name", "(과정명 없음)"))
    p(f"> 컴파일: {meta.get('compiled_at', '')}  |  클라이언트: {meta.get('client_id', '')}")
    hr()

    # 1. concept
    concept = data.get("concept", {})
    if concept:
        h(2, "전체 컨셉")
        p(f"**약속**: {concept.get('promise', '')}")
        p(f"**약속 강도**: {concept.get('promise_strength', '')}")
        p(f"**결과 이미지**: {concept.get('result_image', '')}")
        p(f"**태그라인**: {concept.get('tagline', '')}")
        p(f"**욕망 카테고리**: {concept.get('desire_category', '')}")
        hr()

    # 2. usp
    usp = data.get("usp", {})
    if usp:
        h(2, "핵심 USP")
        p(usp.get("core_usp", ""))
        h(3, "시장 내 포지셔닝")
        p(usp.get("positioning", ""))
        hr()

    # 3. target_problem
    tp = data.get("target_problem", {})
    if tp:
        h(2, "타깃 문제 정의")
        persona = tp.get("persona", {})
        if persona:
            h(3, "페르소나")
            p(f"**요약**: {persona.get('summary', '')}")
            p(f"**인구통계**: {persona.get('demographics', '')}")
            p(f"**상황**: {persona.get('situation', '')}")
            p(f"**심리**: {persona.get('psychographics', '')}")
        painpoints = tp.get("painpoints", [])
        if painpoints:
            h(3, "페인포인트")
            for i, pp in enumerate(painpoints, 1):
                lines.append(f"{i}. [{pp.get('who', '')}] {pp.get('situation', '')} → {pp.get('emotion', '')}\n")
                lines.append(f"   └ 진짜 원인: {pp.get('root_cause', '')}\n")
        hr()

    # 4. solution
    sol = data.get("solution", {})
    if sol:
        h(2, "해결책")
        p(sol.get("overview", ""))
        roadmap = sol.get("roadmap", "")
        if roadmap:
            h(3, "수강 후 로드맵")
            p(roadmap)
        curriculum = sol.get("curriculum", [])
        if curriculum:
            h(3, "커리큘럼")
            for mod in curriculum:
                lines.append(f"- **{mod.get('module', '')}. {mod.get('title', '')}** ({mod.get('duration', '')})\n")
                lines.append(f"  {mod.get('description', '')}\n")
        bonus = sol.get("bonus_materials", [])
        if bonus:
            h(3, "추가 혜택")
            for b in bonus:
                lines.append(f"- {b.get('title', '')}: {b.get('description', '')}\n")
        hr()

    # 5. pricing
    pricing = data.get("pricing", {})
    if pricing:
        h(2, "가격 안내")
        p(f"**공개 가격**: {pricing.get('public_price', 0):,}원")
        p(f"**총 인지 가치**: {pricing.get('total_perceived_value', '')}")
        p(pricing.get("market_comparison", ""))
        hr()

    # 6. social_proof
    sp = data.get("social_proof", [])
    if sp:
        h(2, "사회적 증거")
        for case in sp:
            lines.append(f"**{case.get('id', '')}** [{case.get('consent', {}).get('scope', '')}]\n")
            lines.append(f"{case.get('summary', '')} → {case.get('result', '')}\n\n")
        hr()

    # 7. faq
    faq = data.get("faq", [])
    if faq:
        h(2, "FAQ")
        for item in faq:
            lines.append(f"**Q. {item.get('question', '')}**\n")
            lines.append(f"A. {item.get('answer', '')}\n\n")
        hr()

    return "".join(lines)


def render_free_plan(data: dict) -> str:
    lines = []

    def h(level: int, text: str):
        lines.append(f"{'#' * level} {text}\n")

    def p(text: str):
        if text:
            lines.append(f"{text}\n")

    def hr():
        lines.append("---\n")

    meta = data.get("meta", {})
    h(1, data.get("webinar_name", "(웨비나명 없음)"))
    p(f"> 컴파일: {meta.get('compiled_at', '')}  |  유료 상품 참조: {meta.get('paid_plan_ref', '')}")
    hr()

    concept = data.get("concept", {})
    if concept:
        h(2, "웨비나 컨셉")
        p(f"**약속**: {concept.get('promise', '')}")
        p(f"**약속 강도**: {concept.get('promise_strength', '')}")
        hr()

    tp = data.get("target_problem", {})
    if tp:
        h(2, "타깃 문제")
        p(f"*(출처: {tp.get('reused_from', '')})*")
        persona = tp.get("persona", {})
        if persona:
            p(f"**페르소나**: {persona.get('summary', '')}")
        hr()

    curriculum = data.get("curriculum", {})
    if curriculum:
        h(2, "커리큘럼")
        p(f"총 {curriculum.get('total_duration_min', 0)}분")
        for mod in curriculum.get("modules", []):
            tag = mod.get("exposure_type", "")
            lines.append(f"- **{mod.get('title', '')}** ({mod.get('duration_min', 0)}분) [{tag}]\n")
            lines.append(f"  {mod.get('description', '')}\n")
        hr()

    hook = data.get("hook", {})
    if hook:
        h(2, "Hook")
        p(f'"{hook.get("copy", "")}"')
        p(f"전환 로직: {hook.get('transition_logic', '')}")
        hr()

    sp = data.get("social_proof", [])
    if sp:
        h(2, "사회적 증거")
        for case in sp:
            lines.append(f"**{case.get('id', '')}**: {case.get('summary', '')} → {case.get('result', '')}\n\n")
        hr()

    faq = data.get("faq", [])
    if faq:
        h(2, "FAQ")
        for item in faq:
            lines.append(f"**Q. {item.get('question', '')}**\n")
            lines.append(f"A. {item.get('answer', '')}\n\n")

    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Render plan JSON to Notion-compatible markdown")
    parser.add_argument("input", help="Path to paid_plan.json or free_plan.json")
    parser.add_argument("--output", help="Output .notion.md path")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(json.dumps({"error": f"Input file not found: {args.input}"}))
        sys.exit(2)

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    # detect plan type
    if "webinar_name" in data or data.get("meta", {}).get("plan_type") == "free":
        md = render_free_plan(data)
    else:
        md = render_paid_plan(data)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(json.dumps({"result": "written", "path": str(out_path)}, ensure_ascii=False))
    else:
        sys.stdout.write(md)

    sys.exit(0)


if __name__ == "__main__":
    main()
