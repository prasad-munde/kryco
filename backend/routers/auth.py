from fastapi import APIRouter, HTTPException,Depends
from database import SessionLocal,get_db
from model import User

from schemas import userRegister,userlogin
from utils.security import create_acess_token,get_current_user
from passlib.context import CryptContext
from sqlalchemy.orm import Session


router = APIRouter()
pwd =CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def register(user: userRegister,db:Session =Depends(get_db)):
    
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400,detail="Email already registerd")

        hashed_password = pwd.hash(user.password)
        new_user = User(name=user.name,email=user.email,hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return{"message":"user registerd Sucessfully"}


@router.post("/login")
async def login(user:userlogin,db:Session = Depends(get_db)):
    
    
        existing_user = db.query(User).filter(User.email == user.email).first()
        if not existing_user:
            raise HTTPException(status_code=404,detail="User Not registerd")
        if not pwd.verify(user.password,existing_user.hashed_password):
            raise HTTPException(status_code=401,detail="wrong password")
        token = create_acess_token({"sub":existing_user.email})


        return{"access_token":token,"token_type":"bearer"}

@router.get("/me")
async def get_me(current_user: str = Depends(get_current_user)):
    return{"email":current_user}