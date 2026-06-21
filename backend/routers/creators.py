from fastapi import APIRouter, HTTPException,Depends
from database import SessionLocal,get_db
from model import Creator
from schemas import creatorcreate
from utils.embeddings import creator_to_document
from utils.vector_db import insert_creator
from utils.security import get_current_user
from sqlalchemy.orm import Session
from utils.vector_db import search_creators
router = APIRouter()

@router.post("/register_creator")
async def register_creator(creator:creatorcreate,db:Session=Depends(get_db),currrent_user:str=Depends(get_current_user)):
    new_creator = Creator(name=creator.name,niche=creator.niche,platform=creator.platform,bio=creator.bio)
    db.add(new_creator)
    db.commit()
    db.refresh(new_creator)
    insert_creator(new_creator)
    return {"message":"Creator Profile created succesfully"}

@router.get("/fetch_creator")
async def fetch_creators(db:Session=Depends(get_db),currrent_user:str=Depends(get_current_user)):
    creator_list = db.query(Creator).all()
    return creator_list

@router.get("/search")
def search(
    query: str,
    db: Session = Depends(get_db)
):
    results = search_creators(query)

    creator_ids = [
        hit["id"]
        for hit in results[0]
    ]

    creators = db.query(Creator).filter(
        Creator.id.in_(creator_ids)
    ).all()

    return creators
