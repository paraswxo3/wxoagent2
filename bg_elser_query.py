from elasticsearch import Elasticsearch
import os
import json

# Connect to Elasticsearch
api_key = os.getenv("ES_API_KEY")
es_url = os.getenv("ES_URL")
es =  Elasticsearch(
    es_url,
    api_key=api_key,
    verify_certs=False
)

def searchBG_elser(text_to_search: str):
    response = es.search(
        index="bank_guarantee_clauses_live",
        size=1,
        query={
            "text_expansion": {
                "embedding": {
                    "model_id": ".elser_model_2_linux-x86_64",
                    "model_text": text_to_search
                }
            }
        }
    )

    if len(response["hits"]["hits"]) > 0:
        dict = response["hits"]["hits"][0]
        # print(dict)
        return {"clause_type":dict["_source"]["clause_category"],"category_meaning":dict["_source"]["category_meaning"],
                "category_example":dict["_source"]["category_example"]}
    else:
        return {"clause_type":"","category_meaning":"","category_example":""}

def check_bg_amount_text_from_es(input_text: str):
    response = es.search(
        index="bank_guarantee_amount",
        size=3,
        query={
            "text_expansion": {
                "content_embedding": {
                    "model_id": ".elser_model_2_linux-x86_64",
                    "model_text": input_text
                }
            }
        }
    )
    # print(response.body)
    if len(response["hits"]["hits"]) > 0:
        dict = response["hits"]["hits"][0]
        # print("search score", dict["_score"])
        return dict["_score"]

# clause = "10 We have the power to issue this Gua rantee in your favour under the Charter of our Bank and the undersigned has full power to execute this Guarantee under the Power of Attorney granted to him by the Bank"    
# print(searchBG_elser("clause"))