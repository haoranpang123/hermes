"""Redis 连接管理"""

from redis.asyncio import ConnectionPool, Redis as AsyncRedis

from app.config import get_settings

settings = get_settings()

# Redis 连接池
redis_pool: ConnectionPool | None = None
redis_client: AsyncRedis | None = None


async def init_redis() -> None:
    """初始化 Redis 连接池"""
    global redis_pool, redis_client
    redis_pool = ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=20,
        decode_responses=True,
    )
    redis_client = AsyncRedis(connection_pool=redis_pool)


async def close_redis() -> None:
    """关闭 Redis 连接池"""
    global redis_pool, redis_client
    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()
    redis_client = None
    redis_pool = None


async def get_redis() -> AsyncRedis:
    """获取 Redis 客户端"""
    if redis_client is None:
        await init_redis()
    return redis_client
