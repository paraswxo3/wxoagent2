import pdfplumber
import re

def smart_section_split(text):
    """Splits paragraphs using sentence-ending punctuation and line breaks."""
    return re.split(r'(?<=\.)\s*\n', text)  # Split at periods followed by newlines

def pdf_to_text(pdf_path):
    text = ""
    sections = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()  # Extract text from each page
        sections = smart_section_split(text=text)
        print(sections)
    return sections

sections = pdf_to_text("./171120231905-CorrigendumFormatsWithAmount2.pdf")
# print(sections)
