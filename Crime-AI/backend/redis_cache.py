# backend/redis_cache.py

import json
import redis
import os

def get_redis_connection():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
        decode_responses=True,
    )

def cache_get(job_id: str):
    r = get_redis_connection()
    data = r.get(f"result:{job_id}")
    if data:
        return json.loads(data)
    return None

def cache_set(job_id: str, data: dict):
    r = get_redis_connection()
    r.set(f"result:{job_id}", json.dumps(data), ex=60 * 60 * 24 * 7)  # 7 days
