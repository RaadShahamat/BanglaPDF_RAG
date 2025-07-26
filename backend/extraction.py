import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
import re
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
# Convert PDF to image and extract OCR text (for paragraph)
def extract_ocr_text(pdf_path):
    images = convert_from_path(pdf_path)
    texts = []
    for img in images:
        text = pytesseract.image_to_string(img, lang='ben')
        texts.append(text)
    return texts


    # Extract raw text using PyMuPDF (better table structure)
def extract_pymupdf_texts(pdf_path):
    doc = fitz.open(pdf_path)
    return [page.get_text("text") for page in doc]


# Check if page has SL\nAns pattern (table present)
def contains_table_marker(text):
    return "SL\nAns" in text or "SL Ans" in text

# Extract only valid answer table from the last SL\nAns onward
def extract_table_section_from_text(pym_text):
    lines = pym_text.splitlines()

    # Track all indexes where "SL" and "Ans" occur consecutively
    sl_ans_indexes = []
    for i in range(len(lines) - 1):
        if lines[i].strip() == "SL" and lines[i+1].strip() == "Ans":
            sl_ans_indexes.append(i)

    if not sl_ans_indexes:
        return ""

    # Start scanning just after the last SL-Ans block
    start_index = sl_ans_indexes[-1] + 2
    table_lines = []
    i = start_index

    bangla_num_pattern = r'^[০-৯]{1,3}$'
    bangla_letter_pattern = r'^[ক-হড়ঢ়য়]$'

    while i < len(lines) - 1:
        num_line = lines[i].strip()
        letter_line = lines[i+1].strip()

        if re.match(bangla_num_pattern, num_line) and re.match(bangla_letter_pattern, letter_line):
            table_lines.append(num_line)
            table_lines.append(letter_line)
            i += 2
        else:
            break  # Stop if pattern breaks

    if table_lines:
        return "SL\nAns\n" + " ".join(table_lines)
    else:
        return ""


# Merge OCR + Table (only appending extracted table if present)
def hybrid_ocr_pymupdf(pdf_path):
    ocr_pages = extract_ocr_text(pdf_path)
    pym_pages = extract_pymupdf_texts(pdf_path)

    final_pages = []

    for i in range(len(ocr_pages)):
        ocr_text = ocr_pages[i]
        pym_text = pym_pages[i]

        print(f"📄 Processing Page {i+1}")
        combined_text = ocr_text.strip()

        if contains_table_marker(pym_text):
            table_section = extract_table_section_from_text(pym_text)
            if table_section:
                print(f"➕ Table detected and appended on Page {i+1}")
                combined_text += "\n" + table_section

        final_pages.append(combined_text)

    return final_pages
