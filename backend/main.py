from fastapi import FastAPI
from model import Base
from database import engine

from routers import auth
from routers import products
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(products.router)

@app.get("/")
async def root():
    return{"message":"hello world"}