import redis
import time

class RateLimiter:
    def __init__(self, redis_client: redis.Redis, limit: int, window: int):
        self.redis = redis_client
        self.limit = limit    # e.g., 5 requests
        self.window = window  # e.g., 60 seconds

    def is_allowed(self, user_id: str) -> bool:
        """
        Returns True if request is allowed, False if limit exceeded.
        """
        # Create a unique key for this user in Redis
        # e.g., "rate_limit:user_123"
        key = f"rate_limit:{user_id}"

        # 1. Increment the counter
        current_count = self.redis.incr(key)

        # 2. If this is the FIRST request (count == 1), set the expiry
        if current_count == 1:
            self.redis.expire(key, self.window)

        # 3. Check if we exceeded the limit
        if current_count > self.limit:
            return False
        
        return True