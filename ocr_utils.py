"""
ocr_utils.py — Tesseract OCR wrapper for prescription image parsing.

Provides:
  - extract_text_from_image(image): Run Tesseract OCR on a PIL Image.
"""

import platform
from pathlib import Path

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

# ---------------------------------------------------------------------------
# Tesseract executable path configuration
# ---------------------------------------------------------------------------
# Update this path if Tesseract is installed in a non-default location.

if platform.system() == "Windows":
    _default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if Path(_default).exists():
        pytesseract.pytesseract.tesseract_cmd = _default

# On macOS / Linux the binary is usually on PATH — no override needed.


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def preprocess_image(image: Image.Image) -> Image.Image:
    """Apply light preprocessing to improve OCR accuracy."""
    # Convert to grayscale
    img = image.convert("L")
    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    return img


def extract_text_from_image(image: Image.Image) -> str:
    """Extract text from a PIL Image using Tesseract OCR.

    The image is preprocessed (grayscale + contrast boost + sharpen) before
    being passed to Tesseract for best results on prescription images.

    Parameters
    ----------
    image : PIL.Image.Image
        The prescription image to parse.

    Returns
    -------
    str
        Extracted text, or an error message if OCR fails.
    """
    try:
        processed = preprocess_image(image)
        text = pytesseract.image_to_string(processed, lang="eng")
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        return (
            "[ERROR] Tesseract OCR is not installed or not found.\n"
            "Please install Tesseract and update the path in ocr_utils.py.\n"
            "See README.md for installation instructions."
        )
    except Exception as e:
        return f"[ERROR] OCR processing failed: {e}"
