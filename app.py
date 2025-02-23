from fastapi import FastAPI, File, Header, Depends, Security, HTTPException, Body, UploadFile
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from pdf_to_html import extract_paragraphs_from_base64,check_bg_amount_in_es
from typing import List
from bg_elser_query import searchBG_elser
import json

app = FastAPI()

class BGSection(BaseModel):
    pageNumber: int
    section: str
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

if __name__ == '__main__':
    import uvicorn
    print("starting.....")
    uvicorn.run(app, host='0.0.0.0', port=8080)