from infrastructure.logging_config import configure_logging

configure_logging()

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse

from fastapi_app.core.middleware import setup_middleware
from fastapi_app.core.limiter import limiter
from fastapi_app.api.router import api_router
from domain.core.constants import RedisPrefix
from infrastructure.redis import get_async_redis_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async_redis = await get_async_redis_client()
    if async_redis:
        FastAPICache.init(
            RedisBackend(async_redis),
            prefix=RedisPrefix.CACHE,
            expire=3600,
        )
        app.state.redis = async_redis
        logger.info("Cache_initialized_with_Redis")


    else:
        FastAPICache.init(InMemoryBackend(), prefix=RedisPrefix.CACHE, expire=3600)
        logger.warning("Redis_initialization_failed")

    yield

    if async_redis:
        await async_redis.close()
        await async_redis.connection_pool.disconnect()
        logger.info("Redis_connection_closed")


app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests"},
    )


setup_middleware(app)

app.include_router(api_router, prefix="/api")
