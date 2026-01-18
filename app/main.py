from fastapi import FastAPI, HTTPException, Request
import redis
import os
from app.limiter import RateLimiter

app = FastAPI()

redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

# Token Bucket
# Rate 1.0 = 1 token per second
# Capacity 10 = Max burst of 10 requests at once
limiter = RateLimiter(redis_client=r, rate=1.0, capacity=10)

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/limited")
def limited_endpoint(request: Request):
    client_ip = request.client.host

    if not limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    return {"message":"Request allowed!", "ip":client_ip}


@app.get("/hit")
def hit_counter():
    try:
        count = r.incr("global_hits")
        return {"hits":count}
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="Redis connection error")