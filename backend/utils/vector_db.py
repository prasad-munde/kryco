from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
from utils.embeddings import creator_to_document
client = MilvusClient(
    uri="http://localhost:19530"
)
model = SentenceTransformer("all-mpnet-base-v2")

def insert_creator(creator):
    document = creator_to_document(creator)
    embedding = model.encode(document).tolist()


    client.drop_collection("creators")
    if not client.has_collection("creators"):
        client.create_collection(
            collection_name="creators",
            dimension=768
        )

    result = client.insert(
        collection_name="creators",
        data=[
            {
                "id": creator.id,
                "vector": embedding
            }
        ]
    )
    print(result)
    
def search_creators(query: str):
    query_embedding = model.encode(query).tolist()

    results = client.search(
        collection_name="creators",
        data=[query_embedding],
        limit=5
    )

    return results
