import json
import redis
from app.config import get_settings

settings = get_settings()

# decode_responses=True so we work with str, not bytes
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def cache_get(key: str):
    val = redis_client.get(key)
    return json.loads(val) if val else None


def cache_set(key: str, value: dict, ttl: int = settings.CACHE_TTL_SECONDS):
    redis_client.set(key, json.dumps(value), ex=ttl)


def cache_invalidate(key: str):
    redis_client.delete(key)
