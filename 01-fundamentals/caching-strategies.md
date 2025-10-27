# Caching Strategies 🟢

## 🎯 Learning Objectives
- Understand different caching patterns and when to use them
- Learn cache placement strategies for maximum performance
- Implement cache eviction policies effectively
- Design distributed caching systems

## 📖 What is Caching?

**Caching** stores frequently accessed data in fast storage for quick retrieval. It's one of the most effective ways to improve system performance and reduce load on backend systems.

### Why Caching Works
- **80/20 Rule**: 80% of requests access 20% of data
- **Temporal locality**: Recently accessed data likely to be accessed again
- **Speed difference**: RAM is ~1000x faster than disk, Cache is ~100x faster than RAM

### Performance Impact
```
Database query: 10-100ms
Cache lookup: 0.1-1ms
Performance improvement: 10-1000x faster
```

## 🏗️ Caching Levels

### 1. Browser Cache (Client-Side)
```html
<!-- HTTP Cache Headers -->
<script>
// Cache-Control: max-age=3600 (1 hour)
// ETag: "abc123"
// Last-Modified: Wed, 21 Oct 2024 07:28:00 GMT
</script>
```

**Benefits:**
- Reduces server load
- Improves user experience
- Saves bandwidth

**Use for:** Static content (CSS, JS, images)

### 2. CDN Cache (Edge Servers)
```
[User in NY] → [CDN Edge NYC] → [Origin Server SF]
[User in LA] → [CDN Edge LAX] → [Origin Server SF]
```

**Benefits:**
- Reduced latency (geographically closer)
- Offloads origin server
- DDoS protection

**Use for:** Static assets, videos, popular content

### 3. Application Cache (In-Memory)
```python
# In-memory cache examples
cache = {}  # Simple dictionary
# Or Redis, Memcached for distributed caching
```

**Benefits:**
- Fastest access times
- Reduces database load
- Improves response times

**Use for:** Database query results, session data, computed values

### 4. Database Cache (Query Results)
```sql
-- Query result caching
SELECT * FROM users WHERE active = 1;  -- Cached for 5 minutes
```

**Benefits:**
- Reduces query execution time
- Decreases database CPU usage
- Improves concurrent user capacity

## 🔄 Cache Patterns

### 1. Cache-Aside (Lazy Loading)

The application manages the cache directly.

```python
import time

class CacheAsideExample:
    def __init__(self, cache, database):
        self.cache = cache
        self.database = database

    def get_user(self, user_id):
        # Try cache first
        cache_key = f"user:{user_id}"
        user = self.cache.get(cache_key)

        if user is None:
            # Cache miss - get from database
            print(f"Cache miss for user {user_id}")
            user = self.database.get_user(user_id)

            if user:
                # Store in cache with TTL
                self.cache.set(cache_key, user, ttl=3600)  # 1 hour
        else:
            print(f"Cache hit for user {user_id}")

        return user

    def update_user(self, user_id, user_data):
        # Update database first
        self.database.update_user(user_id, user_data)

        # Invalidate cache to maintain consistency
        cache_key = f"user:{user_id}"
        self.cache.delete(cache_key)

        # Optional: Update cache immediately
        # self.cache.set(cache_key, user_data, ttl=3600)

# Usage example
class SimpleCache:
    def __init__(self):
        self.data = {}
        self.expiry = {}

    def get(self, key):
        if key in self.expiry and time.time() > self.expiry[key]:
            del self.data[key]
            del self.expiry[key]
            return None
        return self.data.get(key)

    def set(self, key, value, ttl=None):
        self.data[key] = value
        if ttl:
            self.expiry[key] = time.time() + ttl

    def delete(self, key):
        self.data.pop(key, None)
        self.expiry.pop(key, None)
```

**Pros:**
- ✅ Application controls cache logic
- ✅ Only requested data is cached
- ✅ Cache failures don't break application

**Cons:**
- ❌ Cache miss penalty (extra roundtrip)
- ❌ Application complexity increases
- ❌ Risk of stale data

