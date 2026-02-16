import logging
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager

from domain.core.constants import RedisPrefix
from infrastructure.redis import get_sync_redis_client
from domain.core.settings import settings

logger = logging.getLogger(__name__)

cache = Cache()
jwt = JWTManager()
redis_client = get_sync_redis_client()

if redis_client:
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=settings.REDIS_URL,
        key_prefix=RedisPrefix.RATELIMIT,
    )
    logger.info("Flask_Limiter_using_Redis_storage")
else:
    limiter = Limiter(key_func=get_remote_address)
    logger.warning("Flask_Limiter_using_in-memory_storage")
