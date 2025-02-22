from langchain_ibm import WatsonxLLM
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

import os
import json

def analyze_clauses(clauses):
    params = {"decoding_method": "greedy", "max_new_tokens": 250, "min_new_tokens": 1}
    # model = "google/flan-ul2"
    model = "mistralai/mixtral-8x7b-instruct-v01"
    api_key = os.getenv("WATSONX_API_KEY")
    llm_prompt = f"""  
    You are an expert in analyzing bank guarantees. Classify each text line into one of the following categories:
    - **Onerous (High Risk)**: The clause poses a significant risk to the bank.
    - **Neutral**: The clause is standard and does not pose a risk.

    Return the result in **exactly** the following JSON format **without deviation**:

    {{
        [
            {{"text": "First text line here", "classification": "Onerous (High Risk)"}},
            {{"text": "Second text line here", "classification": "Neutral"}}
        ]
    }}
    
    ### Input Text:
    {clauses}

    ### **Expected Output (Strict JSON format)**:
    - Return **only** the JSON object, without extra text, explanations, or comments.
    - **Do not** include markdown formatting in your response.
    """

    watsonx_llm = WatsonxLLM(model_id=model, url="https://us-south.ml.cloud.ibm.com",
                             project_id= "4d5952ab-1fa2-45d1-95d7-e9b44612c7fb", apikey=api_key,params=params)

    system_message_prompt = SystemMessagePromptTemplate.from_template(llm_prompt)
    input_template = "{clauses}"
    input_message_prompt = HumanMessagePromptTemplate.from_template(input_template)
    chat_prompt_template = ChatPromptTemplate.from_messages([system_message_prompt, input_message_prompt])
    chat_prompt = chat_prompt_template.format_prompt(clauses=clauses).to_messages()
    onerous_clauses = watsonx_llm.invoke(chat_prompt)
    # print(key_assumptions)
    return onerous_clauses

onerous_clauses = """
1. This BANK GUARANTEE shall be a primary obligation of the Guarantor Bank and accordingly UPNEDA shall not be obliged before enforcing this BANK GUARANTEE to take any action in any court
2. We are liable to pay the guaranteed amount or any part thereof under this Bank Guarantee only if UPNEDA serves upon us a written claim or demand.
3. Our liability under this Guarantee is restricted to INR…………………
4. This guarantee shall be valid and binding on this Bank up to and including……….. and shall not be terminable by notice or any change in the constitution of the Bank or the term of contract or by any other reasons whatsoever and our liability hereunder shall not be impaired or discharged by any extension of time or variations or alternations made, given, or agreed with or without our knowledge or consent, by or between parties to the respective agreement.
5. Our Guarantee shall remain in force until…………….. UPNEDA shall be entitled to invoke this Guarantee till ………. [Insert date which is [Insert the number] of days after the date in the preceding sentence].
"""
response = analyze_clauses(onerous_clauses)
json_output = json.loads(response)
print(json.dumps(json_output, indent=2))

def format_input(clauses):
    clauses_output = ""
    for index, clause in enumerate(clauses):
        formatted_clause = str(index+1) + ". "+clause + "\n"
        clauses_output += formatted_clause
    return clauses_output

# clauses = ["adadd","gsff","hfdds"]

# print(format_input(clauses))

# def format_output(clauses):
