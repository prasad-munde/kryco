from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langchain_core.documents import Document
from langsmith import traceable

from utils.embeddings import creator_to_document

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
COLLECTION_NAME = "creators"
MILVUS_URI = "http://localhost:19530"

embedding_model = HuggingFaceEmbeddings(
    model_name=MODEL_NAME
)

vectorstore = Milvus(
    embedding_function=embedding_model,
    connection_args={
        "uri": MILVUS_URI
    },
    collection_name=COLLECTION_NAME,
    auto_id=False,
)


@traceable
def insert_creator(creator):
    document = creator_to_document(creator)

    doc = Document(
        page_content=document,
        metadata={
            "id": creator.id,
            "name": creator.name,
            "platform": creator.platform,
            "niche": creator.niche,
            "bio": creator.bio,
        },
    )

    vectorstore.add_documents(
        documents=[doc],
        ids=[str(creator.id)]
    )


@traceable
def search_creators(query: str):
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5}
    )

    return retriever.invoke(query)