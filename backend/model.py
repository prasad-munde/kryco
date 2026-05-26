from sqlalchemy import Column,Integer,String
from database import Base

class User(Base):
    __tablename__ ="user"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    email = Column(String,unique=True)
    hashed_password = Column(String)


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer,primary_key=True,index=True)
    prod_name = Column(String)
    category = Column(String)
    description = Column(String)
    brand = Column(String)

