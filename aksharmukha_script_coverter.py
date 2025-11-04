# app.py
import streamlit as st
from io import BytesIO
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from langdetect import detect
import re
import os

# Try to import Aksharamukha transliterator
try:
    from aksharamukha import transliterate as aksharamukha_transliterate
    AKSHARAMUKHA_AVAILABLE = True
except Exception as e:
    AKSHARAMUKHA_AVAILABLE = False

st.set_page_config(page_title="Multi-Script Transliterator + OCR", layout="wide")

st.title("Multi-Script Transliterator with OCR (Aksharamukha + Tesseract)")
st.markdown("""
Upload a text / image / PDF. The app will OCR (if needed), autodetect the input script, 
and transliterate into the target scripts you choose.
""")

# Large list of candidate scripts (from user's list) - many are recognized names in Aksharamukha
ALL_SCRIPTS = [
"Ahom","Arabic","Ariyaka","Assamese","Avestan","Balinese","Batak_Karo","Batak_Mandailing",
"Batak_Pakpak","Batak_Simalungun","Batak_Toba","Bengali","Bhaiksuki","Brahmi","Buginese",
"Buhid","Burmese","Chakma","Cham","Cyrillic","Devanagari","Dives_Akuru","Dogra","Elymaic",
"Ethiopic","Gondi_Gunjala","Gondi_Masaram","Grantha","Grantha_Pandya","Gujarati","Hanunoo",
"Hatran","Hebrew","Imperial_Aramaic","Inscriptional_Pahlavi","Inscriptional_Parthian",
"Hiragana","Katakana","Javanese","Kaithi","Kannada","Kawi","Khamti_Shan","Kharoshthi",
"Khmer","Khojki","Khom_Thai","Khudawadi","Lao","Lepcha","Limbu","Mahajani","Makasar",
"Malayalam","Manichaean","Marchen","Meetei_Mayek","Modi","Mon","Mongolian_Ali_Gali","Mro",
"Multani","Nabataean","Nandinagari","Newa","Old_North_Arabian","Old_Persian","Old_Sogdian",
"Old_South_Arabian","Oriya","Pallava","Palmyrene","Persian","PhagsPa","Phoenician",
"Psalter_Pahlavi","Punjabi","Ranjana","Rejang","Rohingya","Roman","Roman_DMG_Persian",
"Roman_Harvard-Kyoto","Roman_IAST","Roman_IPA_Indic","Roman_ISO_15919","Roman_ITRANS",
"Roman_SLP1","Roman_Semitic","Roman_Titus","Roman_Velthuis","Samaritan","Santali",
"Saurashtra","Shahmukhi","Shan","Sharada","Siddham","Sinhala","Sogdian","Sora_Sompeng",
"Soyombo","Sundanese","Syloti_Nagari","Syriac_Eastern","Syriac_Estrangela","Syriac_Western",
"Tagalog","Tagbanwa","Tai_Laing","Takri","Tamil","Tamil_Extended","Tamil_Brahmi","Telugu",
"Thaana","Thai","Tham_Lanna","Tibetan","Tirhuta","Ugaritic","Urdu","Vatteluttu","Wancho",
"Warang_Citi","Zanabazar_Square"
]

