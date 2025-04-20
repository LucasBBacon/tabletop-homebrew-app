# app/core/redis.py

import redis


# Initialize a Redis client on startup
r = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True,
)

def blacklist_token(token: str, ttl_seconds: int = 3600):
    """
    Add a token to the blacklist with a specified TTL.
    """
    r.setex(token, ttl_seconds, "revoked")
    
def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted.
    """
    return r.get(token) == "revoked"