from fastapi import FastAPI, File, Header, Depends, Security, HTTPException, Body, UploadFile
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from pdf_to_html import extract_paragraphs_from_base64,check_bg_amount_in_es
from typing import List
from bg_elser_query import searchBG_elser
from bg_docs_actions import bg_query,upload_bg_doc_es
from bg_query_doc import query_doc,search_and_query_doc
import json

app = FastAPI()

class BGSection(BaseModel):
    pageNumber: int
    section: str
    section_preview: str
    sectionNumber: int
    score: float
    clause_type: str
    content: str
    explanation: str
    classification: str

class HTMLContent(BaseModel):
    html_content: str

class BGSections(BaseModel):
    matching_sections: List[BGSection]
    not_matching_sections: List[BGSection]
    html_contents: List[HTMLContent]

class BGAmount(BaseModel):
    bg_amount: float

class FindInBGDocsInput(BaseModel):
    content: str
    file_name: str

class FindInBGDocsOutput(BaseModel):
    content: str
    score: float

class FindInBGDocsOutputList(BaseModel):
    output: List[FindInBGDocsOutput]

class QueryBGDocInput(BaseModel):
    paragraphs :List[str]
    user_query: str

class QueryBGDocOutput(BaseModel):
    response: str

class QueryBGDocOutputWrapper(BaseModel):
    sections: List[FindInBGDocsOutput]
    answer: str

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "Auth01234":
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key"
        )
    return api_key


@app.post("/find_sections", response_model=BGSections, dependencies=[Depends(verify_api_key)])
def find_sections(input_doc: str = Body(..., embed=True)):
    response = extract_paragraphs_from_base64(pdf_base64=input_doc)
    # print(json.dumps(response))
    return response

@app.post("/find_bg_amount", response_model=BGAmount, dependencies=[Depends(verify_api_key)])
def find_bg_amount(input_doc: str = Body(..., embed=True)):
    response = check_bg_amount_in_es(pdf_base64=input_doc)
    print("bg amount",response)
    return {"bg_amount":response}

@app.post("/find_in_bg_doc", response_model=FindInBGDocsOutputList, dependencies=[Depends(verify_api_key)])
def find_in_bg_doc(query_input: FindInBGDocsInput = Body(..., embed=True)):
    response = bg_query(filename=query_input.file_name,input_query=query_input.content)
    # print("response",json.dumps(response))
    return {"output":response}

@app.post("/bg_query_doc", response_model=QueryBGDocOutput, dependencies=[Depends(verify_api_key)])
def bg_query_doc(query_input: QueryBGDocInput = Body(..., embed=True)):
    response = query_doc(paragraphs=query_input.paragraphs,search_query=query_input.user_query)
    # print("response",json.dumps(response))
    return {"response":response}

@app.post("/bg_search_doc_and_query", response_model=QueryBGDocOutputWrapper, dependencies=[Depends(verify_api_key)])
def bg_search_doc_and_query(query_input: FindInBGDocsInput = Body(..., embed=True)):
    response = search_and_query_doc(filename=query_input.file_name,input_query=query_input.content)
    # print("response",json.dumps(response))
    return {"sections":response["sections"],"answer":response["answer"]}

@app.post("/upload_doc_to_es", response_model=QueryBGDocOutput, dependencies=[Depends(verify_api_key)])
def upload_doc_to_es(doc_input: FindInBGDocsInput = Body(..., embed=True)):
    response = upload_bg_doc_es(filename=doc_input.file_name,pdf_base64=doc_input.content)
    print("response",response)
    return {"response":"uploaded"}

if __name__ == '__main__':
    import uvicorn
    print("starting.....")
    uvicorn.run(app, host='0.0.0.0', port=8080)