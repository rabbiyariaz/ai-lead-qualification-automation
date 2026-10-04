from __future__ import annotations

from pydantic import BaseModel, Field

TARGET_INDUSTRIES = {
    "plumbing",
    "hvac",
    "electrical",
    "cleaning",
    "landscaping",
    "pest control",
    "roofing",
    "security & alarm",
    "daycare",
}

INDUSTRY_ALIASES = {
    "plumbing": {
        "plumbing", "plumber", "plumbing contractor", "residential plumbing",
        "emergency plumbing services", "pipe fitting", "drain cleaning",
        "plumbing & drain cleaning", "plumbing and drain cleaning",
    },
    "hvac": {
        "hvac", "heating and cooling", "heating & cooling", "air conditioning",
        "heating ventilation and air conditioning", "ac repair", "a/c repair",
        "air conditioning repair", "furnace repair",
    },
    "electrical": {
        "electrical", "electrician", "electrical contractor", "residential electrician",
        "commercial electrician",
    },
    "cleaning": {
        "cleaning", "cleaning services", "janitorial", "house cleaning",
        "commercial cleaning", "maid service",
    },
    "landscaping": {
        "landscaping", "lawn care", "landscape services", "yard care",
        "garden services", "lawn mowing", "lawn maintenance",
    },
    "pest control": {
        "pest control", "exterminator", "termite control", "rodent control",
        "bug extermination", "pest management", "insect control",
    },
    "roofing": {
        "roofing", "roofer", "roof repair", "commercial roofing", "residential roofing",
    },
    "security & alarm": {
        "security & alarm", "security alarm", "security systems", "alarm installation",
        "home security",
    },
    "daycare": {
        "daycare", "childcare", "child care", "child care center", "preschool",
        "nursery school", "early learning center",
    },
}


class ICPConfig(BaseModel):
    target_industries: set[str] = Field(default_factory=lambda: set(TARGET_INDUSTRIES))
    positive_markers: list[tuple[str, str]] = Field(
    default_factory=lambda: [
        (r"word\s+of\s+mouth", "word of mouth"),
        (r"referrals\s+only", "referrals only"),
        (r"no\s+online\s+presence", "no online presence"),
        (r"growing\s+fast", "growing fast"),
        (r"growing", "growing"),
        (r"need\s+more\s+leads", "need more leads"),
        (r"need\s+help", "need help"),
        (r"we\s+are\s+growing", "we are growing"),
        (r"limited\s+online\s+presence", "limited online presence"),
    ]
)
    negative_markers: list[tuple[str, str]] = Field(
    default_factory=lambda: [
        (r"in-house marketing team", "in-house marketing team"),
        (r"established digital campaigns", "established digital campaigns"),
        (r"already have strong digital presence", "strong digital presence"),
        (r"marketing team", "marketing team"),
        (r"highly established", "highly established"),
        (r"not\s+(?:seeking|looking\s+to\s+grow)", "not seeking growth"),
        (r"fully\s+booked", "fully booked"),
        (r"at\s+(?:max(?:imum)?\s+|full\s+)?capacity", "at capacity"),
        (r"no\s+longer\s+accepting", "no longer accepting"),
        (r"not\s+(?:currently\s+)?accepting\s+new", "not accepting new"),
        (r"booked\s+(?:out|solid)", "booked out"),
        (r"not\s+actively\s+seeking", "not actively seeking"),
        (r"waitlist", "waitlist"),
        (r"nothing\s+concrete", "nothing concrete"),
    ]
)

    ambiguity_markers: list[tuple[str, str]] = Field(
    default_factory=lambda: [
        (r"unclear\s+(?:if|whether)", "unclear"),
        (r"not\s+sure\s+(?:if|whether|about)", "not sure"),   # "about" added
        (r"may\s+not\s+be", "may not be"),
        (r"might\s+not\s+be", "might not be"),
        (r"uncertain", "uncertain"),
        (r"unsure", "unsure"),
    ]
)
    
    company_size_ideal_min: int = 1
    company_size_ideal_max: int = 30
    company_size_good_min: int = 31
    company_size_good_max: int = 100
    company_size_ideal_score: int = 30
    company_size_good_score: int = 15
    company_size_out_of_range_score: int = -20
    website_missing_score: int = 25
    email_missing_score: int = 10
    complete_contact_score: int = -5
    positive_signal_score: int = 15
    negative_signal_score: int = -20
    qualification_threshold: int = 50
    review_threshold: int = 10
    disqualification_threshold: int = 10


DEFAULT_ICP_CONFIG = ICPConfig()





