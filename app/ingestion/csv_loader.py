import csv
import logging

from app.models.lead import Lead

logger = logging.getLogger(__name__)

KNOWN_FIELDS = {"lead_id", "company_name", "industry", "company_size", "website", "contact_email", "location", "description"}
REQUIRED_FIELDS = {"company_name", "industry", "contact_email", "company_size"}
ALIAS_FIELDS = {"employee_count", "company_website", "email", "city", "company_description"}


def check_unknown_columns(headers: set):
    unknown = headers - KNOWN_FIELDS - ALIAS_FIELDS
    if unknown:
        logger.warning(f"Unrecognized CSV columns will be dropped: {unknown}")


def check_missing_columns(headers: set):
    missing = REQUIRED_FIELDS - headers - ALIAS_FIELDS
    if missing:
        logger.warning(f"Expected columns missing from CSV: {missing}")


def load_leads_from_csv(csv_path):
    with open(csv_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = set(reader.fieldnames or [])
        check_unknown_columns(headers)
        check_missing_columns(headers)

        leads = []
        for row in reader:
            payload = {
                "lead_id": row.get("lead_id") or row.get("company_name") or "",
                "company_name": row.get("company_name", ""),
                "industry": row.get("industry", ""),
                "company_size": row.get("company_size", "") or row.get("employee_count", ""),
                "website": row.get("website", "") or row.get("company_website", ""),
                "email": row.get("email", "") or row.get("contact_email", ""),
                "location": row.get("location", "") or row.get("city", ""),
                "description": row.get("description", "") or row.get("company_description", ""),
            }
            leads.append(Lead.model_validate(payload))
        return leads