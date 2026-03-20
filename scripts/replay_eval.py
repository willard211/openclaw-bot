#!/usr/bin/env python3
import json
from pathlib import Path

RULES = {
    "skill_product_expert": {
        "weighted_keywords": {
            "规格": 3,
            "参数": 3,
            "moq": 3,
            "认证": 2,
            "交期": 2,
            "型号": 3,
            "specification": 3,
            "spec": 2,
            "lead time": 2,
            "certification": 2,
            "certificate": 2,
            "ce": 1,
            "anchor bolt": 1,
        }
    },
    "skill_company_profile": {
        "weighted_keywords": {
            "公司介绍": 4,
            "工厂": 4,
            "资质": 3,
            "付款": 4,
            "售后": 3,
            "贸易条款": 3,
            "factory": 4,
            "payment terms": 4,
            "after-sales": 3,
            "company profile": 4,
            "introduce": 3,
            "contract": 4,
            "credit terms": 4,
            "exclusivity": 4,
        }
    },
    "skill_sales_copilot": {
        "weighted_keywords": {
            "太贵": 4,
            "便宜点": 4,
            "考虑下": 2,
            "已读不回": 3,
            "何时下单": 3,
            "too expensive": 4,
            "better price": 4,
            "follow up": 3,
            "following up": 3,
            "last quote": 3,
            "order time": 3,
            "final price": 4,
            "final lead time": 4,
            "commitment": 2,
        }
    },
}

RISK_KEYWORDS = [
    "final price",
    "final lead time",
    "contract",
    "credit terms",
    "exclusivity",
    "open account",
]


def route(text: str) -> str:
    low = text.lower()
    scores = {}
    for skill, rule in RULES.items():
        score = 0
        for kw, weight in rule["weighted_keywords"].items():
            if kw.lower() in low:
                score += weight
        scores[skill] = score

    best_skill = max(scores, key=scores.get)
    best_score = scores[best_skill]

    # If no intent signals are found, default to sales assistant as safe triage.
    if best_score == 0:
        return "skill_sales_copilot"
    return best_skill


def should_handoff(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in RISK_KEYWORDS)


def run(cases_path: Path) -> int:
    total = 0
    route_ok = 0
    handoff_ok = 0

    for line in cases_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        total += 1
        case = json.loads(line)
        msg = case["customer_message"]
        got_skill = route(msg)
        got_handoff = should_handoff(msg)

        skill_match = got_skill == case["expected_skill"]
        handoff_match = got_handoff == case["expected_handoff"]
        route_ok += int(skill_match)
        handoff_ok += int(handoff_match)

        print(
            f"[{case['id']}] skill={'OK' if skill_match else 'FAIL'} "
            f"({got_skill} vs {case['expected_skill']}), "
            f"handoff={'OK' if handoff_match else 'FAIL'} "
            f"({got_handoff} vs {case['expected_handoff']})"
        )

    print("\nSummary")
    print(f"- total: {total}")
    print(f"- routing accuracy: {route_ok}/{total} = {route_ok/total:.1%}")
    print(f"- handoff accuracy: {handoff_ok}/{total} = {handoff_ok/total:.1%}")
    return 0


if __name__ == "__main__":
    path = Path("data/replay_cases.jsonl")
    raise SystemExit(run(path))
