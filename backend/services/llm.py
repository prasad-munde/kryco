import os
from schemas import CreatorRecommendationList
from dotenv import load_dotenv
from langsmith import traceable
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()

api_key=os.environ.get("GEMINIAPIKEY")

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                               api_key=api_key)
structured_model = model.with_structured_output(CreatorRecommendationList)

prompt = ChatPromptTemplate.from_template("""
You are an AI influencer marketing assistant.

Brand Requirement:
{query}

Retrieved Creators:
{creators}

Rank the creators from best to worst.

Base the ranking on:
- niche
- bio
- platform
- relevance to the campaign

Provide a reason for every recommendation.
""")

chain = prompt | structured_model

@traceable
def rank_creators(query: str, creators: list):
    response = chain.invoke(
        {
            "query": query,
            "creators": creators,
        }
    )
 

    return response


