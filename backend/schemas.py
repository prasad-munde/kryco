from pydantic import BaseModel,EmailStr

class userRegister(BaseModel):
    name: str
    email:EmailStr
    password:str


class userlogin(BaseModel):
    email:EmailStr
    password:str


class Productcreate(BaseModel):
    prod_name:str
    category:str
    description:str
    brand:str

class Productres(BaseModel):
    id:int
    prod_name:str
    category:str
    description:str
    brand:str

    class Config:
        from_attributes=True
    
class creatorcreate(BaseModel):
    name : str
    niche : str
    platform : str
    bio : str

class creatorres(BaseModel):
    id:int
    name : str
    niche : str
    platform : str
    bio : str
    class Config:
        from_attributes = True