from backend.app.cache_layer.cache import FallbackTTLCache, LocalTTLCache, build_cache


def test_build_cache_without_redis_url():
    cache = build_cache(None)
    assert isinstance(cache, LocalTTLCache)


def test_build_cache_falls_back_when_redis_unavailable():
    cache = build_cache("redis://127.0.0.1:6399/0")
    assert isinstance(cache, FallbackTTLCache)
    cache.set("test-key", {"value": 1}, ttl_seconds=30)
    assert cache.get("test-key") == {"value": 1}
