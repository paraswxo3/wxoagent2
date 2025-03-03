from elasticsearch import Elasticsearch
import requests
import os

# Connect to Elasticsearch
api_key = os.getenv("ES_API_KEY")
es_url = os.getenv("ES_URL")
es =  Elasticsearch(
    es_url,
    api_key=api_key,
    verify_certs=False
)


es.indices.delete(index="bg_docs2", ignore_unavailable=True)
es.indices.create(
    index="bg_docs2",
    settings={"index": {"default_pipeline": "bg_docs_ingest2"}},
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