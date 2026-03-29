import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from docx import Document
import os

class DataExtractor:
    def __init__(self):
        # Configurăm Tesseract pentru limba română și engleză
        self.tess_config = r'--oem 3 --psm 6 -l ron+eng'

    def extract_from_pdf(self, file_path):
        """Extrage text din PDF (atât text nativ, cât și imagini prin OCR dacă e cazul)."""
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                # Încercăm întâi textul nativ
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text + "\n"
                else:
                    # Dacă pagina e goală (e o imagine scanată), folosim OCR
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text += pytesseract.image_to_string(img, config=self.tess_config) + "\n"
            doc.close()
        except Exception as e:
            print(f"Eroare PDF {file_path}: {e}")
        return text

    def extract_from_docx(self, file_path):
        """Extrage text din fișiere Word."""
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Eroare Word {file_path}: {e}")
            return ""

    def extract_from_image(self, file_path):
        """Extrage text din imagini (JPG, PNG)."""
        try:
            return pytesseract.image_to_string(Image.open(file_path), config=self.tess_config)
        except Exception as e:
            print(f"Eroare Imagine {file_path}: {e}")
            return ""

    def process_file(self, file_path):
        """Detectează extensia și alege metoda corectă."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self.extract_from_docx(file_path)
        elif ext in ['.jpg', '.jpeg', '.png']:
            return self.extract_from_image(file_path)
        return ""