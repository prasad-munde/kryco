from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer

client = MilvusClient(
    uri="http://localhost:19530"
)

client.drop_collection("creators")