**Best for:** Read-heavy applications with unpredictable access patterns

### 2. Read-Through Cache

Cache sits between application and database, managing data automatically.

```python
class ReadThroughCache:
    def __init__(self, database):
        self.cache_data = {}
        self.database = database

    def get(self, key):
        if key not in self.cache_data:
            # Cache miss - automatically load from database
            value = self.database.get(key)
            if value:
                self.cache_data[key] = value
            return value
        return self.cache_data[key]

# Application usage
cache = ReadThroughCache(database)
user = cache.get(f"user:{user_id}")  # Cache handles DB lookup
```

**Pros:**
- ✅ Simpler application code
- ✅ Automatic cache population
- ✅ Consistent interface

**Cons:**
- ❌ Cache miss penalty still exists
- ❌ Less control over caching logic

### 3. Write-Through Cache

Writes go to cache and database simultaneously.

```python
class WriteThroughCache:
    def __init__(self, database):
        self.cache_data = {}
        self.database = database

    def get(self, key):
        return self.cache_data.get(key)

    def set(self, key, value):
        # Write to both cache and database
        self.cache_data[key] = value
        self.database.set(key, value)

    def update_user(self, user_id, user_data):
        # Update both cache and database
        cache_key = f"user:{user_id}"
        self.set(cache_key, user_data)

# Usage
cache = WriteThroughCache(database)
cache.update_user(123, {"name": "John", "email": "john@example.com"})
```

**Pros:**
- ✅ Data consistency between cache and database
- ✅ No cache miss on reads after writes
- ✅ Durable writes

**Cons:**
- ❌ Higher write latency
- ❌ Unnecessary writes for rarely-read data
- ❌ Cache can fill with cold data

**Best for:** Write-heavy applications requiring strong consistency

### 4. Write-Behind (Write-Back) Cache

Writes go to cache immediately, database updated asynchronously.

```python
import threading
import queue
import time

class WriteBehindCache:
    def __init__(self, database, flush_interval=5):
        self.cache_data = {}
        self.dirty_keys = set()
        self.database = database
        self.flush_interval = flush_interval
        self.write_queue = queue.Queue()
        self.running = True

        # Start background thread for database writes
        self.writer_thread = threading.Thread(target=self._background_writer)
        self.writer_thread.daemon = True
        self.writer_thread.start()

    def get(self, key):
        return self.cache_data.get(key)

    def set(self, key, value):
        # Write to cache immediately
        self.cache_data[key] = value
        self.dirty_keys.add(key)

        # Queue for background database write
        self.write_queue.put((key, value))

    def _background_writer(self):
        batch = {}
        last_flush = time.time()

        while self.running:
            try:
                # Collect writes for batching
                key, value = self.write_queue.get(timeout=1)
                batch[key] = value

                # Flush batch periodically or when it's large enough
                if (len(batch) >= 10 or
                    time.time() - last_flush > self.flush_interval):
                    self._flush_batch(batch)
                    batch.clear()
                    last_flush = time.time()

            except queue.Empty:
                # Flush any remaining items
                if batch:
                    self._flush_batch(batch)
                    batch.clear()
                    last_flush = time.time()

    def _flush_batch(self, batch):
        for key, value in batch.items():
            self.database.set(key, value)
            self.dirty_keys.discard(key)

# Usage
cache = WriteBehindCache(database, flush_interval=5)
cache.set("user:123", user_data)  # Returns immediately
# Database updated within 5 seconds in background
```

**Pros:**
- ✅ Lowest write latency
- ✅ Can batch database writes
- ✅ Good for write-heavy applications

**Cons:**
- ❌ Data loss risk if cache fails
- ❌ Complex implementation
- ❌ Eventual consistency only

**Best for:** High write volume applications where some data loss is acceptable

### 5. Refresh-Ahead Cache

Proactively refreshes cache before expiration.

