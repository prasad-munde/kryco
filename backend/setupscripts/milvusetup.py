from pymilvus import MilvusClient

client = MilvusClient(
    uri="http://localhost:19530"
)

COLLECTION_NAME = "creators"

if client.has_collection(COLLECTION_NAME):
    client.drop_collection(COLLECTION_NAME)
    print(f"Dropped collection: {COLLECTION_NAME}")
else:
    print("Collection does not exist.")