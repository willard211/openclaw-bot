#!/usr/bin/env python3
import json
from pathlib import Path

SKILL_ORDER = [
    "skill_product_expert",
    "skill_company_profile",
    "skill_sales_copilot",
]

WEIGHTED_RULES = {
    "skill_product_expert": {
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
        "anchor bolt": 1,
        "sample": 1,
    },
    "skill_company_profile": {
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
    },
    "skill_sales_copilot": {
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
        "final contract": 3,
        "commitment": 2,
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


def select_skills(text: str):
    low = text.lower()
    scores = {}
    for skill, keyword_map in WEIGHTED_RULES.items():
        score = 0
        for kw, weight in keyword_map.items():
            if kw.lower() in low:
                score += weight
        scores[skill] = score

    selected = [skill for skill in SKILL_ORDER if scores[skill] > 0]
    if not selected:
        selected = ["skill_sales_copilot"]
    return selected, scores


def should_handoff(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in RISK_KEYWORDS)


def build_reply_outline(text: str):
    skills, scores = select_skills(text)
    sections = []
    for skill in skills:
        if skill == "skill_product_expert":
            sections.append("Product facts: specs, MOQ, lead time, certifications.")
        elif skill == "skill_company_profile":
            sections.append("Company proof: factory capability, QC, payment/after-sales policy.")
        elif skill == "skill_sales_copilot":
            sections.append("Sales push: objection handling and clear CTA.")
    return {
        "skills": skills,
        "scores": scores,
        "handoff": should_handoff(text),
        "outline": " ".join(sections),
    }


def run(cases_path: Path) -> int:
    total = 0
    skill_ok = 0
    handoff_ok = 0

    for line in cases_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        total += 1
        case = json.loads(line)
        msg = case["customer_message"]
        result = build_reply_outline(msg)

        got = result["skills"]
        expected = case["expected_skills"]
        got_handoff = result["handoff"]
        expected_handoff = case["expected_handoff"]

        same_skills = got == expected
        same_handoff = got_handoff == expected_handoff
        skill_ok += int(same_skills)
        handoff_ok += int(same_handoff)

        print(
            f"[{case['id']}] skills={'OK' if same_skills else 'FAIL'} "
            f"({got} vs {expected}), handoff={'OK' if same_handoff else 'FAIL'} "
            f"({got_handoff} vs {expected_handoff})"
        )

    print("\nSummary")
    print(f"- total: {total}")
    print(f"- multi-intent accuracy: {skill_ok}/{total} = {skill_ok/total:.1%}")
    print(f"- handoff accuracy: {handoff_ok}/{total} = {handoff_ok/total:.1%}")
    return 0


if __name__ == "__main__":
    path = Path("data/multi_intent_cases.jsonl")
    raise SystemExit(run(path))
