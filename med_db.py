"""
med_db.py — Curated medicine database and drug-drug interaction checker.

Provides:
  - MEDICINES: dict of common medicines with category and side effects.
  - INTERACTIONS: list of known drug-drug interaction records.
  - find_medicine(name): fuzzy-match a user-typed name to a known medicine.
  - check_interaction(drug_a, drug_b): look up interaction severity.
  - get_all_interactions(drug_list): check every pair in a list of drugs.
"""

from rapidfuzz import process, fuzz

# ---------------------------------------------------------------------------
# Medicine catalogue
# ---------------------------------------------------------------------------

MEDICINES: dict[str, dict] = {
    "aspirin": {
        "category": "NSAID / Antiplatelet",
        "uses": "Pain relief, fever reduction, blood clot prevention",
        "common_side_effects": ["stomach irritation", "bleeding risk", "nausea"],
    },
    "ibuprofen": {
        "category": "NSAID",
        "uses": "Pain, inflammation, fever",
        "common_side_effects": ["stomach upset", "dizziness", "kidney strain"],
    },
    "paracetamol": {
        "category": "Analgesic / Antipyretic",
        "uses": "Pain relief, fever reduction",
        "common_side_effects": ["liver damage (overdose)", "nausea", "rash"],
    },
    "acetaminophen": {
        "category": "Analgesic / Antipyretic",
        "uses": "Pain relief, fever reduction",
        "common_side_effects": ["liver damage (overdose)", "nausea", "rash"],
    },
    "amoxicillin": {
        "category": "Antibiotic (Penicillin)",
        "uses": "Bacterial infections",
        "common_side_effects": ["diarrhea", "nausea", "rash", "allergic reaction"],
    },
    "azithromycin": {
        "category": "Antibiotic (Macrolide)",
        "uses": "Bacterial infections, respiratory tract",
        "common_side_effects": ["nausea", "diarrhea", "abdominal pain"],
    },
    "ciprofloxacin": {
        "category": "Antibiotic (Fluoroquinolone)",
        "uses": "Urinary tract and respiratory infections",
        "common_side_effects": ["nausea", "diarrhea", "tendon damage risk"],
    },
    "metformin": {
        "category": "Antidiabetic (Biguanide)",
        "uses": "Type 2 diabetes",
        "common_side_effects": ["nausea", "diarrhea", "lactic acidosis (rare)"],
    },
    "insulin": {
        "category": "Antidiabetic (Hormone)",
        "uses": "Diabetes (Type 1 & 2)",
        "common_side_effects": ["hypoglycemia", "weight gain", "injection site reaction"],
    },
    "lisinopril": {
        "category": "ACE Inhibitor",
        "uses": "Hypertension, heart failure",
        "common_side_effects": ["dry cough", "dizziness", "hyperkalemia"],
    },
    "enalapril": {
        "category": "ACE Inhibitor",
        "uses": "Hypertension, heart failure",
        "common_side_effects": ["dry cough", "dizziness", "fatigue"],
    },
    "amlodipine": {
        "category": "Calcium Channel Blocker",
        "uses": "Hypertension, angina",
        "common_side_effects": ["swelling (edema)", "dizziness", "flushing"],
    },
    "atenolol": {
        "category": "Beta Blocker",
        "uses": "Hypertension, angina, arrhythmia",
        "common_side_effects": ["fatigue", "cold extremities", "bradycardia"],
    },
    "metoprolol": {
        "category": "Beta Blocker",
        "uses": "Hypertension, angina, heart failure",
        "common_side_effects": ["fatigue", "dizziness", "bradycardia"],
    },
    "losartan": {
        "category": "ARB (Angiotensin II Receptor Blocker)",
        "uses": "Hypertension, diabetic nephropathy",
        "common_side_effects": ["dizziness", "hyperkalemia", "fatigue"],
    },
    "warfarin": {
        "category": "Anticoagulant",
        "uses": "Blood clot prevention",
        "common_side_effects": ["bleeding", "bruising", "hair loss"],
    },
    "heparin": {
        "category": "Anticoagulant",
        "uses": "Blood clot prevention and treatment",
        "common_side_effects": ["bleeding", "thrombocytopenia", "osteoporosis (long-term)"],
    },
    "clopidogrel": {
        "category": "Antiplatelet",
        "uses": "Prevent blood clots (heart attack / stroke)",
        "common_side_effects": ["bleeding", "bruising", "stomach pain"],
    },
    "omeprazole": {
        "category": "Proton Pump Inhibitor",
        "uses": "GERD, stomach ulcers",
        "common_side_effects": ["headache", "nausea", "vitamin B12 deficiency (long-term)"],
    },
    "pantoprazole": {
        "category": "Proton Pump Inhibitor",
        "uses": "GERD, stomach ulcers",
        "common_side_effects": ["headache", "diarrhea", "abdominal pain"],
    },
    "ranitidine": {
        "category": "H2 Blocker",
        "uses": "Acid reflux, peptic ulcers",
        "common_side_effects": ["headache", "dizziness", "constipation"],
    },
    "cetirizine": {
        "category": "Antihistamine",
        "uses": "Allergies, hay fever, urticaria",
        "common_side_effects": ["drowsiness", "dry mouth", "fatigue"],
    },
    "loratadine": {
        "category": "Antihistamine",
        "uses": "Allergies, hay fever",
        "common_side_effects": ["headache", "dry mouth", "fatigue"],
    },
    "diphenhydramine": {
        "category": "Antihistamine (1st gen)",
        "uses": "Allergies, sleep aid, motion sickness",
        "common_side_effects": ["drowsiness", "dry mouth", "urinary retention"],
    },
    "prednisone": {
        "category": "Corticosteroid",
        "uses": "Inflammation, autoimmune conditions, allergies",
        "common_side_effects": ["weight gain", "mood changes", "increased blood sugar"],
    },
    "dexamethasone": {
        "category": "Corticosteroid",
        "uses": "Severe inflammation, allergic reactions",
        "common_side_effects": ["insomnia", "increased appetite", "mood swings"],
    },
    "hydrochlorothiazide": {
        "category": "Diuretic (Thiazide)",
        "uses": "Hypertension, edema",
        "common_side_effects": ["electrolyte imbalance", "dizziness", "increased urination"],
    },
    "furosemide": {
        "category": "Loop Diuretic",
        "uses": "Edema, heart failure, hypertension",
        "common_side_effects": ["dehydration", "electrolyte loss", "dizziness"],
    },
    "spironolactone": {
        "category": "Potassium-Sparing Diuretic",
        "uses": "Heart failure, hypertension, edema",
        "common_side_effects": ["hyperkalemia", "dizziness", "gynecomastia"],
    },
    "simvastatin": {
        "category": "Statin",
        "uses": "High cholesterol",
        "common_side_effects": ["muscle pain", "liver enzyme changes", "headache"],
    },
    "atorvastatin": {
        "category": "Statin",
        "uses": "High cholesterol, cardiovascular prevention",
        "common_side_effects": ["muscle pain", "liver issues", "digestive problems"],
    },
    "rosuvastatin": {
        "category": "Statin",
        "uses": "High cholesterol",
        "common_side_effects": ["muscle pain", "headache", "nausea"],
    },
    "sertraline": {
        "category": "SSRI (Antidepressant)",
        "uses": "Depression, anxiety, OCD, PTSD",
        "common_side_effects": ["nausea", "insomnia", "sexual dysfunction"],
    },
    "fluoxetine": {
        "category": "SSRI (Antidepressant)",
        "uses": "Depression, anxiety, OCD",
        "common_side_effects": ["nausea", "headache", "insomnia"],
    },
    "escitalopram": {
        "category": "SSRI (Antidepressant)",
        "uses": "Depression, generalized anxiety",
        "common_side_effects": ["nausea", "insomnia", "fatigue"],
    },
    "diazepam": {
        "category": "Benzodiazepine",
        "uses": "Anxiety, muscle spasm, seizures",
        "common_side_effects": ["drowsiness", "dependence", "memory impairment"],
    },
    "alprazolam": {
        "category": "Benzodiazepine",
        "uses": "Anxiety, panic disorder",
        "common_side_effects": ["drowsiness", "dependence", "dizziness"],
    },
    "tramadol": {
        "category": "Opioid Analgesic",
        "uses": "Moderate to severe pain",
        "common_side_effects": ["nausea", "dizziness", "constipation", "dependence risk"],
    },
    "morphine": {
        "category": "Opioid Analgesic",
        "uses": "Severe pain",
        "common_side_effects": ["constipation", "respiratory depression", "dependence"],
    },
    "codeine": {
        "category": "Opioid Analgesic",
        "uses": "Mild-moderate pain, cough suppression",
        "common_side_effects": ["constipation", "drowsiness", "nausea"],
    },
    "gabapentin": {
        "category": "Anticonvulsant / Neuropathic Pain",
        "uses": "Epilepsy, nerve pain",
        "common_side_effects": ["drowsiness", "dizziness", "weight gain"],
    },
    "pregabalin": {
        "category": "Anticonvulsant / Neuropathic Pain",
        "uses": "Nerve pain, fibromyalgia, epilepsy",
        "common_side_effects": ["dizziness", "drowsiness", "weight gain"],
    },
    "levothyroxine": {
        "category": "Thyroid Hormone",
        "uses": "Hypothyroidism",
        "common_side_effects": ["weight changes", "anxiety", "palpitations (if overdosed)"],
    },
    "salbutamol": {
        "category": "Bronchodilator (Beta-2 Agonist)",
        "uses": "Asthma, COPD",
        "common_side_effects": ["tremor", "palpitations", "headache"],
    },
    "montelukast": {
        "category": "Leukotriene Receptor Antagonist",
        "uses": "Asthma, allergic rhinitis",
        "common_side_effects": ["headache", "abdominal pain", "mood changes"],
    },
    "methotrexate": {
        "category": "Immunosuppressant / DMARD",
        "uses": "Rheumatoid arthritis, psoriasis, cancer",
        "common_side_effects": ["nausea", "liver toxicity", "immunosuppression"],
    },
    "naproxen": {
        "category": "NSAID",
        "uses": "Pain, inflammation, arthritis",
        "common_side_effects": ["stomach irritation", "headache", "dizziness"],
    },
    "diclofenac": {
        "category": "NSAID",
        "uses": "Pain, inflammation",
        "common_side_effects": ["stomach pain", "nausea", "cardiovascular risk"],
    },
    "cephalexin": {
        "category": "Antibiotic (Cephalosporin)",
        "uses": "Bacterial infections",
        "common_side_effects": ["diarrhea", "nausea", "rash"],
    },
    "doxycycline": {
        "category": "Antibiotic (Tetracycline)",
        "uses": "Bacterial infections, acne, malaria prophylaxis",
        "common_side_effects": ["photosensitivity", "nausea", "esophageal irritation"],
    },
    "clindamycin": {
        "category": "Antibiotic (Lincosamide)",
        "uses": "Serious bacterial infections",
        "common_side_effects": ["diarrhea", "C. difficile risk", "nausea"],
    },
}

