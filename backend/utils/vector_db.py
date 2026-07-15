import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langchain_core.documents import Document
from langsmith import traceable
from utils.embeddings import creator_to_document
load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
MILVUS_URI = os.getenv("MILVUS_URI")

embedding_model = HuggingFaceEmbeddings(
    model_name=MODEL_NAME
)
try:
    vectorstore = Milvus(
        embedding_function=embedding_model,
        connection_args={"uri": MILVUS_URI},
        collection_name=COLLECTION_NAME,
        auto_id=False,
    )
    print("Milvus vectorstore initialized successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
    raise

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