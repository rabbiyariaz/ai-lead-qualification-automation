import os
import time
from datetime import datetime
from pyairtable import Api

from app.config.settings import settings
from app.llm.client import create_llm_client
from app.pipeline.orchestrator import qualify_lead

AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
TABLE_NAME = "Leads"

CHECK_INTERVAL_SECONDS = 120  

api = Api(AIRTABLE_API_KEY)
table = api.table(AIRTABLE_BASE_ID, TABLE_NAME)

llm_client = create_llm_client(settings.groq_model, settings.groq_api_key)

DECISION_TO_STATUS = {
    "qualified": "Qualified",
    "disqualified": "Disqualified",
    "review": "Needs Review",
}


def process_new_leads():
    # Catches both "New" and blank Status (e.g. from form submissions)
    new_leads = table.all(formula="OR({Status} = 'New', {Status} = '')")

    if not new_leads:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No new leads.")
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(new_leads)} new lead(s)")

    for record in new_leads:
        record_id = record["id"]
        fields = record["fields"]

        payload = {
            "company_name": fields.get("company_name"),
            "website": fields.get("website"),
            "industry": fields.get("industry"),
            "contact_email": fields.get("contact_email"),
            "company_size": fields.get("company_size"),
            "location": fields.get("location"),
            "description": fields.get("description"),
        }

        try:
            result = qualify_lead(payload, llm_client=llm_client)
        except Exception as exc:
            print(f"  ERROR processing {payload.get('company_name')}: {exc}")
            continue

        decision = result.get("decision", "review")
        status = DECISION_TO_STATUS.get(decision, "Needs Review")

        print(f"  {payload['company_name']}: {decision} -> {status} "
              f"(score: {result.get('score')}, confidence: {result.get('confidence')})")

        table.update(record_id, {
            "Status": status,
            "decision": decision,
            "score": result.get("score", 0),
            "stage": str(result.get("stage", "")),
            "reason": str(result.get("reason", "")),
            "confidence": result.get("confidence", 0.0),
            "capacity": str(result.get("capacity", "")),
            "growth_intent": str(result.get("growth_intent", "")),
            "customer_acquisition_need": str(result.get("customer_acquisition_need", "")),
            "ambiguity": bool(result.get("ambiguity", False)),
        })


if __name__ == "__main__":
    print(f"Starting pipeline. Checking every {CHECK_INTERVAL_SECONDS} seconds. Press Ctrl+C to stop.\n")
    while True:
        process_new_leads()
        time.sleep(CHECK_INTERVAL_SECONDS)































# import os
# from pyairtable import Api

# from app.config.settings import settings
# from app.llm.client import create_llm_client
# from app.pipeline.orchestrator import qualify_lead

# AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
# AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
# TABLE_NAME = "Leads"

# api = Api(AIRTABLE_API_KEY)
# table = api.table(AIRTABLE_BASE_ID, TABLE_NAME)

# llm_client = create_llm_client(settings.groq_model, settings.groq_api_key)

# # UPDATE these once you confirm the real decision strings
# DECISION_TO_STATUS = {
#     "qualified": "Qualified",
#     "disqualified": "Disqualified",
#     "review": "Needs Review",
# }

# new_leads = new_leads = table.all(formula="OR({Status} = 'New', {Status} = '')")
# print(f"Found {len(new_leads)} new lead(s)\n")

# for record in new_leads:
#     record_id = record["id"]
#     fields = record["fields"]

#     payload = {
#         "company_name": fields.get("company_name"),
#         "website": fields.get("website"),
#         "industry": fields.get("industry"),
#         "contact_email": fields.get("contact_email"),
#         "company_size": fields.get("company_size"),
#         "location": fields.get("location"),
#         "description": fields.get("description"),
#     }

#     result = qualify_lead(payload, llm_client=llm_client)

#     decision = result.get("decision", "review")
#     status = DECISION_TO_STATUS.get(decision, "Needs Review")

#     print(f"{payload['company_name']}: {decision} -> {status} "
#           f"(score: {result.get('score')}, confidence: {result.get('confidence')})")

#     table.update(record_id, {
#         "Status": status,
#         "decision": decision,
#         "score": result.get("score", 0),
#         "stage": str(result.get("stage", "")),
#         "reason": str(result.get("reason", "")),
#         "confidence": result.get("confidence", 0.0),
#         "capacity": str(result.get("capacity", "")),
#         "growth_intent": str(result.get("growth_intent", "")),
#         "customer_acquisition_need": str(result.get("customer_acquisition_need", "")),
#         "ambiguity": bool(result.get("ambiguity", False)),
#     })

# print("\nDone — Airtable updated.")