"""
MedSafe AI — Patient-Facing Healthcare Safety Application
Main Streamlit dashboard with 5 modules.
"""

import json
import datetime
import streamlit as st

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="MedSafe AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Local module imports
# ---------------------------------------------------------------------------
from med_db import find_medicine, check_interaction, get_all_interactions, MEDICINES
from ocr_utils import extract_text_from_image
from symptom import analyze_symptoms, SYMPTOM_LIST
from risk_engine import calculate_risk

# ---------------------------------------------------------------------------
# LLaMA 3 helper (graceful fallback)
# ---------------------------------------------------------------------------

def query_llama(prompt: str, context: str = "") -> str:
    """Send a prompt to LLaMA 3 via Ollama. Returns AI text or fallback."""
    try:
        import ollama
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        response = ollama.chat(
            model="llama3",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are MedSafe AI, an educational healthcare assistant. "
                        "Provide clear, concise, and helpful information. "
                        "Always remind users that your responses are educational only "
                        "and not a substitute for professional medical advice."
                    ),
                },
                {"role": "user", "content": full_prompt},
            ],
        )
        return response["message"]["content"]
    except ImportError:
        return "⚠️ Ollama Python package is not installed. Run `pip install ollama` to enable AI features."
    except Exception as e:
        return f"⚠️ AI service unavailable. Make sure Ollama is running with LLaMA 3 (`ollama pull llama3`).\n\nError: {e}"

# ---------------------------------------------------------------------------
# Custom CSS — Professional Blue / White Medical Theme
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
/* ── Import Google Font ─────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root variables ─────────────────────────────────────── */
:root {
    --primary: #0A6EBD;
    --primary-light: #5DA7DB;
    --primary-dark: #064A80;
    --accent: #12B886;
    --bg-main: #F0F4F8;
    --bg-card: #FFFFFF;
    --text-primary: #1A2332;
    --text-secondary: #5A6B7F;
    --border: #E2E8F0;
    --safe: #12B886;
    --safe-bg: #E6FCF5;
    --caution: #F59F00;
    --caution-bg: #FFF9DB;
    --danger: #E03131;
    --danger-bg: #FFF5F5;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
    --radius: 12px;
}

/* ── Global resets ──────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background: var(--bg-main) !important;
}

/* ── Header bar ─────────────────────────────────────────── */
.main-header {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: var(--radius);
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-md);
    text-align: center;
}
.main-header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.main-header p {
    margin: 0.3rem 0 0;
    font-size: 0.95rem;
    opacity: 0.9;
    font-weight: 300;
}

/* ── Tab styling ────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 6px;
    gap: 4px;
    box-shadow: var(--shadow-sm);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.85rem;
    padding: 8px 16px;
    color: var(--text-secondary);
}
.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
    font-weight: 600;
}

/* ── Card containers ────────────────────────────────────── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease;
}
.card:hover {
    box-shadow: var(--shadow-md);
}

/* ── Severity badges ────────────────────────────────────── */
.badge-safe {
    display: inline-block;
    background: var(--safe-bg);
    color: var(--safe);
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid var(--safe);
}
.badge-caution {
    display: inline-block;
    background: var(--caution-bg);
    color: #B37800;
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid var(--caution);
}
.badge-danger {
    display: inline-block;
    background: var(--danger-bg);
    color: var(--danger);
    padding: 4px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid var(--danger);
}

