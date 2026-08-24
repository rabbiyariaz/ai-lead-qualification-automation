from app.llm.prompts import build_qualification_prompt
from app.llm.schemas import safe_llm_result
from app.ingestion.csv_loader import load_leads_from_csv
from app.models.icp import DEFAULT_ICP_CONFIG
from app.output.csv_writer import write_qualified_leads
from app.pipeline.features import extract_lead_features
from app.pipeline.industry_gate import industry_gate, normalize_lead
from app.pipeline.scoring import score_lead, compute_rule_confidence
from app.pipeline.dedup import dedupe_leads
from concurrent.futures import ThreadPoolExecutor


def compute_llm_decision(evidence: dict) -> str:
    if evidence["capacity"] == "low" or evidence["growth_intent"] == "saturated":
        return "disqualified"
    if evidence["ambiguity"]:
        return "review"
    if evidence["growth_intent"] == "seeking_growth" and evidence["customer_acquisition_need"] in ("high", "moderate"):
        return "qualified"
    return "review"


def compute_llm_confidence(evidence: dict, features, scored: dict, llm_decision: str) -> float:
    confidence = 0.50

    # 1. Evidence completeness
    known_fields = sum([
        evidence["capacity"] != "unknown",
        evidence["growth_intent"] != "unknown",
        evidence["customer_acquisition_need"] != "unknown",
    ])
    confidence += known_fields * 0.08

    # 2. Strength of rule-based evidence
    score = scored["score"]
    if abs(score) >= 40:
        confidence += 0.15
    elif abs(score) >= 25:
        confidence += 0.10
    elif abs(score) >= 10:
        confidence += 0.05

    # 3. Signal agreement (within LLM evidence)
    if evidence["growth_intent"] == "seeking_growth" and evidence["customer_acquisition_need"] in ("high", "moderate"):
        confidence += 0.10
    if evidence["capacity"] == "low" and evidence["growth_intent"] == "saturated":
        confidence += 0.10

    # 4. Ambiguity penalty
    if evidence["ambiguity"]:
        confidence -= 0.20

    # 5. Missing source-data penalty
    missing = sum([features.website_missing, features.email_missing, features.description_missing])
    confidence -= missing * 0.05

    # 6. Agreement between rule-based decision and LLM-derived decision
    if scored["decision"] != "review" and llm_decision == scored["decision"]:
        confidence += 0.05
    elif scored["decision"] not in ("review", llm_decision):
        confidence -= 0.10

    return round(max(0.10, min(0.95, confidence)), 2)


def llm_review(lead, llm_client=None, lead_features=None, scored=None, icp_config=DEFAULT_ICP_CONFIG):
    normalized = normalize_lead(lead)
    features = lead_features or extract_lead_features(normalized, icp_config=icp_config)
    scored_result = scored or score_lead(features, icp_config=icp_config)

    if llm_client is None:
        return {
            "stage": "llm_review",
            "decision": "review",
            "reason": "No LLM client provided; manual review required.",
            "llm_reasoning": "No LLM client provided; manual review required.",
            "confidence": 0.0,
            "positive_signals": scored_result["positive_signals"],
            "negative_signals": scored_result["negative_signals"],
            "score_breakdown": scored_result["score_breakdown"],
            "score": scored_result["score"],
        }

    prompt = build_qualification_prompt(normalized, features=features, scored=scored_result)
    raw_response = llm_client(prompt)
    evidence = safe_llm_result(raw_response)

    decision = compute_llm_decision(evidence)
    confidence = compute_llm_confidence(evidence, features, scored_result, decision)

    return {
        "stage": "llm_review",
        "decision": decision,
        "reason": evidence["reasoning"],
        "llm_reasoning": evidence["reasoning"],
        "confidence": confidence,
        "capacity": evidence["capacity"],
        "growth_intent": evidence["growth_intent"],
        "customer_acquisition_need": evidence["customer_acquisition_need"],
        "ambiguity": evidence["ambiguity"],
        "positive_signals": scored_result["positive_signals"],
        "negative_signals": scored_result["negative_signals"],
        "score_breakdown": scored_result["score_breakdown"],
        "score": scored_result["score"],
    }

def qualify_lead(lead, llm_client=None, icp_config=DEFAULT_ICP_CONFIG):
    normalized = normalize_lead(lead)
    industry_result = industry_gate(normalized, icp_config=icp_config)
    if industry_result is not None:
        return industry_result

    features = extract_lead_features(normalized, icp_config=icp_config)
    scored = score_lead(features, icp_config=icp_config)

    has_description = bool(normalized.description)

    if scored["decision"] == "qualified" and not has_description:
        return {
            "stage": "scoring",
            "decision": "qualified",
            "score": scored["score"],
            "reason": "Passed rule-based scoring",
            "positive_signals": scored["positive_signals"],
            "negative_signals": scored["negative_signals"],
            "score_breakdown": scored["score_breakdown"],
            "llm_reasoning": "",
            "confidence": compute_rule_confidence(features, base_confidence=0.9, icp_config=icp_config),
        }

    if scored["decision"] == "disqualified":
        return {
            "stage": "scoring",
            "decision": "disqualified",
            "score": scored["score"],
            "reason": "Failed rule-based scoring",
            "positive_signals": scored["positive_signals"],
            "negative_signals": scored["negative_signals"],
            "score_breakdown": scored["score_breakdown"],
            "llm_reasoning": "",
            "confidence": compute_rule_confidence(features, base_confidence=0.2, icp_config=icp_config),
        }

    return llm_review(normalized, llm_client=llm_client, lead_features=features, scored=scored, icp_config=icp_config)



def run_qualification_pipeline(input_csv_path, output_csv_path, llm_client=None, icp_config=DEFAULT_ICP_CONFIG):
    leads = load_leads_from_csv(input_csv_path)
    leads = dedupe_leads(leads)

    def process(lead):
        result = qualify_lead(lead.model_dump(), llm_client=llm_client, icp_config=icp_config)
        return {
    **lead.model_dump(),
    "decision": result.get("decision", "review"),
    "score": result.get("score", 0),
    "stage": result.get("stage", "scoring"),
    "reason": result.get("reason", ""),
    "llm_reasoning": result.get("llm_reasoning", ""),
    "confidence": result.get("confidence", 0.0),
    "capacity": result.get("capacity", "unknown"),
    "growth_intent": result.get("growth_intent", "unknown"),
    "customer_acquisition_need": result.get("customer_acquisition_need", "unknown"),
    "ambiguity": result.get("ambiguity", False),
}

    with ThreadPoolExecutor(max_workers=8) as executor:
        qualified_rows = list(executor.map(process, leads))

    write_qualified_leads(output_csv_path, qualified_rows)
    return qualified_rows


