from utils.redis import redis_client
from fastapi import APIRouter, HTTPException,Depends


router = APIRouter()
@router.get("/redis-test")
async def redis_test():

    redis_client.set("hello", "world")

    value = redis_client.get("hello")

    return {
        "redis": value
    }