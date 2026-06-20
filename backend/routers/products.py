from fastapi import APIRouter, HTTPException,Depends
from database import SessionLocal,get_db
from model import Product
from schemas import Productcreate,Productres

from utils.security import get_current_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/create_product")
async def create_product(product : Productcreate,db:Session = Depends(get_db),current_user:str = Depends(get_current_user)):
    
        new_product = Product(prod_name=product.prod_name,category=product.category,description=product.description,brand=product.brand)
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return {"message":"Product listed Sucessfully"}
   
        
@router.get("/fetch_product")
async def fetch_product(db:Session=Depends(get_db),current_user:str = Depends(get_current_user)):
        product_list = db.query(Product).all()
        return product_list
            


