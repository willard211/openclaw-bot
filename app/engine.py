import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent

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
    "最终价格",
    "合同",
    "账期",
    "独家",
]


def _load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


PRODUCT_ROWS = _load_csv(BASE_DIR / "kb-templates" / "product_kb_template.csv")
COMPANY_ROWS = _load_csv(BASE_DIR / "kb-templates" / "company_kb_template.csv")
SALES_ROWS = _load_csv(BASE_DIR / "kb-templates" / "sales_script_kb_template.csv")


def detect_language(text: str) -> str:
    return "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en"


def select_skills(text: str) -> Tuple[List[str], Dict[str, int]]:
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


def _best_product_row(text: str) -> Dict[str, str]:
    low = text.lower()
    for row in PRODUCT_ROWS:
        name = (row.get("product_name_en") or "").lower()
        if name and any(token in name for token in low.split()):
            return row
    return PRODUCT_ROWS[0] if PRODUCT_ROWS else {}


def _company_row() -> Dict[str, str]:
    return COMPANY_ROWS[0] if COMPANY_ROWS else {}


def _sales_row(text: str) -> Dict[str, str]:
    low = text.lower()
    for row in SALES_ROWS:
        intent = (row.get("intent") or "").lower()
        objection = (row.get("objection_type") or "").lower()
        if intent and intent in low:
            return row
        if objection and objection in low:
            return row
    for row in SALES_ROWS:
        tpl = (row.get("script_template") or "").lower()
        if "too expensive" in low and "budget" in tpl:
            return row
        if "follow" in low and "checking in" in tpl:
            return row
    return SALES_ROWS[0] if SALES_ROWS else {}


def _product_reply(text: str, lang: str) -> str:
    row = _best_product_row(text)
    if not row:
        return ""
    if lang == "zh":
        return (
            f"产品信息：{row.get('product_name_cn','')}，规格 {row.get('specs','')}，"
            f"MOQ {row.get('moq','')}，交期 {row.get('lead_time','')}，认证 {row.get('certifications','')}。"
        )
    return (
        f"Product info: {row.get('product_name_en','')}, specs {row.get('specs','')}, "
        f"MOQ {row.get('moq','')}, lead time {row.get('lead_time','')}, certifications {row.get('certifications','')}."
    )


def _company_reply(lang: str) -> str:
    row = _company_row()
    if not row:
        return ""
    if lang == "zh":
        return (
            f"公司信息：{row.get('company_intro','')}；产能 {row.get('factory_capacity','')}；"
            f"质控 {row.get('quality_control','')}；付款条款 {row.get('payment_terms','')}。"
        )
    return (
        f"Company profile: {row.get('company_intro','')}; capacity {row.get('factory_capacity','')}; "
        f"QC {row.get('quality_control','')}; payment terms {row.get('payment_terms','')}."
    )


def _sales_reply(text: str, lang: str) -> str:
    row = _sales_row(text)
    cta = row.get("cta", "Please share quantity and destination port.")
    tpl = row.get("script_template", "")
    if lang == "zh":
        return f"销售建议：{tpl} 下一步：{cta}"
    return f"Sales suggestion: {tpl} Next step: {cta}"


def build_response(message: str) -> Dict[str, object]:
    lang = detect_language(message)
    skills, scores = select_skills(message)
    handoff = should_handoff(message)

    parts = []
    if "skill_product_expert" in skills:
        parts.append(_product_reply(message, lang))
    if "skill_company_profile" in skills:
        parts.append(_company_reply(lang))
    if "skill_sales_copilot" in skills:
        parts.append(_sales_reply(message, lang))

    if handoff:
        if lang == "zh":
            parts.append("该问题涉及高风险条款，已标记为需人工商务确认。")
        else:
            parts.append("This request includes high-risk terms and is flagged for human approval.")

    reply = "\n".join([p for p in parts if p])
    return {
        "language": lang,
        "skills": skills,
        "scores": scores,
        "handoff": handoff,
        "reply": reply,
    }


def to_json(data: Dict[str, object]) -> bytes:
    return json.dumps(data, ensure_ascii=False).encode("utf-8")
