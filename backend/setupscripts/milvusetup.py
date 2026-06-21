from pymilvus import MilvusClient

client = MilvusClient(
    uri="http://localhost:19530"
)

COLLECTION_NAME = "creators"


def setup_milvus():
    
    if client.has_collection(COLLECTION_NAME):
        client.drop_collection(COLLECTION_NAME)
        print(f"Dropped collection: {COLLECTION_NAME}")

    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=768
    )

    print(f"Created collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    setup_milvus()