import pdf_test
import re
import base64
import json
import os
from elasticsearch import Elasticsearch, helpers

api_key = os.getenv("ES_API_KEY")
es_url = os.getenv("ES_URL")
match_thres = os.getenv("DOC_SEARCH_THRESH",16)

es =  Elasticsearch(
    es_url,
    api_key=api_key,
    verify_certs=False
)
def pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")

def upload_bg_doc_es(pdf_base64,filename):
    documents = []
    documents.append(
        {
            "_index": "bg_docs2",
            "_source": {"data": pdf_base64,"filename":filename}
        }
    )
    response = helpers.bulk(es, documents)
    return response

def bg_query(input_query,filename):
    response = es.search(
        index="bg_docs2",
        size=2,
        source={
            "excludes": ["passages.sparse"]
        },
        query={       
        "bool":{
            "filter":[
                 { "term": { "filename.keyword": filename} },
                 {
		"nested": {
			"path": "passages",
			"query": {
				"bool": {
					"filter": [],
					"should": [
						{
							"text_expansion": {
								"passages.sparse.tokens": {
									"model_id": ".elser_model_2_linux-x86_64",
									"model_text": input_query
								}
							}
						}
					]
				}
			},
			"inner_hits": {
				"_source": {
					"excludes": [
						"passages.sparse"
					]
				}
			}
		}
	}
            ]
    }
    }	
    )
    # print(response.body)
    text = extract_inner_hits(json.dumps(response.body))
    print("text",json.dumps(text))
    return text

def extract_inner_hits(data):
    results = []
    data = json.loads(data)
    # Navigate to hits
    if "hits" in data and "hits" in data["hits"]:
        for hit in data["hits"]["hits"]:
            if "inner_hits" in hit:
                for inner_hit_key, inner_hit_value in hit["inner_hits"].items():
                    if "hits" in inner_hit_value and "hits" in inner_hit_value["hits"]:
                        for inner_doc in inner_hit_value["hits"]["hits"]:
                            text = inner_doc.get("_source", {}).get("text", "")
                            score = inner_doc.get("_score", 0)
                            if score > match_thres:
                                text = text.replace("\n\n", "\n")
                                # print("TEXT",text)
                                results.append({"content": text, "score": score})
    
    return results

# Example Usage
# pdf_file = "11FormatofBankGuaranteeWithAmount.pdf"  # Replace with your PDF file path
# # b64 = pdf_to_base64(pdf_file)
# # response = upload_bg_doc_es(b64,"11FormatofBankGuaranteeWithAmount.pdf")
# query = "the amount of this bank guarantee?"
# query = "what is the virat kohli avarage against bgdesh"
# response = bg_query(query,pdf_file)
# print("response",json.dumps(response[0]))

