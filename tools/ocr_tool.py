import os
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import io

# Configure tesseract path for Windows (adjust if needed)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyPDF2 first, then OCR if needed"""
    text = ""
    
    try:
        # Try text extraction first (for text-based PDFs)
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # If no text extracted, it might be a scanned PDF - use OCR
        if not text.strip():
            print(f"    No text found in PDF, attempting OCR on {os.path.basename(file_path)}...", flush=True)
            text = extract_text_from_pdf_ocr(file_path)
    except Exception as e:
        print(f"    Error extracting from PDF {file_path}: {e}", flush=True)
    
    return text


def extract_text_from_pdf_ocr(file_path):
    """Extract text from scanned PDF using OCR"""
    text = ""
    
    try:
        # Convert PDF pages to images
        images = convert_from_path(file_path, dpi=300)
        
        for i, image in enumerate(images):
            print(f"      OCR processing page {i+1}/{len(images)}...", flush=True)
            # Perform OCR on each page
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
    except Exception as e:
        print(f"    OCR error on {file_path}: {e}", flush=True)
    
    return text


def extract_text_from_image(file_path):
    """Extract text from image files using OCR"""
    text = ""
    
    try:
        print(f"    OCR processing image {os.path.basename(file_path)}...", flush=True)
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
    except Exception as e:
        print(f"    OCR error on {file_path}: {e}", flush=True)
    
    return text


def is_ocr_supported_file(file_path):
    """Check if file is supported for OCR processing"""
    ocr_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    return any(file_path.lower().endswith(ext) for ext in ocr_extensions)


def extract_text_with_ocr(file_path):
    """Main function to extract text from files using appropriate method"""
    if not os.path.exists(file_path):
        return ""
    
    file_lower = file_path.lower()
    
    if file_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_lower.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        return extract_text_from_image(file_path)
    else:
        return ""
