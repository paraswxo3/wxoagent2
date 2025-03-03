
import os
import json
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai import Credentials
from bg_docs_actions import bg_query

def query_doc(search_query,paragraphs):
    llm_paragraph = ""
    for index,paragraph in enumerate(paragraphs,start=1):
        llm_paragraph += str(index)+". "+paragraph + "\n\n"

    params = {"decoding_method": "greedy", "max_new_tokens": 2048, "min_new_tokens": 1}
    API_KEY = os.getenv("WATSONX_API_KEY")
    PROJECT_ID   = os.getenv("PROJECT_ID")
    MODEL_ID   = "meta-llama/llama-3-1-70b-instruct"
    credentials = Credentials(api_key=API_KEY,url="https://us-south.ml.cloud.ibm.com")
  
    model = ModelInference(credentials=credentials,model_id=MODEL_ID,project_id=PROJECT_ID)
    llm_prompt = f"""  
        You are an AI assistant that answers user queries based on provided reference text. 

        Below are multiple paragraphs retrieved from a database. Your task is to generate the most relevant and well-supported answer to the given query. 

        ### Retrieved Paragraphs:
        {llm_paragraph}

        ### User Query:
        {search_query}

        ### Instructions:
        - Extract the most relevant information from the paragraphs to answer the query.
        - Use only the provided information; do not generate facts beyond them.
        - If multiple paragraphs contribute to the answer, synthesize the information.
        - If the answer is uncertain or not present, state: "The provided information does not contain a definitive answer."
        - Provide citations by referring to the most relevant paragraph.

        ### Final Answer:
        """
    
    response = model.generate_text(prompt=llm_prompt, params=params)
    return response

def search_and_query_doc(input_query,filename):
    search_result = ""
    docs = bg_query(input_query=input_query,filename=filename)
    input_paragraphs = []
    if docs:
        for index,doc in enumerate(docs):
            input_paragraphs.append(doc['content'])
    # print("input_paragraphs",input_paragraphs)            
    search_result = query_doc(search_query=input_query,paragraphs=input_paragraphs)
    # print("search result",search_result)
    return {"answer":search_result,"sections":docs}

# input_query = "What is the amount of this bank guarantee"
# paragraphs = """
# 1. BANK GUARANTEE FORMAT  \n\nTo   \n\nIndian Institute of Technology Palakkad  \n\nAhalia Integrated Campus   \n\nKozhipara, Palakkad  -678 557   \n\nGuarantee No.:   / Date:  \n\nGuarantee Cover from:  \n\nAmount in Rupees    :  Rs.  \n\nWHEREAS ____________, a Company incorporated under the companies Act, 1956 and having its \n\nRegistered Office at ____________________ in pursuance of Purchase Order No. _____________, dated \n\n___________ for the supply of _____________________.  \n\nAND WHEREAS it has been stipulated by you in the said contract that the supplier shall furnish you with \na bank guarantee by a scheduled commercial recognized by you for the sum specified therein as security \nfor compliance with its obligations in according with the contract.  \nAND WHEREAS we ____________________, have agreed to give the supplier such  a bank guarantee;  \n\nNOW THEREFORE we hereby affirm that we are guarantors and responsible to you, on behalf of the \n\nsupplier, up to a total of Rs._65,50,590/-_________/- (Rupees ______________), and we undertake to \n\npay you, upon your first written demand declaring the supplier to be default under the contract and \n\nwithout cavil or arguments, any sum or sums within the limits of Rs._________/- (Rupees \n\n______________only), as aforesaid, without your needing to prove or to show grounds of reasons for your \n\ndemand or the sum specified therein.  \n\nWe hereby waive the necessity of your demanding the said debt from the supplier before presenting us \n\nwith demand.  \n\nWe further agree that no change or addition to or other modification of the terms of the contact to be \n\nperformed there under or of any of the contract documents which may be made between you and the \n\nsupplier shall in any way release us from any liability under this guarantee and we hereby waive notice of \n\nany such change, addition or modification.  \n\nThis guarantee shall be valid for ___________ from the date of final supply against PO.  \n\nThis guarantee shall be valid until the _________  \n\nPO reference No.

# 2. \n\nWe further agree that no change or addition to or other modification of the terms of the contact to be \n\nperformed there under or of any of the contract documents which may be made between you and the \n\nsupplier shall in any way release us from any liability under this guarantee and we hereby waive notice of \n\nany such change, addition or modification.  \n\nThis guarantee shall be valid for ___________ from the date of final supply against PO.  \n\nThis guarantee shall be valid until the _________  \n\nPO reference No. ____________ dated __________  \n\nNotwithstanding anything contained herein our liability under this Bank Guarantee shall not exceed \n\namount Rs._ Rs._65,50,590/___________/- (Rupees ___________________ only). This Bank Guarantee \n\nshall be valid up to ___________and we are liable to pay the guaranteed amount or any part thereof under \n\n\n\nthis bank guarantee only and only if you serve upon a written claim or demand lodged at our bank counter \n\non or before ____________  \n\nAll claims under the guarantee will be payable at _________________________________  \n\nThis Guarantee will be returned to us as soon as the purpose for which it is issued is fulfilled.
# """
# response = query_doc(input_query,paragraphs)
# print(response)

