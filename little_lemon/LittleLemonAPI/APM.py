from cacheops import cache_invalidated, cache_read
from loguru import logger
from prometheus_client import Counter

cacheops_hits = Counter("cacheops_hits", "Number of Cacheops cache hits", ["model"])

cacheops_misses = Counter(
    "cacheops_misses", "Number of Cacheops cache misses", ["model"]
)

cache_invalidations = Counter(
    "cacheops_invalidations", "Number of Cacheops cache invalidations", ["model"]
)


def on_cache_read(sender, func, hit, **kwargs):
    if hit:
        logger.debug(f"Cache Hit for {sender.__name__}")
        cacheops_hits.labels(model=sender.__name__).inc()
    else:
        logger.debug(f"Cache Miss for {sender.__name__}")
        cacheops_misses.labels(model=sender.__name__).inc()


def on_cache_invalidated(sender, **kwargs):
    logger.debug(f"Cache Invalidation  for {sender.__name__}")
    cache_invalidations.labels(model=sender.__name__).inc()


cache_read.connect(on_cache_read)
cache_invalidated.connect(on_cache_invalidated)
