# Python packages
pip install streamlit pytesseract pdf2image pillow aksharamukha langdetect

# On Debian/Ubuntu (in Colab you might need these):
sudo apt-get update
sudo apt-get install -y tesseract-ocr poppler-utils

# Install specific tesseract language packs if needed, e.g. Bengali, Hindi:
# (Debian package names differ by distro; examples:)
sudo apt-get install -y tesseract-ocr-ben tesseract-ocr-hin tesseract-ocr-beng