/* ── Risk level cards ───────────────────────────────────── */
.risk-low      { border-left: 5px solid var(--safe);   }
.risk-moderate { border-left: 5px solid var(--caution); }
.risk-high     { border-left: 5px solid #E8590C;       }
.risk-critical { border-left: 5px solid var(--danger);  }

/* ── Disclaimer box ─────────────────────────────────────── */
.disclaimer {
    background: #EDF2FF;
    border: 1px solid #BAC8FF;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #364FC7;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
}

/* ── AI response box ────────────────────────────────────── */
.ai-response {
    background: linear-gradient(135deg, #F8F9FE 0%, #EDF2FF 100%);
    border: 1px solid #D0D7FF;
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
    margin-top: 1rem;
}
.ai-response-header {
    font-weight: 600;
    color: var(--primary);
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

/* ── Section label ──────────────────────────────────────── */
.section-label {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 1.05rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Timeline entry ─────────────────────────────────────── */
.timeline-entry {
    border-left: 3px solid var(--primary-light);
    padding-left: 1rem;
    margin-bottom: 1rem;
}
.timeline-time {
    font-size: 0.78rem;
    color: var(--text-secondary);
    font-weight: 500;
}

/* ── Misc fixes ─────────────────────────────────────────── */
.stMetric label { font-size: 0.85rem !important; }
div[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="main-header">
        <h1>🏥 MedSafe AI</h1>
        <p>AI-Assisted Medicine Safety &amp; Health Guidance — Educational Use Only</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "extracted_medicines" not in st.session_state:
    st.session_state.extracted_medicines = []
if "side_effect_log" not in st.session_state:
    st.session_state.side_effect_log = []

# ---------------------------------------------------------------------------
# Helper renderers
# ---------------------------------------------------------------------------

def severity_badge(severity: str) -> str:
    s = severity.lower()
    if s == "safe":
        return '<span class="badge-safe">✓ Safe</span>'
    elif s == "caution":
        return '<span class="badge-caution">⚠ Caution</span>'
    else:
        return '<span class="badge-danger">✕ Dangerous</span>'


def risk_card_class(level: str) -> str:
    return f"risk-{level.lower()}"

# ═══════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💊 Interaction Checker",
    "📋 Prescription OCR",
    "🩺 Symptom Solver",
    "📝 Side-Effect Monitor",
    "🚨 Emergency Risk",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — Medicine Interaction Checker
# ═══════════════════════════════════════════════════════════════════════════

with tab1:
    st.markdown('<div class="section-label">💊 Medicine Interaction Checker</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="disclaimer">ℹ️ This tool provides <b>educational</b> information about potential drug interactions. '
        'It is <b>not</b> a substitute for professional medical advice. Always consult your pharmacist or doctor.</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        drug_count = st.number_input(
            "How many medicines to check?", min_value=2, max_value=6, value=2, key="drug_count"
        )
    drug_names: list[str] = []
    cols = st.columns(min(int(drug_count), 3))
    for i in range(int(drug_count)):
        with cols[i % len(cols)]:
            name = st.text_input(f"Medicine {i+1}", key=f"drug_{i}", placeholder="e.g. Aspirin")
            if name.strip():
                drug_names.append(name.strip())

    if st.button("🔍 Check Interactions", key="btn_check_interactions", type="primary"):
        if len(drug_names) < 2:
            st.warning("Please enter at least 2 medicine names.")
        else:
            # Fuzzy match
            matched: list[str] = []
            for dn in drug_names:
                m = find_medicine(dn)
                if m:
                    matched.append(m)
                else:
                    st.warning(f'⚠️ "{dn}" not found in our database. Skipping.')

            if len(matched) >= 2:
                st.markdown("---")
                st.markdown("**Matched medicines:** " + ", ".join(f"`{m.title()}`" for m in matched))

                interactions = get_all_interactions(matched)
                if interactions:
                    for ix in interactions:
                        st.markdown(
                            f'<div class="card">'
                            f'<strong>{ix["drug_a"]}</strong> + <strong>{ix["drug_b"]}</strong> '
                            f'&nbsp;{severity_badge(ix["severity"])}'
                            f'<br><span style="color:var(--text-secondary);font-size:0.9rem;">{ix["reason"]}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.success("✅ No known interactions found between these medicines.")

                # AI Summary
                with st.spinner("🤖 Generating AI safety summary…"):
                    prompt = (
                        f"Analyze the following drug combination for a patient: {', '.join(m.title() for m in matched)}.\n"
                        f"Known interactions found: {json.dumps(interactions, indent=2) if interactions else 'None'}.\n\n"
                        "Provide a concise educational summary about:\n"
                        "1. Overall safety of this combination\n"
                        "2. Key things the patient should watch for\n"
                        "3. When to contact their doctor\n"
                        "Keep the response under 200 words."
                    )
                    ai_text = query_llama(prompt)

                st.markdown(
                    f'<div class="ai-response">'
                    f'<div class="ai-response-header">🤖 AI Safety Summary</div>'
                    f'{ai_text}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — Prescription OCR + AI Parsing
# ═══════════════════════════════════════════════════════════════════════════

with tab2:
    st.markdown('<div class="section-label">📋 Prescription OCR + AI Parsing</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="disclaimer">ℹ️ Upload a prescription image for automated text extraction and AI parsing. '
        'Results are for <b>reference only</b>. Always verify with your pharmacist.</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader("Upload prescription image", type=["jpg", "jpeg", "png"], key="rx_upload")

    if uploaded is not None:
        from PIL import Image
        image = Image.open(uploaded)
        st.image(image, caption="Uploaded Prescription", use_container_width=True)

        with st.spinner("🔍 Running OCR…"):
            raw_text = extract_text_from_image(image)

        with st.expander("📄 Raw OCR Text", expanded=False):
            st.code(raw_text, language="text")

        if raw_text.startswith("[ERROR]"):
            st.error(raw_text)
        else:
            with st.spinner("🤖 AI is parsing the prescription…"):
                prompt = (
                    "Extract all medicines from the following prescription text and return ONLY a valid JSON array. "
                    "Each object should have these keys: medicine, dosage, frequency, duration.\n"
                    "If you cannot determine a field, use \"N/A\".\n\n"
                    f"Prescription text:\n{raw_text}\n\n"
                    "Return ONLY the JSON array, no other text."
                )
                ai_parsed = query_llama(prompt)

            st.markdown(
                f'<div class="ai-response">'
                f'<div class="ai-response-header">🤖 AI-Parsed Prescription</div></div>',
                unsafe_allow_html=True,
            )

            # Try to parse JSON from AI response
            parsed_meds = []
            try:
                # Find JSON array in the response
                start = ai_parsed.find("[")
                end = ai_parsed.rfind("]") + 1
                if start != -1 and end > start:
                    parsed_meds = json.loads(ai_parsed[start:end])
            except (json.JSONDecodeError, ValueError):
                pass

            if parsed_meds:
                for med in parsed_meds:
                    med_name = med.get("medicine", "Unknown")
                    dosage = med.get("dosage", "N/A")
                    freq = med.get("frequency", "N/A")
                    dur = med.get("duration", "N/A")

                    # Validate against DB
                    db_match = find_medicine(med_name)
                    status = "✅ Found in database" if db_match else "⚠️ Not in database"

                    st.markdown(
                        f'<div class="card">'
                        f'<strong>{med_name}</strong> &nbsp;<small style="color:var(--text-secondary);">{status}</small><br>'
                        f'<span style="font-size:0.9rem;">Dosage: {dosage} &nbsp;|&nbsp; Frequency: {freq} &nbsp;|&nbsp; Duration: {dur}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    if db_match and db_match not in st.session_state.extracted_medicines:
                        st.session_state.extracted_medicines.append(db_match)
            else:
                st.info("AI could not extract structured data. Showing raw AI response:")
                st.markdown(ai_parsed)

            with st.expander("🔎 Raw AI JSON Response"):
                st.code(ai_parsed, language="json")

            if st.session_state.extracted_medicines:
                st.markdown("---")
                st.info(
                    f"**Medicines saved to session:** "
                    f"{', '.join(m.title() for m in st.session_state.extracted_medicines)} "
                    f"— available across all tabs."
                )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — Symptom & Doubt Solver
# ═══════════════════════════════════════════════════════════════════════════

with tab3:
    st.markdown('<div class="section-label">🩺 Symptom & Doubt Solver</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="disclaimer">⚠️ <b>This is NOT a medical diagnosis.</b> This tool provides general educational '
        'information only. Always consult a qualified healthcare professional for medical advice.</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        selected_symptoms = st.multiselect(
            "Select symptoms from the list",
            options=[s.title() for s in SYMPTOM_LIST],
            key="symptom_select",
        )
    with col_b:
        custom_symptom_text = st.text_area(
            "Or describe your symptoms",
            placeholder="e.g. I have a persistent headache and feel dizzy after standing up…",
            key="symptom_text",
            height=120,
        )

    if st.button("🔍 Analyze Symptoms", key="btn_symptoms", type="primary"):
        all_symptoms = [s.lower() for s in selected_symptoms]

        # Try to match custom text to known symptoms
        if custom_symptom_text.strip():
            for sym in SYMPTOM_LIST:
                if sym in custom_symptom_text.lower():
                    if sym not in all_symptoms:
                        all_symptoms.append(sym)

        if not all_symptoms:
            st.warning("Please select or describe at least one symptom.")
        else:
            results = analyze_symptoms(all_symptoms)

            if results:
                st.markdown("### 📋 Possible Conditions")
                for r in results:
                    sev = r["severity"]
                    sev_color = {"severe": "var(--danger)", "moderate": "var(--caution)", "mild": "var(--safe)"}.get(sev, "gray")
                    st.markdown(
                        f'<div class="card">'
                        f'<span style="color:{sev_color};font-weight:600;text-transform:uppercase;font-size:0.75rem;">{sev}</span><br>'
                        f'<strong>{r["condition"]}</strong> '
                        f'<small style="color:var(--text-secondary);">— related to: {r["symptom"]}</small><br>'
                        f'<span style="font-size:0.9rem;">{r["description"]}</span><br>'
                        f'<span style="font-size:0.85rem;color:var(--primary);">💡 {r["recommended_action"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No matching conditions found for the given symptoms in our database.")

            # AI enhanced response
            with st.spinner("🤖 Getting personalized guidance from AI…"):
                symptom_str = ", ".join(all_symptoms)
                prompt = (
                    f"A user reports the following symptoms: {symptom_str}.\n"
                    f"{'They also described: ' + custom_symptom_text if custom_symptom_text.strip() else ''}\n\n"
                    "As an educational health assistant, provide:\n"
                    "1. **Home Remedies** — safe home care suggestions\n"
                    "2. **Lifestyle Suggestions** — habits that may help\n"
                    "3. **Warning Signs** — when to see a doctor immediately\n\n"
                    "Keep the response concise (under 250 words). End with a reminder to consult a doctor."
                )
                ai_text = query_llama(prompt)

            with st.expander("🤖 AI Health Guidance", expanded=True):
                st.markdown(ai_text)
                st.markdown(
                    '<div class="disclaimer">🔔 Reminder: This AI-generated guidance is for <b>educational purposes only</b>. '
                    'It is not a diagnosis. Please consult a healthcare professional.</div>',
                    unsafe_allow_html=True,
                )

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — Side-Effect Monitor
# ═══════════════════════════════════════════════════════════════════════════

with tab4:
    st.markdown('<div class="section-label">📝 Side-Effect Monitor & Logger</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="disclaimer">ℹ️ Log and track medication side effects over time. AI analysis is '
        '<b>educational only</b> — report serious side effects to your doctor.</div>',
        unsafe_allow_html=True,
    )

    with st.form("side_effect_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            se_age = st.number_input("Age", min_value=1, max_value=120, value=30, key="se_age")
        with col2:
            se_gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="se_gender")
        with col3:
            se_medicine = st.text_input("Medicine Name", placeholder="e.g. Metformin", key="se_medicine")

        col4, col5 = st.columns(2)
        with col4:
            se_dosage = st.text_input("Dosage", placeholder="e.g. 500mg twice daily", key="se_dosage")
        with col5:
            se_description = st.text_area(
                "Describe the side effect",
                placeholder="e.g. I feel dizzy and nauseous 30 minutes after taking the medicine…",
                key="se_desc",
                height=100,
            )

        submitted = st.form_submit_button("📝 Log & Analyze", type="primary")

    if submitted:
        # Validation
        if not se_medicine.strip():
            st.error("Please enter a medicine name.")
        elif not se_description.strip():
            st.error("Please describe the side effect you experienced.")
        else:
            entry = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "age": se_age,
                "gender": se_gender,
                "medicine": se_medicine.strip(),
                "dosage": se_dosage.strip() or "Not specified",
                "description": se_description.strip(),
                "ai_analysis": "",
            }

            # AI analysis
            with st.spinner("🤖 Analyzing your report…"):
                prompt = (
                    f"A {se_age}-year-old {se_gender.lower()} patient is taking {se_medicine} "
                    f"(dosage: {se_dosage or 'not specified'}) and reports:\n"
                    f'"{se_description}"\n\n'
                    "As an educational health assistant, provide:\n"
                    "1. Whether this is a known side effect of this medicine\n"
                    "2. How common this side effect typically is\n"
                    "3. What the patient should do (continue, adjust, or seek medical help)\n"
                    "Keep it concise (under 150 words). End with a reminder to consult their doctor."
                )
                ai_text = query_llama(prompt)
                entry["ai_analysis"] = ai_text

            st.session_state.side_effect_log.append(entry)

            st.success("✅ Side effect logged successfully!")
            st.markdown(
                f'<div class="ai-response">'
                f'<div class="ai-response-header">🤖 AI Analysis</div>'
                f'{ai_text}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Timeline / History
    if st.session_state.side_effect_log:
        st.markdown("---")
        st.markdown("### 📅 Side-Effect History")
        for i, entry in enumerate(reversed(st.session_state.side_effect_log)):
            st.markdown(
                f'<div class="timeline-entry">'
                f'<div class="timeline-time">🕐 {entry["timestamp"]}</div>'
                f'<strong>{entry["medicine"]}</strong> ({entry["dosage"]})<br>'
                f'<span style="font-size:0.9rem;color:var(--text-secondary);">{entry["description"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            with st.expander(f"🤖 AI Analysis — Entry {len(st.session_state.side_effect_log) - i}"):
                st.markdown(entry.get("ai_analysis", "No analysis available."))
    else:
        st.info("No side effects logged yet. Use the form above to log your first entry.")

# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 — Emergency Risk Predictor
# ═══════════════════════════════════════════════════════════════════════════

with tab5:
    st.markdown('<div class="section-label">🚨 Emergency Risk Predictor</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="disclaimer">⚠️ This is an <b>educational risk estimation tool</b>. It does NOT replace '
        'professional emergency assessment. If you feel unwell, <b>call emergency services immediately</b>.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### Enter Your Vitals")
    col1, col2, col3 = st.columns(3)
    with col1:
        v_hr = st.number_input("Heart Rate (bpm)", min_value=20, max_value=250, value=72, key="v_hr")
        v_temp = st.number_input("Temperature (°F)", min_value=90.0, max_value=110.0, value=98.6, step=0.1, key="v_temp")
    with col2:
        v_sbp = st.number_input("Systolic BP (mmHg)", min_value=40, max_value=300, value=120, key="v_sbp")
        v_dbp = st.number_input("Diastolic BP (mmHg)", min_value=20, max_value=200, value=80, key="v_dbp")
    with col3:
        v_spo2 = st.number_input("SpO₂ (%)", min_value=50.0, max_value=100.0, value=98.0, step=0.5, key="v_spo2")

    if st.button("🔍 Calculate Risk", key="btn_risk", type="primary"):
        result = calculate_risk(
            heart_rate=v_hr,
            systolic=v_sbp,
            diastolic=v_dbp,
            temperature=v_temp,
            spo2=v_spo2,
        )

        score = result["score"]
        level = result["level"]
        factors = result["factors"]
        action = result["action"]

        # Color mapping
        level_colors = {
            "Low": ("var(--safe)", "#E6FCF5"),
            "Moderate": ("var(--caution)", "#FFF9DB"),
            "High": ("#E8590C", "#FFF4E6"),
            "Critical": ("var(--danger)", "#FFF5F5"),
        }
        color, bg = level_colors.get(level, ("gray", "#F8F9FA"))

        st.markdown("---")

        # Score display
        mc1, mc2 = st.columns([1, 2])
        with mc1:
            st.metric("Risk Score", f"{score}%", delta=None)
            st.progress(score / 100)
        with mc2:
            st.markdown(
                f'<div class="card {risk_card_class(level)}" style="background:{bg};">'
                f'<span style="color:{color};font-weight:700;font-size:1.4rem;">{level} Risk</span><br>'
                f'<span style="font-size:0.95rem;font-weight:500;">{action}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Contributing factors
        if factors:
            st.markdown("**Contributing Risk Factors:**")
            for f in factors:
                st.markdown(f"- ⚠️ {f}")
        else:
            st.success("✅ All vitals are within normal ranges.")

        # AI explanation
        with st.spinner("🤖 Generating educational explanation…"):
            prompt = (
                f"A patient has the following vitals:\n"
                f"- Heart Rate: {v_hr} bpm\n"
                f"- Blood Pressure: {v_sbp}/{v_dbp} mmHg\n"
                f"- Temperature: {v_temp}°F\n"
                f"- Oxygen Saturation: {v_spo2}%\n\n"
                f"The calculated risk level is: {level} ({score}%).\n"
                f"Risk factors identified: {', '.join(factors) if factors else 'None'}.\n\n"
                "Provide a brief educational explanation of:\n"
                "1. What these vital signs mean\n"
                "2. Why the risk level was assigned\n"
                "3. General guidance (not a diagnosis)\n"
                "Keep it under 200 words."
            )
            ai_text = query_llama(prompt)

        st.markdown(
            f'<div class="ai-response">'
            f'<div class="ai-response-header">🤖 AI Risk Explanation</div>'
            f'{ai_text}'
            f'</div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:var(--text-secondary);font-size:0.8rem;padding:1rem 0;">'
    '🏥 MedSafe AI — Educational Healthcare Safety Tool<br>'
    'All AI outputs are for <b>educational purposes only</b> and do not constitute medical advice.<br>'
    'Always consult a qualified healthcare professional for medical decisions.'
    '</div>',
    unsafe_allow_html=True,
)
