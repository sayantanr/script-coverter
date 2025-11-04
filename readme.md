# Python packages
pip install streamlit pytesseract pdf2image pillow aksharamukha langdetect

# On Debian/Ubuntu (in Colab you might need these):
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils

# Install specific tesseract language packs if needed, e.g. Bengali, Hindi:
# (Debian package names differ by distro; examples:)
sudo apt-get install -y tesseract-ocr-ben tesseract-ocr-hin tesseract-ocr-beng


!pip install streamlit indic-transliteration pytesseract pdf2image pillow
!apt-get install -y tesseract-ocr poppler-utils
run streamlit in google colab 

!streamlit run app.py --server.port 6006 & npx localtunnel --port 6006

✅ Features Recap

✔ Accepts .txt, .pdf, or .png/.jpg
✔ OCR using Tesseract
✔ Auto-detects input script (Indic family only)
✔ Choose input transliteration scheme manually (ITRANS, IAST, HK, etc.)
✔ Converts to multiple output scripts
✔ One-click .txt download for each output


