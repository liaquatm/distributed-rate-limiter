import redis
import time

class RateLimiter:
    # LUA_SCRIPT: The logic that runs inside Redis
    # KEYS[1] = The user's unique key (e.g., "rate_limit:127.0.0.1")
    # ARGV[1] = Refill rate (tokens per second)
    # ARGV[2] = Bucket capacity (max burst)
    # ARGV[3] = Current timestamp
    LUA_SCRIPT = """
    local key = KEYS[1]
    local rate = tonumber(ARGV[1])
    local capacity = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local requested = 1

    -- 1. Get the last time we updated this key
    local last_update_key = key .. ":ts"
    local last_update = tonumber(redis.call("get", last_update_key))
    if last_update == nil then
        last_update = 0
    end

    -- 2. Get current tokens (if none, start full)
    local current_tokens = tonumber(redis.call("get", key))
    if current_tokens == nil then
        current_tokens = capacity
    end

    -- 3. Calculate how many tokens we Gained since last time
    -- Formula: (Time Passed) * (Tokens per Second)
    local delta = math.max(0, now - last_update)
    local filled_tokens = math.min(capacity, current_tokens + (delta * rate))

    -- 4. Check if we have enough
    local allowed = 0
    if filled_tokens >= requested then
        filled_tokens = filled_tokens - requested
        allowed = 1
        -- Save the new state
        redis.call("set", last_update_key, now)
        redis.call("set", key, filled_tokens)
    else
        -- Even if we reject, we update the refill so they don't lose credit for time passed
        redis.call("set", last_update_key, now)
        redis.call("set", key, filled_tokens)
    end

    -- 5. Set expiry (clean up keys after 60s of silence)
    redis.call("expire", key, 60)
    redis.call("expire", last_update_key, 60)

    return allowed
    """

    def __init__(self, redis_client: redis.Redis, rate: float, capacity: int):
        self.redis = redis_client
        self.rate = rate          
        self.capacity = capacity  
        # Pre-load the script into Redis for performance
        self.script = self.redis.register_script(self.LUA_SCRIPT)

    def is_allowed(self, user_id: str) -> bool:
        key = f"rate_limit:{user_id}"
        now = time.time()
        
        # Run the script atomically
        # Returns 1 if allowed, 0 if blocked
        result = self.script(
            keys=[key], 
            args=[self.rate, self.capacity, now]
        )
        
        return result == 1