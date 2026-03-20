import time
from cache import TTLCache

def test_expiration():
    cache = TTLCache(ttl_seconds=1)
    cache.set('key1', 'value1')
    assert cache.get('key1') == 'value1'
    time.sleep(1.1)
    assert cache.get('key1') is None  # Should be expired

def test_concurrent_access():
    import threading
    cache = TTLCache(ttl_seconds=60)
    errors = []

    def writer():
        for i in range(100):
            cache.set(f'key_{i}', f'value_{i}')

    def reader():
        for i in range(100):
            cache.get(f'key_{i}')

    threads = [threading.Thread(target=writer) for _ in range(5)]
    threads += [threading.Thread(target=reader) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Check some values exist
    found = sum(1 for i in range(100) if cache.get(f'key_{i}') is not None)
    assert found > 0