```python
import threading
import time

class RefreshAheadCache:
    def __init__(self, database, refresh_threshold=0.8):
        self.cache_data = {}
        self.expiry_times = {}
        self.database = database
        self.refresh_threshold = refresh_threshold

    def get(self, key):
        if key in self.cache_data:
            # Check if refresh is needed
            if self._should_refresh(key):
                # Refresh in background
                threading.Thread(target=self._refresh_key, args=(key,)).start()

            return self.cache_data[key]

        # Cache miss - load immediately
        value = self.database.get(key)
        if value:
            self.set(key, value, ttl=300)  # 5 minutes
        return value

    def set(self, key, value, ttl):
        self.cache_data[key] = value
        self.expiry_times[key] = time.time() + ttl

    def _should_refresh(self, key):
        if key not in self.expiry_times:
            return False

        expiry_time = self.expiry_times[key]
        current_time = time.time()
        time_to_expiry = expiry_time - current_time
        total_ttl = expiry_time - (current_time - time_to_expiry)

        # Refresh when 80% of TTL has passed
        return (time_to_expiry / total_ttl) < (1 - self.refresh_threshold)

    def _refresh_key(self, key):
        # Background refresh
        new_value = self.database.get(key)
        if new_value:
            self.set(key, new_value, ttl=300)
```

**Best for:** Applications with predictable access patterns and strict latency requirements

## 🚮 Cache Eviction Policies

### 1. LRU (Least Recently Used)

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, key, value):
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.capacity:
                # Remove least recently used (first item)
                self.cache.popitem(last=False)

        self.cache[key] = value

# Usage
cache = LRUCache(capacity=3)
cache.put("a", 1)
cache.put("b", 2)
cache.put("c", 3)
cache.put("d", 4)  # "a" gets evicted
```

**Best for:** General-purpose caching with good temporal locality

### 2. LFU (Least Frequently Used)

```python
from collections import defaultdict

