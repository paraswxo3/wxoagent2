import pdfplumber
import re
import base64
import json
import io
from bg_elser_query import searchBG_elser

def pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")

def smart_section_split(text):
    """Splits paragraphs using sentence-ending punctuation and line breaks."""
    return re.split(r'(?<=\.)\s*\n', text)  # Split at periods followed by newlines

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
    with pdfplumber.open(bytes) as pdf:
        for page in pdf.pages:
            text = page.extract_text() + "\n"  # Extract text from each page
            sections = smart_section_split(text=text)
            for section in sections:
                search_result = searchBG_elser(text_to_search=section)
                if(search_result["score"] > 25.0):
                    matching_content.append({"pageNumber":page_num,"section":section,"sectionNumber":section_num} | search_result)
                else:
                    not_matching_content.append({"pageNumber":page_num,"section":section,"sectionNumber":section_num} | search_result)
                html_content += f"<p section-num={section_num}>{section}</p>"
                section_num = section_num + 1
            html_contents.append({"html_content":html_content})
            page_num = page_num + 1
            html_content = ""
        response["matching_sections"] = matching_content
        response["not_matching_sections"] = not_matching_content

        response["html_contents"] = html_contents
    return response

def pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        base64_str = base64.b64encode(pdf_file.read()).decode("utf-8")
    return base64_str

# Example Usage
# pdf_file = "171120231905-CorrigendumFormats.pdf"  # Replace with your PDF file path
# b64 = pdf_to_base64(pdf_file)
# sections = extract_paragraphs_from_base64(b64)
# print(json.dumps(sections))
# for i, para in enumerate(paragraphs):  # Print first 5 paragraphs
#     print(f"Paragraph {i}: {para}\n")
