import hashlib
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from loguru import logger
from prometheus_client import Counter

cached_queryset_hit = Counter("cached_queryset_hit", "Number of requests served by a cached Queryset", ["model"])
cached_queryset_miss = Counter("cached_queryset_miss", "Number of  requests not served by a cached Queryset", ["model"])
cached_queryset_evicted = Counter("cached_queryset_evicted", "Number of cached Querysets evicted",['model'])

class CachedQuerySetMixIn:
    """Mixin class to cache querysets based on user and request parameters.

    This class provides a mechanism to cache the results of queryset retrievals, 
    reducing the need for repeated database queries. It generates a unique cache key 
    based on the user's identity and the request parameters, allowing for efficient 
    retrieval of cached data when available.

    Methods:
        get_queryset(): Retrieves the queryset, utilizing cache if available.

    Args:
        self: The instance of the class.

    Returns:
        The queryset, either from the cache or freshly retrieved and cached.

    Raises:
        Any exceptions raised by the underlying queryset retrieval or filtering methods.
    """
     
    def get_queryset(self):
        user_id = self.request.user.id if self.request.user.is_authenticated else 'anon'
        query_params = self.request.GET.urlencode()
        query_params_hash = hashlib.md5(query_params.encode('utf-8')).hexdigest()

        # Get the model name(s) associated with the view
        model_names = '_'.join([model.__name__ for model in getattr(self, 'cache_models', [])])
        model_names.append(getattr('primary_model').__name__)
        cache_key = f"{getattr('primary_model').__name__}:{self.__class__.__name__}_{model_names}_{user_id}_{query_params_hash}_cache_key"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(f"Cache Hit for {getattr('primary_model').__name__}")
            cached_queryset_hit.labels(model=getattr('primary_model').__name__).inc()
            return cached_data
        cached_queryset_miss.labels(model=getattr('primary_model').__name__).inc()
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)
        data = self.serializer_class(queryset, many=True).data
        cache.set(cache_key, data, timeout=3600)
        return queryset




@receiver([post_save, post_delete])
def invalidate_cache(sender, instance, **kwargs):
    model_name = sender.__name__
    # Pattern to match cache keys that include the model name
    cache_key_pattern = f"{model_name}:*"
    if cache_keys := cache.keys(cache_key_pattern):
        # Delete all matching keys
        cache.delete_many(cache_keys)
        cached_queryset_evicted.labels(model=model_name).inc()
        logger.debug(f"Cache invalidated for model: {model_name}")


