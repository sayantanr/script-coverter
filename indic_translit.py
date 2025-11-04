# Install dependencies
# In Colab use: !pip install streamlit indic-transliteration pytesseract pdf2image pillow
# And for OCR support: !apt-get install -y tesseract-ocr poppler-utils

import streamlit as st
from PIL import Image
import pytesseract
from io import BytesIO
from pdf2image import convert_from_bytes
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import re

st.set_page_config(page_title="Indic Transliteration + OCR", layout="wide")
st.title("🕉 Indic Script Transliterator with OCR (using indic-transliteration)")

st.markdown("""
Upload a **.txt**, **.pdf**, or **image** file.  
This app will:
1. Extract text using OCR if needed  
2. Autodetect the script (best-effort)  
3. Convert (transliterate) to your chosen Indic script(s)
""")

# -------------------------------------------------------------------
# STEP 1 — Upload file
uploaded_file = st.file_uploader("Upload a .txt, .pdf, or image file", type=["txt","pdf","png","jpg","jpeg"])

# -------------------------------------------------------------------
# Helper: Detect script based on Unicode range
SCRIPT_RANGES = [
    ("Devanagari", (0x0900, 0x097F)),
    ("Bengali", (0x0980, 0x09FF)),
    ("Gurmukhi", (0x0A00, 0x0A7F)),
    ("Gujarati", (0x0A80, 0x0AFF)),
    ("Oriya", (0x0B00, 0x0B7F)),
    ("Tamil", (0x0B80, 0x0BFF)),
    ("Telugu", (0x0C00, 0x0C7F)),
    ("Kannada", (0x0C80, 0x0CFF)),
    ("Malayalam", (0x0D00, 0x0D7F)),
    ("Latin", (0x0041, 0x007A)),
]

def detect_script(text):
    counts = {}
    for ch in text:
        cp = ord(ch)
        for name, (lo, hi) in SCRIPT_RANGES:
            if lo <= cp <= hi:
                counts[name] = counts.get(name, 0) + 1
    if not counts:
        return "Unknown"
    return max(counts, key=counts.get)

# -------------------------------------------------------------------
# Helper: OCR for images and PDFs
def ocr_image(image, lang='eng'):
    return pytesseract.image_to_string(image, lang=lang)

def ocr_pdf(pdf_bytes, lang='eng'):
    images = convert_from_bytes(pdf_bytes)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang=lang) + "\n"
    return text

# -------------------------------------------------------------------
# STEP 2 — Process input
if uploaded_file:
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8").strip()
    elif file_name.endswith(".pdf"):
        st.info("📄 Performing OCR on PDF (this may take a while)...")
        text = ocr_pdf(uploaded_file.read())
    else:
        st.info("🖼 Performing OCR on image...")
        image = Image.open(BytesIO(uploaded_file.read()))
        st.image(image, caption="Uploaded image", use_column_width=True)
        text = ocr_image(image)
    
    if not text.strip():
        st.warning("No readable text found.")
    else:
        st.subheader("📜 Extracted Text (first 1000 chars):")
        st.code(text[:1000])

        detected = detect_script(text)
        st.write(f"🧭 Detected Script: **{detected}**")

        # -------------------------------------------------------------------
        # STEP 3 — Transliteration options
        st.subheader("🔤 Choose Target Script(s)")
        targets = st.multiselect(
            "Select target scripts",
            options=[
                "DEVANAGARI", "BENGALI", "GUJARATI", "ORIYA",
                "TAMIL", "TELUGU", "KANNADA", "MALAYALAM", "IAST", "ITRANS"
            ],
            default=["DEVANAGARI", "BENGALI"]
        )

        st.subheader("⚙️ Select Input Scheme")
        source_scheme = st.selectbox(
            "Input transliteration scheme (choose based on your text style)",
            ["ITRANS", "IAST", "HK", "SLP1", "VELTHUIS", "DEVANAGARI", "BENGALI", "GUJARATI", "TAMIL"]
        )

        if st.button("🔁 Transliterate"):
            for tgt in targets:
                try:
                    output = transliterate(text, getattr(sanscript, source_scheme), getattr(sanscript, tgt))
                    st.markdown(f"### 🈴 Output → {tgt}")
                    st.text_area(f"{tgt}_output", output[:2000], height=200)
                    st.download_button(
                        f"⬇ Download {tgt}.txt",
                        output,
                        file_name=f"{uploaded_file.name}_{tgt}.txt"
                    )
                except Exception as e:
                    st.error(f"Error converting to {tgt}: {e}")
