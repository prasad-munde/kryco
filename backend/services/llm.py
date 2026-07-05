import os
from google import genai
from dotenv import load_dotenv
from langsmith import traceable
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
api_key=os.environ.get("GEMINIAPIKEY")
client = genai.Client(api_key=api_key)

@traceable    
def rank_creators(query:str,creator:list):
    prompt = f"""Brand requirement {query}
                 creators {creator}
            rank these creators best to worst match according to the query of brand
            Return:
            -creator id
            -rank 
            -reason

        return Json only"""

    response = client.models.generate_content(
        model="gemma-4-26b-a4b-it",
        contents = prompt
    )

    return response.text



