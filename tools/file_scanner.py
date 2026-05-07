import os
from tools.ocr_tool import extract_text_with_ocr, is_ocr_supported_file


def scan_files(path):
    file_paths = []
    
    # Check if path is a file
    if os.path.isfile(path):
        return [path]
    
    # Otherwise treat as directory
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                file_paths.append(os.path.join(root, file))
    
    return file_paths


def read_file(file_path):
    """Read file content - uses OCR for PDFs and images, regular read for text files"""
    try:
        # Check if file needs OCR processing
        if is_ocr_supported_file(file_path):
            return extract_text_with_ocr(file_path)
        
        # Regular text file reading
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        # Try with different encoding if UTF-8 fails
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except:
            return ""
