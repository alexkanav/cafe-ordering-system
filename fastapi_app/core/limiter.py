import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

from infrastructure.redis import get_sync_redis_client
from domain.core.constants import RedisPrefix
from domain.core.settings import settings

logger = logging.getLogger(__name__)


def create_limiter() -> Limiter:
    sync_redis = get_sync_redis_client()

    if sync_redis:
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=settings.REDIS_URL,
            key_prefix=RedisPrefix.RATELIMIT
        )
        logger.info("Limiter_using_Redis_storage")
    else:
        limiter = Limiter(
            key_func=get_remote_address,
            key_prefix=RedisPrefix.RATELIMIT
        )
        logger.warning("Limiter_using_in-memory_storage")
    return limiter


limiter = create_limiter()
