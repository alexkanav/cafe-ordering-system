import logging
import redis
import redis.asyncio as aioredis

from domain.core.settings import settings

logger = logging.getLogger(__name__)


def get_sync_redis_client() -> redis.Redis | None:
    try:
        client = redis.Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
        logger.info("Sync_Redis_available")
        return client

    except redis.RedisError:
        logger.warning("Sync_Redis_unavailable", exc_info=True)
        return None

    except Exception:
        logger.exception("Unexpected_error_during_Sync_Redis_init")
        return None


async def get_async_redis_client() -> aioredis.Redis | None:
    try:
        client = aioredis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        await client.ping()
        logger.info("Async_Redis_available")
        return client

    except redis.RedisError:
        logger.warning("Async_Redis_unavailable", exc_info=True)
        return None

    except Exception:
        logger.exception("Unexpected_error_during_Async_Redis_init")
        return None
