from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Lead(BaseModel):
    model_config = ConfigDict(extra="ignore")

    lead_id: str | None = None
    company_name: str | None = None
    industry: str | None = None
    company_size: str | int | None = None
    website: str | None = None
    email: str | None = Field(default=None, alias="contact_email")
    location: str | None = None
    description: str | None = None

    @field_validator("company_name", "industry", "website", "email", "location", "description", mode="before")
    @classmethod
    def clean_optional_text(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        return str(value).strip() or None


class NormalizedLead(BaseModel):
    lead_id: str | None = None
    company_name: str | None = None
    industry: str | None = None
    normalized_industry: str = ""
    company_size: int | None = None
    website: str | None = None
    email: str | None = None
    location: str | None = None
    description: str | None = None
    website_present: bool = False
    email_present: bool = False


class LeadFeatures(BaseModel):
    company_size: int | None = None
    company_size_fit: bool = False
    website_present: bool = False
    email_present: bool = False
    website_missing: bool = False
    email_missing: bool = False
    growth_signal: bool = False
    marketing_team_signal: bool = False
    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    ambiguity_signals: list[str] = Field(default_factory=list)
    description_missing: bool = False
    insufficient_data: bool = False