# ---------------------------------------------------------------------------
# Drug-drug interactions  (keyed by frozenset for order-independent lookup)
# ---------------------------------------------------------------------------

_INTERACTION_LIST: list[dict] = [
    # ── Dangerous ─────────────────────────────────────────────
    {"drugs": ("aspirin", "warfarin"), "severity": "Dangerous",
     "reason": "Both thin the blood; combined use significantly increases risk of serious bleeding."},
    {"drugs": ("ibuprofen", "warfarin"), "severity": "Dangerous",
     "reason": "NSAIDs increase anticoagulant effect and bleeding risk with warfarin."},
    {"drugs": ("aspirin", "heparin"), "severity": "Dangerous",
     "reason": "Dual antiplatelet + anticoagulant greatly raises hemorrhage risk."},
    {"drugs": ("warfarin", "heparin"), "severity": "Dangerous",
     "reason": "Two anticoagulants together cause excessive bleeding risk."},
    {"drugs": ("clopidogrel", "warfarin"), "severity": "Dangerous",
     "reason": "Combined antiplatelet and anticoagulant therapy increases bleeding risk."},
    {"drugs": ("methotrexate", "ibuprofen"), "severity": "Dangerous",
     "reason": "NSAIDs reduce renal clearance of methotrexate, causing toxic accumulation."},
    {"drugs": ("methotrexate", "naproxen"), "severity": "Dangerous",
     "reason": "NSAIDs can increase methotrexate levels to toxic range."},
    {"drugs": ("sertraline", "tramadol"), "severity": "Dangerous",
     "reason": "Risk of serotonin syndrome — a potentially life-threatening condition."},
    {"drugs": ("fluoxetine", "tramadol"), "severity": "Dangerous",
     "reason": "Both raise serotonin levels; combined use risks serotonin syndrome."},
    {"drugs": ("diazepam", "morphine"), "severity": "Dangerous",
     "reason": "Benzodiazepine + opioid combination can cause fatal respiratory depression."},
    {"drugs": ("alprazolam", "morphine"), "severity": "Dangerous",
     "reason": "Combined CNS depression may lead to respiratory failure."},
    {"drugs": ("alprazolam", "codeine"), "severity": "Dangerous",
     "reason": "Benzodiazepine + opioid increases risk of extreme sedation and respiratory depression."},
    {"drugs": ("lisinopril", "spironolactone"), "severity": "Dangerous",
     "reason": "Both raise potassium; combined use risks dangerous hyperkalemia."},
    {"drugs": ("enalapril", "spironolactone"), "severity": "Dangerous",
     "reason": "ACE inhibitor + potassium-sparing diuretic can cause severe hyperkalemia."},
    {"drugs": ("lisinopril", "losartan"), "severity": "Dangerous",
     "reason": "Dual RAAS blockade increases risk of hypotension, hyperkalemia, and renal failure."},

    # ── Caution ───────────────────────────────────────────────
    {"drugs": ("aspirin", "ibuprofen"), "severity": "Caution",
     "reason": "Both are NSAIDs; combined use increases stomach ulcer and bleeding risk."},
    {"drugs": ("aspirin", "naproxen"), "severity": "Caution",
     "reason": "Two NSAIDs together raise GI bleeding risk; naproxen may also reduce aspirin's cardioprotective effect."},
    {"drugs": ("ibuprofen", "naproxen"), "severity": "Caution",
     "reason": "Taking two NSAIDs together increases gastrointestinal and renal risks."},
    {"drugs": ("aspirin", "clopidogrel"), "severity": "Caution",
     "reason": "Dual antiplatelet therapy: effective post-stent but raises bleeding risk. Use only under medical supervision."},
    {"drugs": ("metformin", "insulin"), "severity": "Caution",
     "reason": "Combined use may cause hypoglycemia; blood glucose must be monitored carefully."},
    {"drugs": ("lisinopril", "metformin"), "severity": "Caution",
     "reason": "ACE inhibitors may enhance hypoglycemic effect of metformin."},
    {"drugs": ("prednisone", "metformin"), "severity": "Caution",
     "reason": "Corticosteroids raise blood sugar, counteracting metformin's effect."},
    {"drugs": ("prednisone", "insulin"), "severity": "Caution",
     "reason": "Corticosteroids increase blood glucose; insulin dose may need adjustment."},
    {"drugs": ("prednisone", "ibuprofen"), "severity": "Caution",
     "reason": "Both increase GI bleeding risk; use together with caution."},
    {"drugs": ("prednisone", "aspirin"), "severity": "Caution",
     "reason": "Increased risk of GI ulceration and bleeding."},
    {"drugs": ("omeprazole", "clopidogrel"), "severity": "Caution",
     "reason": "Omeprazole may reduce clopidogrel activation, decreasing its antiplatelet effect."},
    {"drugs": ("ciprofloxacin", "dexamethasone"), "severity": "Caution",
     "reason": "Fluoroquinolones + corticosteroids increase tendon rupture risk."},
    {"drugs": ("simvastatin", "amlodipine"), "severity": "Caution",
     "reason": "Amlodipine increases simvastatin levels; higher statin doses raise muscle damage risk."},
    {"drugs": ("atorvastatin", "amlodipine"), "severity": "Caution",
     "reason": "Amlodipine can modestly increase atorvastatin exposure."},
    {"drugs": ("gabapentin", "morphine"), "severity": "Caution",
     "reason": "Combined CNS depression may increase sedation and respiratory risk."},
    {"drugs": ("pregabalin", "tramadol"), "severity": "Caution",
     "reason": "Additive CNS depression; risk of excessive sedation."},
    {"drugs": ("cetirizine", "diazepam"), "severity": "Caution",
     "reason": "Both cause drowsiness; combination may impair alertness significantly."},
    {"drugs": ("diphenhydramine", "diazepam"), "severity": "Caution",
     "reason": "Additive sedation from two CNS depressants."},
    {"drugs": ("diphenhydramine", "tramadol"), "severity": "Caution",
     "reason": "Increased sedation and possible serotonin interaction."},
    {"drugs": ("furosemide", "lisinopril"), "severity": "Caution",
     "reason": "Diuretic + ACE inhibitor may cause excessive blood pressure drop or renal impairment."},
    {"drugs": ("hydrochlorothiazide", "lisinopril"), "severity": "Caution",
     "reason": "Commonly co-prescribed but requires monitoring for hypotension and electrolyte changes."},
    {"drugs": ("levothyroxine", "omeprazole"), "severity": "Caution",
     "reason": "PPIs can reduce levothyroxine absorption; take at different times."},
    {"drugs": ("doxycycline", "paracetamol"), "severity": "Caution",
     "reason": "Generally safe, but both are hepatically metabolized; monitor in liver disease."},

    # ── Safe (notable but low-risk) ───────────────────────────
    {"drugs": ("paracetamol", "amoxicillin"), "severity": "Safe",
     "reason": "No significant interaction; commonly used together for infections with fever/pain."},
    {"drugs": ("omeprazole", "amoxicillin"), "severity": "Safe",
     "reason": "Used together in H. pylori triple therapy; well-established safe combination."},
    {"drugs": ("cetirizine", "paracetamol"), "severity": "Safe",
     "reason": "No known interaction; often used together for cold/allergy with pain."},
    {"drugs": ("salbutamol", "montelukast"), "severity": "Safe",
     "reason": "Complementary asthma therapies; safe and commonly co-prescribed."},
    {"drugs": ("amlodipine", "atorvastatin"), "severity": "Safe",
     "reason": "Available as a fixed-dose combination (Caduet); generally safe together."},
    {"drugs": ("metformin", "atorvastatin"), "severity": "Safe",
     "reason": "Commonly co-prescribed for diabetes + cholesterol; no significant interaction."},
    {"drugs": ("losartan", "amlodipine"), "severity": "Safe",
     "reason": "Two antihypertensives from different classes; safe and effective combination."},
    {"drugs": ("loratadine", "paracetamol"), "severity": "Safe",
     "reason": "No interaction; commonly paired for allergy relief with pain/fever."},
]

