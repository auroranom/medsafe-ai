"""
symptom.py — Rule-based symptom analysis engine.

Provides:
  - SYMPTOM_DB: mapping of symptoms to possible conditions.
  - SYMPTOM_LIST: flat list of all known symptom strings (for dropdowns).
  - analyze_symptoms(symptom_list): match symptoms to conditions.
"""

# ---------------------------------------------------------------------------
# Symptom → Condition Database
# ---------------------------------------------------------------------------

SYMPTOM_DB: dict[str, list[dict]] = {
    "fever": [
        {
            "condition": "Common Cold / Flu",
            "description": "Viral upper respiratory infection",
            "recommended_action": "Rest, hydrate, monitor temperature",
            "severity": "mild",
        },
        {
            "condition": "Bacterial Infection",
            "description": "May indicate bacterial cause requiring antibiotics",
            "recommended_action": "Consult a doctor if fever persists >3 days or exceeds 103°F",
            "severity": "moderate",
        },
        {
            "condition": "COVID-19",
            "description": "SARS-CoV-2 infection",
            "recommended_action": "Isolate, get tested, consult healthcare provider",
            "severity": "moderate",
        },
    ],
    "headache": [
        {
            "condition": "Tension Headache",
            "description": "Stress or muscle tension related",
            "recommended_action": "Rest, over-the-counter pain relief, manage stress",
            "severity": "mild",
        },
        {
            "condition": "Migraine",
            "description": "Neurological condition with intense headache",
            "recommended_action": "Consult a doctor for recurring episodes; avoid triggers",
            "severity": "moderate",
        },
        {
            "condition": "Dehydration",
            "description": "Insufficient fluid intake",
            "recommended_action": "Increase water intake, rest",
            "severity": "mild",
        },
    ],
    "cough": [
        {
            "condition": "Common Cold",
            "description": "Viral infection of upper airways",
            "recommended_action": "Rest, warm fluids, honey (adults)",
            "severity": "mild",
        },
        {
            "condition": "Bronchitis",
            "description": "Inflammation of bronchial tubes",
            "recommended_action": "See a doctor if cough persists >2 weeks or produces colored mucus",
            "severity": "moderate",
        },
        {
            "condition": "Allergic Reaction",
            "description": "Triggered by allergens (dust, pollen, etc.)",
            "recommended_action": "Identify and avoid allergens; consider antihistamines",
            "severity": "mild",
        },
    ],
    "chest pain": [
        {
            "condition": "Angina",
            "description": "Reduced blood flow to heart muscle",
            "recommended_action": "Seek immediate medical attention",
            "severity": "severe",
        },
        {
            "condition": "GERD / Acid Reflux",
            "description": "Gastric acid irritating the esophagus",
            "recommended_action": "Antacids, avoid spicy food, elevate head during sleep",
            "severity": "mild",
        },
        {
            "condition": "Muscle Strain",
            "description": "Chest wall muscle injury",
            "recommended_action": "Rest, OTC pain relief, apply ice",
            "severity": "mild",
        },
    ],
    "nausea": [
        {
            "condition": "Gastritis",
            "description": "Inflammation of stomach lining",
            "recommended_action": "Bland diet, avoid spicy/acidic food, consult doctor if persistent",
            "severity": "mild",
        },
        {
            "condition": "Food Poisoning",
            "description": "Bacterial or viral contamination of food",
            "recommended_action": "Stay hydrated, rest; see doctor if symptoms are severe",
            "severity": "moderate",
        },
        {
            "condition": "Medication Side Effect",
            "description": "Some medicines cause nausea as a common side effect",
            "recommended_action": "Take with food; consult prescribing doctor",
            "severity": "mild",
        },
    ],
    "fatigue": [
        {
            "condition": "Anemia",
            "description": "Low red blood cell count / hemoglobin",
            "recommended_action": "Blood test recommended; increase iron-rich foods",
            "severity": "moderate",
        },
        {
            "condition": "Hypothyroidism",
            "description": "Underactive thyroid gland",
            "recommended_action": "Thyroid function test (TSH); consult endocrinologist",
            "severity": "moderate",
        },
        {
            "condition": "Sleep Deprivation",
            "description": "Insufficient or poor-quality sleep",
            "recommended_action": "Improve sleep hygiene, aim for 7–9 hours",
            "severity": "mild",
        },
    ],
    "shortness of breath": [
        {
            "condition": "Asthma",
            "description": "Chronic airway inflammation",
            "recommended_action": "Use prescribed inhaler; see pulmonologist",
            "severity": "moderate",
        },
        {
            "condition": "Pneumonia",
            "description": "Lung infection",
            "recommended_action": "Seek medical attention promptly",
            "severity": "severe",
        },
        {
            "condition": "Anxiety / Panic Attack",
            "description": "Stress-induced breathing difficulty",
            "recommended_action": "Breathing exercises, reduce stressors, consider therapy",
            "severity": "mild",
        },
    ],
    "dizziness": [
        {
            "condition": "Low Blood Pressure",
            "description": "Hypotension causing reduced brain perfusion",
            "recommended_action": "Rise slowly, stay hydrated, check BP",
            "severity": "mild",
        },
        {
            "condition": "Inner Ear Disorder (Vertigo)",
            "description": "BPPV or labyrinthitis",
            "recommended_action": "Consult ENT specialist; Epley maneuver may help",
            "severity": "moderate",
        },
        {
            "condition": "Dehydration",
            "description": "Insufficient fluid intake",
            "recommended_action": "Drink fluids, rest in a cool area",
            "severity": "mild",
        },
    ],
    "sore throat": [
        {
            "condition": "Viral Pharyngitis",
            "description": "Common viral throat infection",
            "recommended_action": "Warm salt-water gargle, rest, warm fluids",
            "severity": "mild",
        },
        {
            "condition": "Strep Throat",
            "description": "Bacterial Group A Streptococcus infection",
            "recommended_action": "Consult doctor; antibiotics may be needed",
            "severity": "moderate",
        },
    ],
    "abdominal pain": [
        {
            "condition": "Gastritis / Peptic Ulcer",
            "description": "Inflammation or ulceration of stomach lining",
            "recommended_action": "Avoid NSAIDs and spicy food; consult gastroenterologist",
            "severity": "moderate",
        },
        {
            "condition": "Appendicitis",
            "description": "Inflammation of the appendix (right lower abdomen)",
            "recommended_action": "Seek emergency care if pain is severe and localized",
            "severity": "severe",
        },
        {
            "condition": "Irritable Bowel Syndrome (IBS)",
            "description": "Functional GI disorder with cramping",
            "recommended_action": "Dietary changes, stress management, consult GI specialist",
            "severity": "mild",
        },
    ],
    "diarrhea": [
        {
            "condition": "Viral Gastroenteritis",
            "description": "Stomach flu caused by a virus",
            "recommended_action": "Stay hydrated with ORS; bland diet",
            "severity": "mild",
        },
        {
            "condition": "Food Intolerance",
            "description": "Lactose or gluten intolerance",
            "recommended_action": "Identify trigger foods; consider allergy testing",
            "severity": "mild",
        },
        {
            "condition": "Bacterial Infection",
            "description": "Salmonella, E. coli, etc.",
            "recommended_action": "See a doctor if bloody stools or lasts >3 days",
            "severity": "moderate",
        },
    ],
    "joint pain": [
        {
            "condition": "Osteoarthritis",
            "description": "Degenerative joint disease",
            "recommended_action": "Exercise, weight management, OTC pain relief",
            "severity": "moderate",
        },
        {
            "condition": "Rheumatoid Arthritis",
            "description": "Autoimmune joint inflammation",
            "recommended_action": "Consult rheumatologist; early treatment is important",
            "severity": "moderate",
        },
        {
            "condition": "Gout",
            "description": "Uric acid crystal deposition in joints",
            "recommended_action": "Low-purine diet, hydrate, consult doctor",
            "severity": "moderate",
        },
    ],
    "rash": [
        {
            "condition": "Allergic Dermatitis",
            "description": "Skin reaction to allergens",
            "recommended_action": "Avoid trigger, antihistamines, topical corticosteroids",
            "severity": "mild",
        },
        {
            "condition": "Drug Reaction",
            "description": "Adverse skin reaction to medication",
            "recommended_action": "Stop suspected medication and consult doctor immediately",
            "severity": "moderate",
        },
        {
            "condition": "Eczema",
            "description": "Chronic inflammatory skin condition",
            "recommended_action": "Moisturize, avoid irritants, consult dermatologist",
            "severity": "mild",
        },
    ],
    "back pain": [
        {
            "condition": "Muscle Strain",
            "description": "Overuse or injury to back muscles",
            "recommended_action": "Rest, gentle stretching, OTC pain relief",
            "severity": "mild",
        },
        {
            "condition": "Herniated Disc",
            "description": "Disc pressing on spinal nerves",
            "recommended_action": "See orthopedic or spine specialist; imaging may be needed",
            "severity": "moderate",
        },
        {
            "condition": "Kidney Stones",
            "description": "Pain radiating to lower back / flank",
            "recommended_action": "Seek medical attention; hydrate, pain management",
            "severity": "severe",
        },
    ],
    "vomiting": [
        {
            "condition": "Food Poisoning",
            "description": "Contaminated food or water",
            "recommended_action": "Stay hydrated; see doctor if severe or bloody",
            "severity": "moderate",
        },
        {
            "condition": "Gastroenteritis",
            "description": "Viral stomach infection",
            "recommended_action": "ORS, rest, bland diet",
            "severity": "mild",
        },
        {
            "condition": "Medication Side Effect",
            "description": "Common with certain antibiotics, opioids, chemo",
            "recommended_action": "Talk to your doctor about anti-nausea options",
            "severity": "mild",
        },
    ],
    "insomnia": [
        {
            "condition": "Stress / Anxiety",
            "description": "Mental health-related sleep disruption",
            "recommended_action": "Sleep hygiene, relaxation techniques, consider CBT-I",
            "severity": "mild",
        },
        {
            "condition": "Medication Side Effect",
            "description": "Stimulants, SSRIs, steroids can disrupt sleep",
            "recommended_action": "Discuss with prescribing physician",
            "severity": "mild",
        },
    ],
    "swelling": [
        {
            "condition": "Edema",
            "description": "Fluid retention in tissues",
            "recommended_action": "Elevate limbs, reduce salt, check kidney / heart function",
            "severity": "moderate",
        },
        {
            "condition": "Allergic Reaction",
            "description": "Angioedema from allergens",
            "recommended_action": "Antihistamines; seek emergency care if airway is affected",
            "severity": "moderate",
        },
    ],
    "muscle pain": [
        {
            "condition": "Overexertion / Exercise Injury",
            "description": "Muscle strain from physical activity",
            "recommended_action": "Rest, ice, gentle stretching",
            "severity": "mild",
        },
        {
            "condition": "Fibromyalgia",
            "description": "Chronic widespread musculoskeletal pain",
            "recommended_action": "Consult rheumatologist; exercise and stress management",
            "severity": "moderate",
        },
        {
            "condition": "Statin Side Effect",
            "description": "Muscle pain is a known side effect of statin medications",
            "recommended_action": "Report to prescribing doctor",
            "severity": "mild",
        },
    ],
    "frequent urination": [
        {
            "condition": "Urinary Tract Infection (UTI)",
            "description": "Bacterial infection of the urinary system",
            "recommended_action": "See doctor; antibiotics usually needed",
            "severity": "moderate",
        },
        {
            "condition": "Diabetes",
            "description": "High blood sugar causes increased urination",
            "recommended_action": "Blood glucose test recommended",
            "severity": "moderate",
        },
    ],
    "weight loss": [
        {
            "condition": "Hyperthyroidism",
            "description": "Overactive thyroid gland",
            "recommended_action": "Thyroid function tests; consult endocrinologist",
            "severity": "moderate",
        },
        {
            "condition": "Diabetes (uncontrolled)",
            "description": "Unexplained weight loss can signal diabetes",
            "recommended_action": "Blood glucose and HbA1c tests",
            "severity": "moderate",
        },
        {
            "condition": "Malnutrition / Malabsorption",
            "description": "Inadequate nutrient absorption",
            "recommended_action": "Nutritional assessment; check for celiac or GI issues",
            "severity": "moderate",
        },
    ],
    "palpitations": [
        {
            "condition": "Anxiety / Panic Attack",
            "description": "Stress-induced heart racing",
            "recommended_action": "Breathing exercises, stress reduction, consider therapy",
            "severity": "mild",
        },
        {
            "condition": "Arrhythmia",
            "description": "Irregular heart rhythm",
            "recommended_action": "ECG / Holter monitor recommended; consult cardiologist",
            "severity": "moderate",
        },
        {
            "condition": "Hyperthyroidism",
            "description": "Excess thyroid hormones can cause rapid heartbeat",
            "recommended_action": "Thyroid function test",
            "severity": "moderate",
        },
    ],
}

# Flat sorted list for UI dropdowns
SYMPTOM_LIST: list[str] = sorted(SYMPTOM_DB.keys())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_symptoms(symptoms: list[str]) -> list[dict]:
    """Analyze a list of symptom strings and return matched conditions.

    Parameters
    ----------
    symptoms : list[str]
        Symptom names (should match keys in SYMPTOM_DB).

    Returns
    -------
    list[dict]
        Each dict:  symptom, condition, description, recommended_action, severity.
        Sorted by severity descending (severe → moderate → mild).
    """
    severity_order = {"severe": 0, "moderate": 1, "mild": 2}
    results: list[dict] = []

    for symptom in symptoms:
        key = symptom.strip().lower()
        if key in SYMPTOM_DB:
            for cond in SYMPTOM_DB[key]:
                results.append({
                    "symptom": key.title(),
                    **cond,
                })

    results.sort(key=lambda r: severity_order.get(r.get("severity", "mild"), 3))
    return results
