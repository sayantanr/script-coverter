# Install the required library
!pip install indic-transliteration

# ---- Step 1: Upload input file ----
from google.colab import files
uploaded = files.upload()   # Choose your 'input.txt' or any Roman text file

# ---- Step 2: Read the uploaded file ----
filename = list(uploaded.keys())[0]
with open(filename, 'r', encoding='utf-8') as f:
    roman_text = f.read().strip()

# ---- Step 3: Transliterate ----
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

devnagri_text = transliterate(roman_text, sanscript.ITRANS, sanscript.DEVANAGARI)
bengali_text  = transliterate(roman_text, sanscript.ITRANS, sanscript.BENGALI)

# ---- Step 4: Save outputs ----
with open("devnagri_output.txt", "w", encoding="utf-8") as f:
    f.write(devnagri_text)

with open("bengali_output.txt", "w", encoding="utf-8") as f:
    f.write(bengali_text)

# ---- Step 5: Download the result files ----
files.download("devnagri_output.txt")
files.download("bengali_output.txt")

print("✅ Done! Files are ready for download.")

