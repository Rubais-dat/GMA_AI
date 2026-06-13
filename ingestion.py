import os
import re
import fitz           # PyMuPDF
import pytesseract
from PIL import Image

# ── Tesseract path ────────────────────────────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ── Config ────────────────────────────────────────────────────────────────────
PDF_PATH         = "documents/KERALA_COLLEGES.pdf"
CLEANED_FILE     = "data/gma_cleaned.txt"
PROGRESS_FILE    = "data/gma_ocr_progress.txt"   # saves progress so restart is safe
OCR_DPI          = 200                            # higher = better quality, slower
TESSERACT_CONFIG = "--oem 3 --psm 6"             # best accuracy mode


def clean_text(text: str) -> str:
    """Remove junk characters and normalise whitespace."""
    if not text:
        return ""
    for ch in ["\u200b", "\u200c", "\u200d", "\ufeff"]:
        text = text.replace(ch, "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_page_text(page) -> str:
    """
    Try direct text extraction first (fast).
    Fall back to OCR if the page has no selectable text.
    """
    direct = page.get_text().strip()
    if direct:
        return clean_text(direct)

    # Render page as image and run OCR
    mat  = fitz.Matrix(OCR_DPI / 72, OCR_DPI / 72)   # scale to target DPI
    pix  = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img  = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    ocr_text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
    return clean_text(ocr_text)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(CLEANED_FILE), exist_ok=True)

    if not os.path.exists(PDF_PATH):
        print(f"ERROR: PDF not found at {PDF_PATH}")
        exit(1)

    doc        = fitz.open(PDF_PATH)
    total      = len(doc)
    print(f"PDF loaded — {total} pages. Starting extraction (OCR on image pages)...")

    # Load already-processed pages if a previous run was interrupted
    start_page = 0
    all_text   = ""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as pf:
            lines = pf.read().splitlines()
        if lines:
            start_page = int(lines[0])          # first line = last completed page index
        if os.path.exists(CLEANED_FILE):
            with open(CLEANED_FILE, "r", encoding="utf-8") as cf:
                all_text = cf.read()
        print(f"Resuming from page {start_page + 1} (previous run saved {start_page} pages).")

    # Process each page
    for p_idx in range(start_page, total):
        page_num = p_idx + 1
        try:
            text = extract_page_text(doc[p_idx])
        except Exception as e:
            print(f"  [Page {page_num}] ERROR: {e} — skipping.")
            text = ""

        if text:
            all_text += f"\n\n--- Page {page_num} ---\n{text}\n"

        # Progress report every 10 pages
        if page_num % 10 == 0 or page_num == total:
            print(f"  [{page_num}/{total}] processed — total chars so far: {len(all_text):,}")

        # Save progress every 20 pages so a crash doesn't lose everything
        if page_num % 20 == 0 or page_num == total:
            with open(CLEANED_FILE, "w", encoding="utf-8") as cf:
                cf.write(all_text)
            with open(PROGRESS_FILE, "w", encoding="utf-8") as pf:
                pf.write(str(page_num))

    # Final save & cleanup
    with open(CLEANED_FILE, "w", encoding="utf-8") as cf:
        cf.write(all_text)
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

    print(f"\n✅ Done! All {total} pages processed.")
    print(f"   Saved to : {CLEANED_FILE}")
    print(f"   Total    : {len(all_text):,} characters")
