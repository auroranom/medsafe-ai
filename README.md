# MedSafe AI

A patient-facing healthcare safety web application with 5 AI-assisted modules for medicine safety analysis, prescription parsing, symptom guidance, side-effect monitoring, and emergency risk prediction.

## Tech Stack

- **Python 3.10+**
- **Streamlit** — Multi-tab dashboard UI
- **pytesseract + Pillow** — OCR for prescription images
- **RapidFuzz** — Fuzzy string matching for medicine names
- **Ollama + LLaMA 3** — Local LLM for AI explanations, summarization, and extraction

## Setup Instructions

### 1. Create and activate a virtual environment

```bash
python -m venv medsafe_env

# Windows
medsafe_env\Scripts\activate

# macOS / Linux
source medsafe_env/bin/activate
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

- **Windows**: Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and install. Update the `TESSERACT_CMD` path in `ocr_utils.py` if your install location differs from the default.
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt install tesseract-ocr`

### 4. Install Ollama and pull LLaMA 3

```bash
# Install Ollama from https://ollama.com
ollama pull llama3
```

### 5. Run the app

```bash
streamlit run app.py
```

The app will open at [http://localhost:8501](http://localhost:8501).

## Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | Medicine Interaction Checker | Check drug-drug interactions with AI safety summaries |
| 2 | Prescription OCR + AI Parsing | Upload prescription images for automated parsing |
| 3 | Symptom & Doubt Solver | Get symptom guidance with home remedies and warning signs |
| 4 | Side-Effect Monitor | Log and analyze medication side effects over time |
| 5 | Emergency Risk Predictor | Vital sign-based risk scoring with AI explanations |

## Disclaimer

All AI outputs are **educational only** and are **not** medical diagnoses. Always consult a qualified healthcare professional for medical advice.
