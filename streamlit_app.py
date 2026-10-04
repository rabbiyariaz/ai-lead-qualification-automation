import html

import streamlit as st

from app.config.settings import settings
from app.llm.client import create_llm_client
from app.pipeline.orchestrator import qualify_lead


st.set_page_config(
    page_title="Lead Qualifier",
    page_icon="L",
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        :root {
            --ink: #17212b;
            --muted: #667482;
            --line: #d9e1e6;
            --paper: #f7faf8;
            --accent: #0f766e;
        }

        .stApp {
            background: linear-gradient(135deg, #f7faf8 0%, #eef5f2 52%, #f7f3eb 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 850px;
            padding: 4rem 2rem 5rem;
        }

        h1, h2, h3, p, label {
            font-family: Georgia, "Times New Roman", serif;
        }

        h1 {
            color: var(--ink);
            font-size: clamp(2.4rem, 6vw, 4.5rem);
            letter-spacing: 0;
            line-height: 0.98;
            margin-bottom: 0.75rem;
        }

        .eyebrow {
            color: var(--accent);
            font-family: "Courier New", monospace;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }

        .intro {
            color: var(--muted);
            font-size: 1.08rem;
            line-height: 1.6;
            margin-bottom: 2.4rem;
            max-width: 620px;
        }

        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid rgba(217, 225, 230, 0.9);
            border-radius: 8px;
            padding: 1.6rem;
            box-shadow: 0 18px 50px rgba(38, 62, 74, 0.08);
        }

        [data-testid="stTextInput"] label,
        [data-testid="stTextArea"] label,
        [data-testid="stSelectbox"] label {
            color: var(--ink);
            font-size: 0.94rem;
            font-weight: 700;
        }

        [data-testid="stFormSubmitButton"] button {
            background: var(--accent);
            border: 0;
            border-radius: 5px;
            color: white;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1rem;
            font-weight: 700;
            min-height: 3rem;
            width: 100%;
        }

        [data-testid="stFormSubmitButton"] button:hover {
            background: #115e59;
            color: white;
        }

        .result-card {
            background: #fff;
            border: 1px solid var(--line);
            border-left: 7px solid var(--result-color);
            border-radius: 8px;
            box-shadow: 0 18px 50px rgba(38, 62, 74, 0.1);
            margin-top: 2.2rem;
            padding: 1.8rem;
        }

        .result-header {
            align-items: center;
            display: flex;
            gap: 1rem;
            justify-content: space-between;
            margin-bottom: 1.4rem;
        }

        .decision {
            color: var(--result-color);
            font-family: "Courier New", monospace;
            font-size: 0.86rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .metrics {
            display: flex;
            gap: 2.5rem;
        }

        .metric-label {
            color: var(--muted);
            font-family: "Courier New", monospace;
            font-size: 0.67rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .metric-value {
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.75rem;
            font-weight: 700;
        }

        .result-label {
            color: var(--accent);
            font-family: "Courier New", monospace;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            margin-bottom: 0.3rem;
            text-transform: uppercase;
        }

        .result-copy {
            color: var(--ink);
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1rem;
            line-height: 1.55;
            margin-bottom: 1.3rem;
        }

        @media (max-width: 600px) {
            .block-container { padding: 2.5rem 1rem 3rem; }
            .result-header { align-items: flex-start; flex-direction: column; }
            .metrics { gap: 1.5rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_llm_client():
    return create_llm_client(settings.groq_model, settings.groq_api_key)


def next_best_action(decision: str) -> str:
    actions = {
        "qualified": "Prioritize outreach and schedule a discovery call.",
        "disqualified": "Do not pursue now; keep the lead out of the active sales queue.",
        "review": "Review the signals manually and confirm fit before contacting the lead.",
    }
    return actions.get(decision, actions["review"])


def safe_text(value, fallback="Not provided") -> str:
    text = str(value or "").strip()
    return html.escape(text) if text else fallback


st.markdown('<div class="eyebrow">Inbound intelligence / 01</div>', unsafe_allow_html=True)
st.title("Lead Qualifier")
st.markdown(
    '<p class="intro">Turn an inbound enquiry into a clear next move. Add the lead details below and let the qualification pipeline assess fit, intent, and urgency.</p>',
    unsafe_allow_html=True,
)

with st.form("lead_qualification_form"):
    st.subheader("Lead details")
    first_row = st.columns(2)
    with first_row[0]:
        company_name = st.text_input("Company name", placeholder="Acme Home Services")
        website = st.text_input("Website", placeholder="https://example.com")
        industry = st.text_input("Industry", placeholder="Home services")
        contact_email = st.text_input("Contact email", placeholder="hello@example.com")
    with first_row[1]:
        company_size = st.text_input("Company size", placeholder="11-50 employees")
        location = st.text_input("Location", placeholder="Manchester, UK")
        description = st.text_area(
            "Company description",
            placeholder="What the company does, who it serves, and what it may need...",
            height=144,
        )

    submitted = st.form_submit_button("Qualify This Lead")


if submitted:
    if not company_name.strip():
        st.error("Please enter a company name before qualifying the lead.")
    else:
        payload = {
            "company_name": company_name.strip(),
            "website": website.strip(),
            "industry": industry.strip(),
            "contact_email": contact_email.strip(),
            "company_size": company_size.strip(),
            "location": location.strip(),
            "description": description.strip(),
        }

        with st.spinner("Assessing lead signals..."):
            try:
                result = qualify_lead(payload, llm_client=get_llm_client())
            except Exception as exc:
                st.error(f"The lead could not be qualified: {exc}")
            else:
                decision = str(result.get("decision", "review")).lower()
                result_color = {
                    "qualified": "#15803d",
                    "disqualified": "#b42318",
                    "review": "#b45309",
                }.get(decision, "#b45309")
                score = result.get("score", 0)
                confidence = result.get("confidence", 0.0)
                try:
                    confidence_display = f"{float(confidence) * 100:.0f}%"
                except (TypeError, ValueError):
                    confidence_display = safe_text(confidence)

                st.markdown(
                    f"""
                    <section class="result-card" style="--result-color: {result_color};">
                        <div class="result-header">
                            <div class="decision">{safe_text(decision).title()}</div>
                            <div class="metrics">
                                <div><div class="metric-label">Score</div><div class="metric-value">{safe_text(score, "0")}</div></div>
                                <div><div class="metric-label">Confidence</div><div class="metric-value">{confidence_display}</div></div>
                            </div>
                        </div>
                        <div class="result-label">Reason</div>
                        <div class="result-copy">{safe_text(result.get("reason"))}</div>
                        <div class="result-label">Next best action</div>
                        <div class="result-copy">{safe_text(next_best_action(decision))}</div>
                    </section>
                    """,
                    unsafe_allow_html=True,
                )
