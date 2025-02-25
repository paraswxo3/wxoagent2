from elasticsearch import Elasticsearch
import requests

# Connect to Elasticsearch
api_key = "SWRLZ041VUJBSVlmZWZBX2NBcWk6c1c3a0ZIVUtSWk90bURIcWNkR2h4UQ=="
cloud_id = "paraswxo2:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDAwNTkxOWNiMzhmOTQ2ODQ5M2ViMzkxZjU0NDk4ZWQ2JGYwNzM4MmNjMDVjYjQzNTFhMGEwNzYzNTFmMzdlMWNi"
es =  Elasticsearch(
    "https://005919cb38f9468493eb391f54498ed6.us-central1.gcp.cloud.es.io:443",
    api_key=api_key
)

es.indices.delete(index="bg_docs1", ignore_unavailable=True)
es.indices.create(
    index="bg_docs1",
    settings={"index": {"default_pipeline": "bg_docs_ingest1"}},
    mappings={
    "_source": {
      "excludes": [
        "data",
        "attachment.content"
      ]
    },
    "properties": {
      "attachment": {
        "properties": {
          "content": {
            "type": "text",
            "fields": {
              "keyword": {
                "type": "keyword",
                "ignore_above": 256
              }
            }
          }
        }
      },
      "filename": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "ingest_timestamp": {
        "type": "date"
      },
      "passages": {
        "type": "nested",
        "properties": {
          "filename": {
            "type": "text"
          },
          "sparse": {
            "properties": {
              "is_truncated": {
                "type": "boolean"
              },
              "model_id": {
                "type": "text",
                "fields": {
                  "keyword": {
                    "type": "keyword",
                    "ignore_above": 256
                  }
                }
              },
              "tokens": {
                "type": "sparse_vector"
              }
            }
          },
          "text": {
            "type": "text"
          },
          "title": {
            "type": "text"
          }
        }
      }
    }
  }
)