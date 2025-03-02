import base64
import re
import io
import pdfplumber

def smart_section_split(text):
    """Splits paragraphs using sentence-ending punctuation and line breaks."""
    return re.split(r'(?<=[.;_])\s*\n', text)  # Split at periods followed by newlines

def pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")
    
def extract_paragraphs_from_base64(pdf_base64):
    text = ""
    page_num = 1
    section_num = 1
    html_contents = []
    html_content = ""
    matching_content = []
    not_matching_content = []
    response = {}
    pdf_bytes = base64.b64decode(pdf_base64)
    bytes = io.BytesIO()
    bytes.write(pdf_bytes)
    neutral_explain = "This clause is standard and does not pose a risk"
    neutral_text = "Neutral"
    index1 = 0
    with pdfplumber.open(bytes) as pdf:
        for page in pdf.pages:
            text = page.extract_text() + "\n"  # Extract text from each page
            sections = smart_section_split(text=text)
            for section in sections:
                print("************* section ***************** ",section)


pdf_file = "11FormatofBankGuaranteeWithAmount4.pdf"  # Replace with your PDF file path
b64 = pdf_to_base64(pdf_file)
extract_paragraphs_from_base64(b64)
  