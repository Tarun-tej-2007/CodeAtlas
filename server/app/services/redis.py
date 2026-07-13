import redis
from app.core.config import settings

# Instantiate default global connection pool
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_timeout=5,
)

class RedisService:
    """
    Service encapsulating Redis cache operations for token deactivation and revocation.
    """
    def __init__(self, client: redis.Redis = redis_client) -> None:
        self.client = client

    def revoke_token(self, jti: str, expires_in_seconds: int) -> None:
        """
        Stores the JWT ID (jti) inside the Redis blocklist with a TTL matching the token's remaining lifespan.
        """
        if expires_in_seconds <= 0:
            return
        key = f"revoked_token:{jti}"
        self.client.setex(name=key, time=expires_in_seconds, value="1")

    def is_token_revoked(self, jti: str) -> bool:
        """
        Asserts if the given JWT ID (jti) exists in the Redis blocklist.
        """
        key = f"revoked_token:{jti}"
        return self.client.exists(key) > 0
