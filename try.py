from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

vs = Milvus(
    embedding_function=embedding,
    collection_name="creators",
    connection_args={
        "uri": "http://localhost:19530",
    },
    drop_old=True,
)

print("VectorStore created successfully!")