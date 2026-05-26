from fastapi import APIRouter, HTTPException,Depends
from database import SessionLocal
from model import Product
from schemas import Productcreate
from utils.security import get_current_user


router = APIRouter()

@router.post("/create_product")
async def create_product(product : Productcreate,current_user:str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        new_product = Product(prod_name=product.prod_name,category=product.category,description=product.description,brand=product.brand)
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return {"message":"Product listed Sucessfully"}
    finally:
        db.close()
        
