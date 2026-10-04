from app.pipeline.industry_gate import normalize_lead


def build_qualification_prompt(lead, features, scored):
    normalized = normalize_lead(lead)

    return (
        "You are extracting structured evidence from a business lead description for a "
        "sales/marketing qualification system. You are NOT deciding whether to qualify or "
        "disqualify — only classify the evidence present. The Python rule engine will determine "
        "the final decision from your output.\n\n"
        "Return valid JSON with exactly these keys: capacity, growth_intent, "
        "customer_acquisition_need, ambiguity, reasoning, positive_signals, negative_signals.\n\n"
        "capacity must be one of 'low', 'moderate', 'high', 'unknown' — is the business at/near "
        "capacity? A waitlist or 'fully booked' language indicates low current capacity. "
        "Do not interpret this alone as evidence of growth intent or customer-acquisition need., and must never be read "
        "as a positive demand signal.\n"
        "growth_intent must be one of 'seeking_growth', 'saturated', 'stable', 'unknown'. A "
        "waitlist or being fully booked means 'saturated', not 'seeking_growth'. Do not assume "
        "growth intent unless the description gives explicit or clearly implied evidence of it.\n"
        "customer_acquisition_need must be one of 'high', 'moderate', 'low', 'unknown', based only "
        "on marketing/digital presence signals — company size alone is not sufficient evidence.\n"
        "ambiguity must be true or false. Do not treat hedging language ('not sure', 'may not be') "
        "as positive evidence — hedging means unresolved, not favorable. If evidence is unclear, "
        "use 'unknown' rather than guessing.\n\n"
        f"Normalized industry: {normalized.normalized_industry}\n"
        f"Company size: {normalized.company_size}\n"
        f"Website present: {normalized.website_present}\n"
        f"Email present: {normalized.email_present}\n"
        f"Rule score: {scored['score']}\n"
        f"Score breakdown: {scored['score_breakdown']}\n"
        f"Positive signals: {features.positive_signals}\n"
        f"Negative signals: {features.negative_signals}\n"
        f"Ambiguity signals: {features.ambiguity_signals}\n"
        f"Company description: {(normalized.description or '')}\n\n"
        "reasoning should be 1-2 sentences explaining the evidence behind your classifications, "
        "grounded only in the description and signals given above."
    )
