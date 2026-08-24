import os

from app.config.settings import settings
from app.llm.client import create_llm_client
from app.pipeline.orchestrator import run_qualification_pipeline
from dotenv import load_dotenv
load_dotenv()


def main():
    llm = create_llm_client(
        model=os.getenv("GROQ_MODEL", settings.groq_model),
        api_key=os.getenv("GROQ_API_KEY", settings.groq_api_key),
    )

    run_qualification_pipeline(
        "sample_leads.csv",
        "qualified_leads.csv",
        llm_client=llm,
    )


if __name__ == "__main__":
    main()