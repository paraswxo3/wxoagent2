from elasticsearch import Elasticsearch
import os

# Connect to Elasticsearch
api_key = os.getenv("ES_API_KEY")
es_url = os.getenv("ES_URL")
es =  Elasticsearch(
    es_url,
    api_key=api_key,
    verify_certs=False
)

# List of example clauses
# clauses = [
#     {"text":"This Guarantee shall remain valid from [Start Date] to [Expiry Date].","clause":"Duration"},
#     {"text":"The Bank is liable to pay upon the Beneficiary's first written demand.","clause":"Demand"},
#     {"text":"Any claim under this Guarantee shall be made in writing before the expiry date.","clause":"Expiry"}
# ]
# documents = []

# for index,dictionary in enumerate(clauses,start=1):
#     documents.append(
#         {
#             "_index": "bank_guarantee_clauses",
#             "_source": {"content": dictionary["text"],"clause":dictionary["clause"]}
#         }
#     )
# helpers.bulk(es, documents)
# for i, clause in enumerate(clauses):
#     es.index(index="bank_guarantee_clauses", id=i, body={"content": clause},timeout="120s")
# print("Clauses Indexed Successfully!")
def searchBG_elser(text_to_search: str):
    print("---------- searching in ES")
    response = es.search(
        index="bank_guarantee_clauses",
        size=3,
        query={
            "text_expansion": {
                "content_embedding": {
                    "model_id": ".elser_model_2_linux-x86_64",
                    "model_text": text_to_search
                }
            }
        }
    )
    # print(response.body)
    print("------- finished searching in ES")

    if len(response["hits"]["hits"]) > 0:
        dict = response["hits"]["hits"][0]
        return {"score":dict["_score"],"clause_type":dict["_source"]["clause"],"content":dict["_source"]["content"]}
    else:
        return {"score":0.0,"clause_type":"","content":""}

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

    

# text = "This Guarantee shall remain valid from 10th Jan 2024 to 12 December 2024"
# # text = "hello there"
# response = searchBG_elser(text)
# print(response)
# for hit in response["hits"]["hits"]:
#         doc_id = hit["_id"]
#         score = hit["_score"]
#         content = hit["_source"]["content"]
#         clause = hit["_source"]["clause"]
#         print(f"Score: {score}, Content: {content}, Clause: {clause}\n")
# # Function to generate embeddings using ELSER
# def generate_embedding(text):
#     url = "https://my-elasticsearch-project-bab827.es.us-east-1.aws.elastic.cloud:443/_inference/sparse_embedding/.elser-2-elasticsearch"
#     body = {
#         "task_settings": {
#             "model_id": ".elser-2-elasticsearch",
#             "input": {
#                 "field": "text"
#             },
#             "output": {
#                 "field": "elser_embedding"
#             }
#         },
#         "document": {
#             "content": text
#         }
#     }
#     response = requests.post(url, json=body,headers={"Content-Type":"application/json","Authorization":"ApiKey "+api_key})
#     print("response ",response.content)
#     # return response.json()["inference_results"][0]["predicted_value"]
# # generate_embedding("This Guarantee shall remain valid from [Start Date] to [Expiry Date].")
# # Index clauses
# # for i, clause in enumerate(clauses):
# #     generate_embedding(clause)
# #     # print("embedding",embedding)
# #     # es.index(index="bank_guarantee_clauses", id=i, body={"text": clause, "elser_embedding": embedding})