# Build a fast lookup dict keyed by frozenset of drug names
INTERACTIONS: dict[frozenset, dict] = {
    frozenset(item["drugs"]): item for item in _INTERACTION_LIST
}

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

_MEDICINE_NAMES = list(MEDICINES.keys())


def find_medicine(name: str, score_cutoff: int = 60) -> str | None:
    """Return the best fuzzy-matched medicine name, or None if no match."""
    name = name.strip().lower()
    if name in MEDICINES:
        return name
    result = process.extractOne(name, _MEDICINE_NAMES, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
    return result[0] if result else None


def check_interaction(drug_a: str, drug_b: str) -> dict | None:
    """Look up interaction between two drug names (case-insensitive).

    Returns a dict with keys: drugs, severity, reason — or None if unknown.
    """
    key = frozenset([drug_a.lower(), drug_b.lower()])
    return INTERACTIONS.get(key)


def get_all_interactions(drug_list: list[str]) -> list[dict]:
    """Check all pairwise interactions for a list of drug names.

    Returns a list of dicts, each containing: drug_a, drug_b, severity, reason.
    """
    results = []
    cleaned = [d.lower().strip() for d in drug_list if d.strip()]
    for i in range(len(cleaned)):
        for j in range(i + 1, len(cleaned)):
            info = check_interaction(cleaned[i], cleaned[j])
            if info:
                results.append({
                    "drug_a": cleaned[i].title(),
                    "drug_b": cleaned[j].title(),
                    "severity": info["severity"],
                    "reason": info["reason"],
                })
    return results
