import pdfplumber
import re
import base64
import json
import io
from bg_elser_query import searchBG_elser
from bg_elser_query import check_bg_amount_text_from_es
from analyze_clauses import analyze_clauses, extract_json_from_text, get_bg_amount

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
    neutral_explain = "This clause is standard and does not pose a risk"
    neutral_text = "Neutral"
    llm_clause_input = ""  ## for the inital 4 not_matching_sections, call LLM to analyze them further
    llm_input_index = 0
    not_matching_clauses_indexes = []
    not_matching_clauses_index = 0
    with pdfplumber.open(bytes) as pdf:
        for page in pdf.pages:
            text = page.extract_text() + "\n"  # Extract text from each page
            sections = smart_section_split(text=text)
            for section in sections:
                search_result = searchBG_elser(text_to_search=section)
                if(search_result["score"] > 25.0):
                    matching_content.append({"pageNumber":page_num,"section":section,"sectionNumber":section_num,"classification":neutral_text,"explanation":neutral_explain} | search_result)
                else:
                    if len(section) > 70 and  search_result["score"] > 12.0:
                        not_matching_content.append({"pageNumber":page_num,"section":section,"sectionNumber":section_num,"classification":neutral_text,"explanation":""} | search_result)
                        if llm_input_index < 3:  ## for the inital 3 not_matching_sections, call LLM to analyze them further
                            llm_clause_input += str(llm_input_index+1) + ". "+first_n_words(section,45) + "\n"
                            llm_input_index += 1
                            not_matching_clauses_indexes.append(not_matching_clauses_index)
                        not_matching_clauses_index += 1
                html_content += f"<p section-num={section_num}>{section}</p>"
                section_num = section_num + 1
            
            html_contents.append({"html_content":html_content})
            page_num = page_num + 1
            html_content = ""
        analysis_output = []
        print(llm_clause_input)
        if len(not_matching_content) > 0:
            output = analyze_clauses(llm_clause_input)
            print("output",output)
            analysis_output = extract_json_from_text(output)
        print(json.dumps(analysis_output))
        output_index = 0
        for index in not_matching_clauses_indexes:
            not_matching_content[index]["classification"] = analysis_output[output_index]["classification"]
            not_matching_content[index]["explanation"] = analysis_output[output_index]["explanation"]
            output_index += 1
        response["matching_sections"] = matching_content
        not_matching_content_sorted = sort_json_by_term(not_matching_content, "classification", "Onerous")
        response["not_matching_sections"] = not_matching_content_sorted
        response["html_contents"] = html_contents
    return response

def check_bg_amount_in_es(pdf_base64):
    bg_amount = 0.0
    pdf_bytes = base64.b64decode(pdf_base64)
    bytes = io.BytesIO()
    bytes.write(pdf_bytes)
    page_num = 0
    match_section = ""
    with pdfplumber.open(bytes) as pdf:
        for page in pdf.pages:
            if page_num == 0:
                text = page.extract_text() + "\n"  # Extract text from each page
                sections = smart_section_split(text=text)
                highest_score = 0.0
                for section in sections:
                    score = check_bg_amount_text_from_es(section)
                    if score > highest_score:
                        highest_score = score
                        match_section = section
                        print(f"page number {page_num} score {highest_score}")
            page_num = page_num + 1
    print("highest_score",highest_score)
    bg_amount = get_bg_amount(match_section)
    return bg_amount


def pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        base64_str = base64.b64encode(pdf_file.read()).decode("utf-8")
    return base64_str

def first_n_words(text, n):
    words = text.split()  # Split text into words (default separator is any whitespace)
    return ' '.join(words[:n])  # Join only the first 'n' words

def sort_json_by_term(json_array, key, term):
    term_lower = term.lower()  # Convert search term to lowercase

    def custom_sort(obj):
        value = obj.get(key, "").lower()  # Get the key's value, convert to lowercase
        return (term_lower not in value, value)  # Move matching items to the top

    return sorted(json_array, key=custom_sort)


# Example Usage
# pdf_file = "171120231905-CorrigendumFormats.pdf"  # Replace with your PDF file path
# b64 = pdf_to_base64(pdf_file)
# sections = extract_paragraphs_from_base64(b64)
# print(json.dumps(sections))
# for i, para in enumerate(paragraphs):  # Print first 5 paragraphs
#     print(f"Paragraph {i}: {para}\n")

