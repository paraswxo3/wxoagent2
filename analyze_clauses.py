
import os
import json
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai import Credentials
import re


def analyze_clauses(clauses):
    params = {"decoding_method": "greedy", "max_new_tokens": 6000, "min_new_tokens": 1}
    # model = "google/flan-ul2"
    API_KEY = os.getenv("WATSONX_API_KEY")
    PROJECT_ID   = os.getenv("PROJECT_ID")
    MODEL_ID   = "mistralai/mixtral-8x7b-instruct-v01"

    credentials = Credentials(api_key=API_KEY,url="https://us-south.ml.cloud.ibm.com")
  
    model = ModelInference(credentials=credentials,model_id=MODEL_ID,project_id=PROJECT_ID)

    llm_prompt = f"""  
    You are an expert in analyzing bank guarantees.  Analyze the following Bank Guarantee clauses. Identify if they are onerous and explain why.

    Clauses:
    {clauses}

    Label each of the above clauses as: 
    - **Onerous**: The clause poses a significant risk to the bank.
    - **Neutral**: The clause is standard and does not pose a risk.
    Provide a very brief explanation (less than 50 words) for each classification. Do not use phrases like - 'This clause is Onerous because' in the explanation

    ### **Expected Output (Strict JSON format)**:
    Return the result in **exactly** the following JSON format **without deviation**:
        {{
            [
                {{"explanation": "First line with a very brief explanation here", "classification": "Onerous (High Risk)"}},
                {{"explanation": "Second line with a very brief explanation here", "classification": "Neutral"}}
            ]
        }}
    ### Return only the JSON Object
    ### Do not return any examples
    ### Do not include markdown formatting in your response.
    """
    onerous_clauses = model.generate_text(prompt=llm_prompt, params={"decoding_method": "greedy", "max_new_tokens": 250})
    # print(key_assumptions)
    return onerous_clauses
def extract_json_from_text(response_text):
    json_pattern = r'\[.*?\]'  # Match JSON objects `{}` or arrays `[]`
    matches = re.findall(json_pattern, response_text, re.DOTALL)  # Extract potential JSON
    for match in matches:
        try:
            return json.loads(match)  # Return first valid JSON
        except json.JSONDecodeError:
            continue
    return None  # No valid JSON found

onerous_clauses = """
1. This BANK GUARANTEE shall be a primary obligation of the Guarantor Bank and accordingly UPNEDA shall not be obliged before enforcing this BANK GUARANTEE to take any action in any court
2. We are liable to pay the guaranteed amount or any part thereof under this Bank Guarantee only if UPNEDA serves upon us a written claim or demand.
3. Our liability under this Guarantee is restricted to INR…………………
4. This guarantee shall be valid and binding on this Bank up to and including……….. and shall not be terminable by notice or any change in the constitution of the Bank or the term of contract or by any other reasons whatsoever and our liability hereunder shall not be impaired or discharged by any extension of time or variations or alternations made, given, or agreed with or without our knowledge or consent, by or between parties to the respective agreement.
5. Our Guarantee shall remain in force until…………….. UPNEDA shall be entitled to invoke this Guarantee till ………. [Insert date which is [Insert the number] of days after the date in the preceding sentence].
"""
# response = analyze_clauses(onerous_clauses)
# print(response)
# # json_output = json.loads(response)
# # print(json.dumps(json_output, indent=2))
# result = extract_json_from_text(response)
# print(json.dumps(result))
def format_input(clauses):
    clauses_output = ""
    for index, clause in enumerate(clauses):
        formatted_clause = str(index+1) + ". "+clause + "\n"
        clauses_output += formatted_clause
    return clauses_output

# clauses = ["adadd","gsff","hfdds"]

# print(format_input(clauses))

# def format_output(clauses):
