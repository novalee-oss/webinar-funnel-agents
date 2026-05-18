#!/usr/bin/env python3
"""
pricing-helper: simulate.py
매출 목표 / CAC / 전환율 기반 가격 시나리오 시뮬레이션
"""

import argparse
import json
import math
import sys


def simulate(revenue_target: int, cac: int, conversion_rates: list[float],
             target_students: int = 20) -> dict:
    rates = sorted(set(conversion_rates))[:3]
    while len(rates) < 3:
        rates.append(rates[-1] * 2 if rates else 0.01)

    # anchor: revenue_target / target_students, rounded to nearest 10만원
    anchor_price = math.ceil(revenue_target / target_students / 100000) * 100000

    # low: anchor - 10%, mid: anchor, high: anchor + 15%
    prices = {
        "low":  round(anchor_price * 0.9 / 100000) * 100000,
        "mid":  anchor_price,
        "high": round(anchor_price * 1.15 / 100000) * 100000,
    }

    candidates = []
    labels = ["low", "mid", "high"]
    for label, rate in zip(labels, rates):
        price = prices[label]
        leads_needed = math.ceil(revenue_target / (rate * price)) if price > 0 else 0
        students_needed = math.ceil(revenue_target / price) if price > 0 else 0
        projected_revenue = price * students_needed
        candidates.append({
            "level": label,
            "amount": price,
            "cac_assumption": cac,
            "conversion_rate": rate,
            "required_leads": leads_needed,
            "required_students": students_needed,
            "projected_revenue": projected_revenue,
            "margin_per_student": price - cac,
        })

    return {
        "revenue_target": revenue_target,
        "cac_assumption": cac,
        "target_students_assumption": target_students,
        "candidates": candidates,
    }


def main():
    parser = argparse.ArgumentParser(description="Pricing simulator for product planning")
    parser.add_argument("--revenue-target", type=int, required=True)
    parser.add_argument("--cac", type=int, default=200000)
    parser.add_argument("--conversion-rates", type=str, default="0.01,0.02,0.03",
                        help="Comma-separated list of 3 conversion rates")
    parser.add_argument("--target-students", type=int, default=20,
                        help="Expected number of students (used to anchor price range)")
    args = parser.parse_args()

    try:
        rates = [float(r.strip()) for r in args.conversion_rates.split(",")]
    except ValueError:
        print(json.dumps({"error": "conversion-rates must be comma-separated floats"}))
        sys.exit(2)

    result = simulate(args.revenue_target, args.cac, rates, args.target_students)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
