"""
risk_engine.py — Rule-based emergency risk scoring engine.

Provides:
  - calculate_risk(heart_rate, systolic, diastolic, temperature, spo2)
      → dict with score, level, factors, action.
"""

# ---------------------------------------------------------------------------
# Clinical thresholds  (simplified for educational use)
# ---------------------------------------------------------------------------

def _hr_score(hr: float) -> tuple[float, str | None]:
    """Score heart rate (bpm). Normal: 60–100."""
    if hr < 40:
        return 30, "Very low heart rate (severe bradycardia)"
    if hr < 50:
        return 15, "Low heart rate (bradycardia)"
    if hr < 60:
        return 5, "Slightly low heart rate"
    if hr <= 100:
        return 0, None
    if hr <= 120:
        return 5, "Slightly elevated heart rate"
    if hr <= 150:
        return 15, "High heart rate (tachycardia)"
    return 30, "Very high heart rate (severe tachycardia)"


def _bp_systolic_score(sbp: float) -> tuple[float, str | None]:
    """Score systolic blood pressure (mmHg). Normal: 90–120."""
    if sbp < 70:
        return 30, "Critically low systolic BP (severe hypotension)"
    if sbp < 90:
        return 15, "Low systolic BP (hypotension)"
    if sbp <= 120:
        return 0, None
    if sbp <= 140:
        return 5, "Elevated systolic BP (pre-hypertension)"
    if sbp <= 180:
        return 15, "High systolic BP (hypertension)"
    return 30, "Critically high systolic BP (hypertensive crisis)"


def _bp_diastolic_score(dbp: float) -> tuple[float, str | None]:
    """Score diastolic blood pressure (mmHg). Normal: 60–80."""
    if dbp < 40:
        return 25, "Critically low diastolic BP"
    if dbp < 60:
        return 10, "Low diastolic BP"
    if dbp <= 80:
        return 0, None
    if dbp <= 90:
        return 5, "Elevated diastolic BP"
    if dbp <= 120:
        return 15, "High diastolic BP"
    return 25, "Critically high diastolic BP (hypertensive emergency)"


def _temp_score(temp_f: float) -> tuple[float, str | None]:
    """Score body temperature (°F). Normal: 97.0–99.5."""
    if temp_f < 95:
        return 25, "Hypothermia"
    if temp_f < 97:
        return 10, "Below-normal temperature"
    if temp_f <= 99.5:
        return 0, None
    if temp_f <= 101:
        return 5, "Low-grade fever"
    if temp_f <= 103:
        return 15, "Moderate fever"
    return 25, "High fever (hyperthermia)"


def _spo2_score(spo2: float) -> tuple[float, str | None]:
    """Score oxygen saturation (%). Normal: 95–100."""
    if spo2 >= 95:
        return 0, None
    if spo2 >= 90:
        return 10, "Mildly low oxygen saturation"
    if spo2 >= 85:
        return 20, "Low oxygen saturation (hypoxemia)"
    return 30, "Critically low oxygen saturation"


# ---------------------------------------------------------------------------
# Risk level mapping
# ---------------------------------------------------------------------------

def _level_from_score(score: int) -> tuple[str, str]:
    """Return (level_label, recommended_action) for a given score."""
    if score <= 25:
        return "Low", "No immediate action needed. Continue monitoring your health."
    if score <= 50:
        return "Moderate", "Schedule a visit with your healthcare provider soon."
    if score <= 75:
        return "High", "Seek medical attention promptly. Visit urgent care or your doctor today."
    return "Critical", "Seek immediate emergency care. Call emergency services or go to the nearest ER."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_risk(
    heart_rate: float,
    systolic: float,
    diastolic: float,
    temperature: float,
    spo2: float,
) -> dict:
    """Calculate an emergency risk score from vital signs.

    Parameters
    ----------
    heart_rate : float   — beats per minute
    systolic   : float   — systolic blood pressure (mmHg)
    diastolic  : float   — diastolic blood pressure (mmHg)
    temperature: float   — body temperature in °F
    spo2       : float   — oxygen saturation percentage

    Returns
    -------
    dict with keys:
        score   : int        (0–100, clamped)
        level   : str        ("Low" / "Moderate" / "High" / "Critical")
        factors : list[str]  (contributing risk factors)
        action  : str        (recommended action text)
    """
    total = 0.0
    factors: list[str] = []

    for fn, val in [
        (_hr_score, heart_rate),
        (_bp_systolic_score, systolic),
        (_bp_diastolic_score, diastolic),
        (_temp_score, temperature),
        (_spo2_score, spo2),
    ]:
        pts, desc = fn(val)
        total += pts
        if desc:
            factors.append(desc)

    score = int(min(max(total, 0), 100))
    level, action = _level_from_score(score)

    return {
        "score": score,
        "level": level,
        "factors": factors,
        "action": action,
    }