# Helper: minimal unicode-range script detection by sampling characters
# This is a best-effort script detector (not language detection)
SCRIPT_RANGES = [
    ("Latin", (0x0041, 0x007A)),
    ("Devanagari", (0x0900, 0x097F)),
    ("Bengali", (0x0980, 0x09FF)),
    ("Gurmukhi", (0x0A00, 0x0A7F)),
    ("Gujarati", (0x0A80, 0x0AFF)),
    ("Oriya", (0x0B00, 0x0B7F)),
    ("Tamil", (0x0B80, 0x0BFF)),
    ("Telugu", (0x0C00, 0x0C7F)),
    ("Kannada", (0x0C80, 0x0CFF)),
    ("Malayalam", (0x0D00, 0x0D7F)),
    ("Sinhala", (0x0D80, 0x0DFF)),
    ("Thai", (0x0E00, 0x0E7F)),
    ("Lao", (0x0E80, 0x0EFF)),
    ("Tibetan", (0x0F00, 0x0FFF)),
    ("Myanmar", (0x1000, 0x109F)),
    ("Georgian", (0x10A0, 0x10FF)),
    ("Hangul", (0xAC00, 0xD7AF)),
    ("Hebrew", (0x0590, 0x05FF)),
    ("Arabic", (0x0600, 0x06FF)),
    ("Cyrillic", (0x0400, 0x04FF)),
    ("Greek", (0x0370, 0x03FF))
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

# OCR helpers
def ocr_image(image: Image.Image, tesseract_lang=None):
    if tesseract_lang:
        return pytesseract.image_to_string(image, lang=tesseract_lang)
    else:
        return pytesseract.image_to_string(image)

def ocr_pdf_bytes(pdf_bytes, tesseract_lang=None):
    texts = []
    try:
        images = convert_from_bytes(pdf_bytes)
    except Exception as e:
        st.error(f"PDF to image convert error: {e}")
        return ""
    for img in images:
        texts.append(ocr_image(img, tesseract_lang))
    return "\n".join(texts)

# UI
uploaded_file = st.file_uploader("Upload a .txt / image / .pdf file", type=["txt","pdf","png","jpg","jpeg","tiff"])
tesseract_lang = st.text_input("Tesseract OCR language code (optional, e.g., hin, ben, eng)", value="")

if not AKSHARAMUKHA_AVAILABLE:
    st.error("Aksharamukha is not available. Please `pip install aksharamukha`. The app will still try OCR but transliteration will be disabled.")
    st.stop()

if uploaded_file:
    file_bytes = uploaded_file.read()
    file_type = uploaded_file.type
    input_text = ""
    if uploaded_file.name.lower().endswith(".txt"):
        try:
            input_text = file_bytes.decode("utf-8")
        except:
            input_text = file_bytes.decode("latin-1")
    elif file_type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
        st.info("Performing OCR on PDF...")
        input_text = ocr_pdf_bytes(file_bytes, tesseract_lang or None)
    else:
        # image
        try:
            image = Image.open(BytesIO(file_bytes)).convert("RGB")
            st.image(image, caption="Uploaded image", use_column_width=True)
            st.info("Performing OCR on image...")
            input_text = ocr_image(image, tesseract_lang or None)
        except Exception as e:
            st.error(f"Couldn't open image: {e}")

    if not input_text.strip():
        st.warning("No text detected from the input (or file empty).")
    else:
        st.subheader("Detected / Extracted text (first 1000 chars):")
        st.code(input_text[:1000])

        # Simple language detection for hint (may fail for short text)
        try:
            lang_hint = detect(input_text)
        except:
            lang_hint = "unknown"

        detected_script = detect_script(input_text)
        st.write(f"Detected script (best-effort): **{detected_script}** · Language hint: **{lang_hint}**")

        # Select outputs
        st.markdown("### Choose target scripts (multiple allowed):")
        targets = st.multiselect("Target scripts", options=ALL_SCRIPTS, default=["Devanagari","Bengali","Roman"])
        apply_button = st.button("Transliterate & Generate files")

        if apply_button:
            if not targets:
                st.warning("Pick at least one target script.")
            else:
                st.info("Transliterating... this may take a few seconds.")
                outputs = {}
                for tgt in targets:
                    # map some names to Aksharamukha names (best-effort mapping)
                    tgt_ak = tgt.replace(" ", "_")
                    # try converting using Aksharamukha API
                    try:
                        # Aksharamukha API: aksharamukha_transliterate.process(inputScript, outputScript, text)
                        # Best-effort: attempt to auto-detect source script name for Aksharamukha:
                        src_ak = None
                        # Use roman if input detected Latin
                        if detected_script == "Latin":
                            src_ak = "Roman"
                        elif detected_script == "Devanagari":
                            src_ak = "Devanagari"
                        elif detected_script == "Bengali":
                            src_ak = "Bengali"
                        elif detected_script == "Arabic":
                            src_ak = "Arabic"
                        elif detected_script == "Cyrillic":
                            src_ak = "Cyrillic"
                        elif detected_script == "Hebrew":
                            src_ak = "Hebrew"
                        else:
                            # fallback to "Devanagari" or "Roman"
                            src_ak = "Roman"

                        # Aksharamukha function call:
                        out_text = aksharamukha_transliterate.process(src_ak, tgt_ak, input_text)
                        outputs[tgt] = out_text
                    except Exception as e:
                        outputs[tgt] = f"[ERROR transliteration to {tgt}: {e}]"

                # Display results and provide downloads
                for name, txt in outputs.items():
                    st.markdown(f"**Output — {name}**")
                    st.text_area(f"preview_{name}", value=txt[:2000], height=200)
                    # create download button
                    b = txt.encode("utf-8")
                    st.download_button(label=f"Download {name}.txt", data=b, file_name=f"{uploaded_file.name}_{name}.txt", mime="text/plain")
                st.success("Done — files ready to download.")
