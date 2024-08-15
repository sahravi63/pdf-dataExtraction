from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

def extract_text_from_pdf(pdf_path, use_ocr=False, ocr_lang='eng'):
    text = ''
    reader = PdfReader(pdf_path)
    
    # Iterate through pages using an index for page numbers
    for i, page in enumerate(reader.pages):
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text
        elif use_ocr:
            # Convert the PDF page to an image and then apply OCR
            images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
            for image in images:
                text += pytesseract.image_to_string(image, lang=ocr_lang)
    
    return text
