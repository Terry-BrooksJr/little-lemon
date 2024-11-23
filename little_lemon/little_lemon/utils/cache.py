import hashlib
from typing import Union

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from loguru import logger
from prometheus_client import Counter
from redis.exceptions import LockNotOwnedError
from rest_framework import status
from rest_framework.response import Response

cached_queryset_hit = Counter(
    "cached_queryset_hit", "Number of requests served by a cached Queryset", ["model"]
)
cached_queryset_miss = Counter(
    "cached_queryset_miss",
    "Number of  requests not served by a cached Queryset",
    ["model"],
)
cached_queryset_evicted = Counter(
    "cached_queryset_evicted", "Number of cached Querysets evicted", ["model"]
)


class CachedResponseMixin:
    """Mixin class to provide caching functionality for API responses.

    This mixin allows views to cache their responses based on user identity and query parameters,
    improving performance by reducing the need for repeated database queries.
    """

    def get_cache_key(self) -> str:
        """Generate a unique cache key based on the request and model information.

        This method constructs a cache key that incorporates the user ID, query parameters,
        and model names associated with the view.

        Returns:
            str: A unique cache key for the current request.

        Raises:
            AttributeError: If the view does not have a 'primary_model' attribute.
        """
        user_id = self.request.user.id if self.request.user.is_authenticated else "anon"
        query_params = self.request.GET.urlencode()
        query_params_hash = hashlib.md5(query_params.encode("utf-8")).hexdigest()

        # Get the model name(s) associated with the view
        model_names = []

        # Add the primary model name
        primary_model = getattr(self, "primary_model", None)
        if primary_model:
            model_names.append(primary_model.__name__)
        else:
            raise AttributeError("View must have a 'primary_model' attribute.")

        # Add the cache_models names
        cache_models = getattr(self, "cache_models", [])
        model_names.extend(model.__name__ for model in cache_models)
        # Combine the model names into a string
        model_names_str = "_".join(model_names)

        return f"{primary_model.__name__}:{self.__class__.__name__}_{model_names_str}_{user_id}_{query_params_hash}_cache_key"

    def get_cached_response(self, cache_key) -> Union[Response | None]:
        """Retrieve cached data using the provided cache key.

        This method checks if there is cached data for the given cache key and returns it if available.

        Args:
            cache_key (str): The cache key to look up.

        Returns:
            Response or None: The cached response if found, otherwise None.
        """
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(
                f"Cache Hit for {self.primary_model.__name__} - Cache Key: {cache_key}"
            )
            cached_queryset_hit.labels(model=self.primary_model.__name__).inc()
            return Response(cached_data, status=status.HTTP_200_OK)
        else:
            logger.debug(
                f"Cache Miss for {self.primary_model.__name__}  - Cache Key: {cache_key}"
            )
            cached_queryset_miss.labels(model=self.primary_model.__name__).inc()
            return None

    def cache_response(self, cache_key, data):
        """Store data in the cache with the specified cache key.

        This method saves the provided data in the cache for a duration of one hour.

        Args:
            cache_key (str): The cache key under which to store the data.
            data: The data to be cached.
        """
        logger.debug(f"New Cache Set {cache_key}: {data}")
        cache.set(cache_key, data, timeout=settings.VIEW_CACHE_TTL)

    def list(self, request, *args, **kwargs) -> Response:
        """Handle GET requests for listing resources with caching.

        This method attempts to return a cached response if available;
        otherwise, it retrieves the data, caches it, and returns the response.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The cached or newly generated response.
        """
        cache_key = self.get_cache_key()
        if cached_response := self.get_cached_response(cache_key):
            return cached_response

        # If cache miss, proceed as usual
        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            self.cache_response(cache_key, data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        self.cache_response(cache_key, data)
        return Response(data)

    def retrieve(self, request, *args, **kwargs) -> Response:
        """Handle GET requests for retrieving a single resource with caching.

        This method checks for a cached response and returns it if available;
        otherwise, it retrieves the resource, caches it, and returns the response.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The cached or newly generated response.
        """
        cache_key = self.get_cache_key()
        if cached_response := self.get_cached_response(cache_key):
            return cached_response

        # If cache miss, proceed as usual
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        self.cache_response(cache_key, data)
        return Response(data)


@receiver([post_save, post_delete])
def invalidate_cache(sender, **kwargs):
    model_name = sender.__name__
    logger.debug(f"Signal Received For {model_name}")
    # Pattern to match cache keys that include the model name as namespace
    cache_key_pattern = f"{model_name}:*"
    logger.debug(f'Searching For Cache Key Pattern" {cache_key_pattern}')
    if cache_keys := cache.keys(cache_key_pattern):
        cache.delete_many(cache_keys)
        logger.info(f"Cache invalidated for model: {model_name}")
    else:
        logger.debug(
            f"No cache keys found for model: {model_name} using {cache_key_pattern}"
        )
