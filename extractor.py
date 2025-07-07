import os
import fitz  # PyMuPDF for PDFs
from PIL import Image
import pytesseract

# Chunking function
def chunk_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap  # Move window with overlap
    return chunks

# Extractors for supported file types
def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_text_from_pdf(file_path):
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

# Generic extractor based on file type
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        return extract_text_from_txt(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        return extract_text_from_image(file_path)
    else:
        return None  # Unsupported files are skipped

# Folder-based extractor with chunking
def extract_text_from_folder(folder_path, recursive=True, chunk_size=300, overlap=50):
    dataset = []
    supported_files = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f'Found file: {file_path}')
            text = extract_text(file_path)
            if text:
                chunks = chunk_text(text, chunk_size, overlap)
                dataset.extend(chunks)
                supported_files += 1
                print(f'Extracted {len(chunks)} chunks from {file_path}')
            else:
                print(f'Skipped unsupported or empty file: {file_path}')
        if not recursive:
            break
    print(f'Total extracted chunks: {len(dataset)}')
    print(f'Total supported files processed: {supported_files}')
    return dataset
