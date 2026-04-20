import pdfplumber
from docx import Document
import os
import re

def extract_text_from_pdf(file_path):
    """Extract text from PDF file using pdfplumber"""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file using python-docx"""
    text = ""
    try:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""
    return text

def clean_text(text):
    """Clean and normalize extracted text"""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\-\@\(\)]', '', text)
    return text.strip()

def extract_text_from_file(file_path):
    """Main function to extract text from PDF or DOCX files"""
    if not os.path.exists(file_path):
        return ""
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        text = extract_text_from_docx(file_path)
    else:
        return ""
    
    return clean_text(text)