class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.frequencies = defaultdict(int)
        self.min_frequency = 0
        self.frequency_groups = defaultdict(list)

    def get(self, key):
        if key not in self.cache:
            return None

        # Increment frequency
        self._increment_frequency(key)
        return self.cache[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return

        if key in self.cache:
            self.cache[key] = value
            self._increment_frequency(key)
            return

        if len(self.cache) >= self.capacity:
            self._evict_lfu()

        # Add new key
        self.cache[key] = value
        self.frequencies[key] = 1
        self.frequency_groups[1].append(key)
        self.min_frequency = 1

    def _increment_frequency(self, key):
        freq = self.frequencies[key]
        self.frequencies[key] = freq + 1

        # Remove from current frequency group
        self.frequency_groups[freq].remove(key)

        # Add to new frequency group
        self.frequency_groups[freq + 1].append(key)

        # Update min_frequency if needed
        if freq == self.min_frequency and not self.frequency_groups[freq]:
            self.min_frequency += 1

    def _evict_lfu(self):
        # Remove least frequently used key
        lfu_key = self.frequency_groups[self.min_frequency].pop(0)
        del self.cache[lfu_key]
        del self.frequencies[lfu_key]
```

**Best for:** Applications where access frequency matters more than recency

### 3. TTL (Time To Live)

```python
import time
import threading

class TTLCache:
    def __init__(self):
        self.cache = {}
        self.expiry_times = {}
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            if key in self.expiry_times:
                if time.time() > self.expiry_times[key]:
                    # Expired
                    del self.cache[key]
                    del self.expiry_times[key]
                    return None

            return self.cache.get(key)

    def put(self, key, value, ttl_seconds):
        with self.lock:
            self.cache[key] = value
            self.expiry_times[key] = time.time() + ttl_seconds

    def cleanup_expired(self):
        """Background cleanup of expired entries"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, expiry in self.expiry_times.items()
                if current_time > expiry
            ]

            for key in expired_keys:
                del self.cache[key]
                del self.expiry_times[key]
```

**Best for:** Time-sensitive data that becomes stale after a specific period

## 🌐 Distributed Caching

### Cache Partitioning Strategies

#### 1. Simple Hash Partitioning

```python
import hashlib

class DistributedCache:
    def __init__(self, cache_nodes):
        self.cache_nodes = cache_nodes

    def _get_node(self, key):
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        node_index = hash_value % len(self.cache_nodes)
        return self.cache_nodes[node_index]

    def get(self, key):
        node = self._get_node(key)
        return node.get(key)

    def set(self, key, value, ttl=None):
        node = self._get_node(key)
        return node.set(key, value, ttl)

# Usage
cache_nodes = [RedisNode("redis1:6379"), RedisNode("redis2:6379")]
distributed_cache = DistributedCache(cache_nodes)
```

#### 2. Consistent Hashing

```python
import hashlib
import bisect

class ConsistentHashCache:
    def __init__(self, nodes, replicas=150):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []

        for node in nodes:
            self.add_node(node)

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node.name}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)

    def remove_node(self, node):
        for i in range(self.replicas):
            key = self._hash(f"{node.name}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, key):
        if not self.ring:
            return None

        hash_key = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, hash_key)

        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]

    def get(self, key):
        node = self.get_node(key)
        return node.get(key) if node else None

    def set(self, key, value, ttl=None):
        node = self.get_node(key)
        return node.set(key, value, ttl) if node else False
```

### Redis Cluster Example

```python
import redis
from rediscluster import RedisCluster

class RedisClusterCache:
    def __init__(self, startup_nodes):
        self.client = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            skip_full_coverage_check=True
        )

    def get(self, key):
        try:
            return self.client.get(key)
        except redis.RedisError:
            return None

    def set(self, key, value, ttl=None):
        try:
            if ttl:
                return self.client.setex(key, ttl, value)
            else:
                return self.client.set(key, value)
        except redis.RedisError:
            return False

    def delete(self, key):
        try:
            return self.client.delete(key)
        except redis.RedisError:
            return False

# Usage
startup_nodes = [
    {"host": "127.0.0.1", "port": "7000"},
    {"host": "127.0.0.1", "port": "7001"},
    {"host": "127.0.0.1", "port": "7002"}
]

cache = RedisClusterCache(startup_nodes)
cache.set("user:123", user_data, ttl=3600)
```

## 🎯 Cache Design Patterns

### 1. Multi-Level Caching

```python
class MultiLevelCache:
    def __init__(self, l1_cache, l2_cache, database):
        self.l1_cache = l1_cache  # Fast, small (in-memory)
        self.l2_cache = l2_cache  # Slower, larger (Redis)
        self.database = database

    def get(self, key):
        # Try L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            return value

        # Try L2 cache
        value = self.l2_cache.get(key)
        if value is not None:
            # Promote to L1 cache
            self.l1_cache.set(key, value, ttl=300)
            return value

        # Cache miss - get from database
        value = self.database.get(key)
        if value is not None:
            # Store in both cache levels
            self.l1_cache.set(key, value, ttl=300)
            self.l2_cache.set(key, value, ttl=3600)

        return value

    def set(self, key, value):
        # Write to database
        self.database.set(key, value)

        # Update both cache levels
        self.l1_cache.set(key, value, ttl=300)
        self.l2_cache.set(key, value, ttl=3600)
```

### 2. Cache Warming

```python
class CacheWarmer:
    def __init__(self, cache, database):
        self.cache = cache
        self.database = database

    def warm_popular_data(self):
        """Pre-load frequently accessed data"""
        popular_keys = self.database.get_popular_keys(limit=1000)

        for key in popular_keys:
            if not self.cache.get(key):
                value = self.database.get(key)
                if value:
                    self.cache.set(key, value, ttl=3600)

    def warm_predictive_data(self, user_id):
        """Pre-load data user is likely to access"""
        # Example: warm friend's profiles for social media
        friend_ids = self.database.get_friend_ids(user_id)

        for friend_id in friend_ids[:10]:  # Top 10 friends
            cache_key = f"user:{friend_id}"
            if not self.cache.get(cache_key):
                friend_data = self.database.get_user(friend_id)
                if friend_data:
                    self.cache.set(cache_key, friend_data, ttl=1800)
```

## ⚡ Performance Optimization

### Cache Performance Metrics

```python
import time
from collections import defaultdict

class CacheMetrics:
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
        self.response_times = []
        self.key_frequencies = defaultdict(int)

    def record_hit(self, key, response_time):
        self.hits += 1
        self.total_requests += 1
        self.response_times.append(response_time)
        self.key_frequencies[key] += 1

    def record_miss(self, key, response_time):
        self.misses += 1
        self.total_requests += 1
        self.response_times.append(response_time)
        self.key_frequencies[key] += 1

    def get_hit_ratio(self):
        if self.total_requests == 0:
            return 0
        return self.hits / self.total_requests

    def get_average_response_time(self):
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)

    def get_popular_keys(self, limit=10):
        return sorted(
            self.key_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

# Usage with cache
class MonitoredCache:
    def __init__(self, cache):
        self.cache = cache
        self.metrics = CacheMetrics()

    def get(self, key):
        start_time = time.time()
        value = self.cache.get(key)
        response_time = time.time() - start_time

        if value is not None:
            self.metrics.record_hit(key, response_time)
        else:
            self.metrics.record_miss(key, response_time)

        return value
```

## 🛠️ Practical Implementation Tips

### 1. Cache Size Optimization

```python
def calculate_optimal_cache_size(total_memory_mb, hit_ratio_target=0.8):
    """
    Calculate optimal cache size based on available memory and target hit ratio
    """
    # Rule of thumb: 60-80% of available memory for cache
    max_cache_memory = total_memory_mb * 0.7

    # Estimate based on working set size
    # For web applications, typically 20% of data is accessed 80% of the time
    working_set_ratio = 0.2

    recommended_size = max_cache_memory * working_set_ratio

    return {
        'max_memory_mb': max_cache_memory,
        'recommended_mb': recommended_size,
        'expected_hit_ratio': hit_ratio_target
    }

# Example
result = calculate_optimal_cache_size(16000)  # 16GB RAM
print(f"Recommended cache size: {result['recommended_mb']}MB")
```

### 2. Cache Key Design

```python
class CacheKeyManager:
    @staticmethod
    def user_profile(user_id):
        return f"user:profile:{user_id}"

    @staticmethod
    def user_friends(user_id, page=1):
        return f"user:friends:{user_id}:page:{page}"

    @staticmethod
    def post_data(post_id):
        return f"post:{post_id}"

    @staticmethod
    def trending_posts(category, limit=10):
        return f"trending:posts:{category}:limit:{limit}"

    @staticmethod
    def search_results(query, filters_hash):
        # Hash filters to create consistent key
        return f"search:{hashlib.md5(query.encode()).hexdigest()}:{filters_hash}"

# Usage
cache_key = CacheKeyManager.user_profile(12345)
user_data = cache.get(cache_key)
```

## ✅ Knowledge Check

After studying this section, you should be able to:

- [ ] Choose the appropriate caching pattern for different scenarios
- [ ] Design cache eviction policies based on access patterns
- [ ] Implement distributed caching with proper partitioning
- [ ] Calculate cache hit ratios and performance metrics
- [ ] Design multi-level caching architectures

## 🔄 Quick Review Questions

1. **When would you use Write-Behind over Write-Through caching?**
2. **What's the difference between LRU and LFU eviction policies?**
3. **How does consistent hashing help with distributed caching?**
4. **What are the trade-offs of client-side vs server-side caching?**
5. **How do you handle cache invalidation in a distributed system?**

## 🚀 Next Steps

- Study [Database Concepts](database-concepts.md) to understand cache-database relationships
- Learn [Reliability and Availability](reliability-and-availability.md) for fault-tolerant caching
- Practice implementing caching in [Real-World Examples](../04-real-world-examples/)

---

**Remember**: Caching is not a silver bullet. Always measure performance before and after implementing caching, and consider the complexity it adds to your system!