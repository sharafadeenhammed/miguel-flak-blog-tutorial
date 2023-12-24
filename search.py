from elasticsearch import Elasticsearch
from app import app

es = Elasticsearch(
  api_key= app.config['ELASTICSEARCH_API_KEY'],
  cloud_id=app.config['ELASTICSEARCH_CLOUD_ID']
  
)
