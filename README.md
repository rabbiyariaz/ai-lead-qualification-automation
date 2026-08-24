# AI Lead Qualification Pipeline

This project qualifies inbound leads using a deterministic rule-based pipeline and optional LLM review for ambiguous leads.

## Run locally

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your Groq API key.

4. Run the CLI entry point:

```bash
python main.py
```

5. Or run the FastAPI app:

```bash
uvicorn app.main:app --reload
```

## Modules

- `app/models`: typed data models
- `app/pipeline`: industry gate, feature extraction, scoring, orchestration
- `app/llm`: provider abstraction and Groq integration
- `app/ingestion`: CSV ingestion
- `app/output`: CSV output writing
- `app/config`: settings and environment variables

## Current behavior

- hard industry filter
- rule-based ICP scoring
- LLM review only for ambiguous leads
- CSV export of qualified results
