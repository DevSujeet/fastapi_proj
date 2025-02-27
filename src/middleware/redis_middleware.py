import redis.asyncio as aioredis#import aioredis
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib
import json
import logging
from typing import Optional

from src.config.configs import CacheSettings

logger = logging.getLogger("redis_cache_middleware")
logging.basicConfig(level=logging.INFO)


class RedisCacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, cache_settings: CacheSettings):
        """
        Middleware to cache FastAPI responses using Redis with Cache-Control support.

        Args:
            app (FastAPI): FastAPI application instance.
            cache_settings (CacheSettings): Configuration settings for caching.
        """
        super().__init__(app)
        self.redis_url = cache_settings.cache_url
        self.default_ttl = cache_settings.default_ttl
        self.redis = None

    async def dispatch(self, request: Request, call_next):
        """
        Process each request, applying cache strategies based on Cache-Control headers.
        """
        # Lazily initialize Redis connection
        if self.redis is None:
            self.redis = await self._initialize_redis()

        # Generate a unique cache key
        cache_key = self._generate_cache_key(request)

        # Parse the Cache-Control header
        cache_control = request.headers.get("Cache-Control", "").lower()
        if "no-store" in cache_control:
            logger.info("Cache-Control: no-store - Skipping cache for this request")
            return await call_next(request)

        if "no-cache" in cache_control:
            logger.info("Cache-Control: no-cache - Fetching fresh response")
            response = await call_next(request)
            return self._add_cache_control_header(response, ttl=0)

        max_age = self._parse_max_age(cache_control)

        try:
            if max_age is None:
                max_age = self.default_ttl

            cached_response = await self.redis.get(cache_key)
            if cached_response:
                remaining_ttl = await self.redis.ttl(cache_key)
                logger.info(f"Cache hit for key: {cache_key}, TTL remaining: {remaining_ttl} seconds")
                cached_data = json.loads(cached_response)
                return self._add_cache_control_header(
                    JSONResponse(content=cached_data),
                    ttl=remaining_ttl,
                )

            response = await call_next(request)
            if response.status_code == 200:
                response_body = await self._extract_response_body(response)
                await self.redis.set(cache_key, response_body, ex=max_age)
                logger.info(f"Response cached for key: {cache_key}, TTL: {max_age} seconds")
                return self._add_cache_control_header(response, ttl=max_age)

        except Exception as e:
            logger.error(f"Error in RedisCacheMiddleware: {e}")

        return await call_next(request)

    async def _initialize_redis(self):
        try:
            logger.info("Connecting to Redis...")
            redis = await aioredis.from_url(self.redis_url, decode_responses=True)
            logger.info("Connected to Redis.")
            return redis
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _generate_cache_key(self, request: Request) -> str:
        hash_input = f"{request.method}:{request.url.path}?{request.url.query}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def _parse_max_age(self, cache_control: str) -> Optional[int]:
        if "max-age" in cache_control:
            try:
                max_age = int(cache_control.split("max-age=")[-1].split(",")[0])
                return max_age
            except ValueError:
                logger.warning("Invalid max-age value in Cache-Control header")
        return None

    async def _extract_response_body(self, response) -> str:
        body = b"".join([chunk async for chunk in response.body_iterator])
        return body.decode("utf-8")

    def _add_cache_control_header(self, response, ttl: int):
        response.headers["Cache-Control"] = f"max-age={ttl}"
        return response
