import csv


def write_qualified_leads(output_csv_path, rows):
    fieldnames = [
        "lead_id",
        "company_name",
        "industry",
        "company_size",
        "website",
        "email",
        "location",
        "description",
        "decision",
        "score",
        "stage",
        "reason",
        "llm_reasoning",
        "confidence",
        "capacity",
        "growth_intent",
        "customer_acquisition_need",
        "ambiguity",
    ]

    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)