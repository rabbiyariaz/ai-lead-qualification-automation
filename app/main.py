from fastapi import FastAPI, HTTPException

from app.config.settings import settings
from app.ingestion.csv_loader import load_leads_from_csv
from app.llm.client import create_llm_client
from app.output.csv_writer import write_qualified_leads
from app.pipeline.orchestrator import qualify_lead

from fastapi import UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io
import csv

app = FastAPI(title="AI Lead Qualification API", version="1.0.0")


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/v1/leads/qualify")
def qualify_lead_api(payload: dict):
    try:
        llm_client = create_llm_client(settings.groq_model, settings.groq_api_key)
        result = qualify_lead(payload, llm_client=llm_client)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/leads/qualify/csv")
async def qualify_csv_api(file: UploadFile = File(...)):
    try:
        # 1. Validate file
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported."
            )

        # 2. Read uploaded CSV directly into memory
        content = await file.read()

        text = content.decode("utf-8-sig")
        csv_file = io.StringIO(text)

        # 3. Read CSV rows
        reader = csv.DictReader(csv_file)

        # 4. Create LLM client
        llm_client = create_llm_client(
            settings.groq_model,
            settings.groq_api_key
        )

        qualified_rows = []

        # 5. Qualify each lead
        for row in reader:

            result = qualify_lead(
                row,
                llm_client=llm_client
            )


            merged = {
    **row,
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

            qualified_rows.append(merged)

        # 6. Create output CSV in memory
        output = io.StringIO()

        fieldnames = [
    *reader.fieldnames,
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

        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(qualified_rows)

        # 7. Convert to bytes
        output.seek(0)

        csv_bytes = io.BytesIO(
            output.getvalue().encode("utf-8")
        )

        # 8. Return CSV directly as download
        base_name = file.filename.rsplit(".", 1)[0]

        return StreamingResponse(
            csv_bytes,
            media_type="text/csv",
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{base_name}_qualified.csv"'
                )
            }
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc