import os
from jose import jwt,JWTError
from datetime import datetime,timedelta
from fastapi import Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401,detail="invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401,detail="invalid token")

def create_acess_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    
    return token

print(type(ACCESS_TOKEN_EXPIRE_MINUTES))
