# Caching Technologies and Tools 🟡

## 🎯 Learning Objectives
- Compare different caching technologies and their use cases
- Understand implementation details of popular caching solutions
- Design distributed caching architectures
- Choose the right caching tool for specific scenarios

## 🗄️ In-Memory Caching Solutions

### Redis - The Swiss Army Knife

**Redis** (Remote Dictionary Server) is an in-memory data structure store used as database, cache, and message broker.

#### Key Features:
- **Data Types**: Strings, Hashes, Lists, Sets, Sorted Sets, Bitmaps, HyperLogLogs
- **Persistence**: RDB snapshots and AOF (Append Only File)
- **Clustering**: Built-in sharding and replication
- **Pub/Sub**: Message broker capabilities
- **Lua Scripting**: Server-side scripting support

#### Redis Implementation Examples:

```python
import redis
import json
import time
from typing import Optional, Any

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0, decode_responses=True):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError):
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized_value = json.dumps(value)
            return self.client.setex(key, ttl, serialized_value)
        except (redis.RedisError, TypeError):
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.client.delete(key))
        except redis.RedisError:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.client.exists(key))
        except redis.RedisError:
            return False

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        try:
            return self.client.incrby(key, amount)
        except redis.RedisError:
            return None

    def hash_set(self, name: str, key: str, value: Any) -> bool:
        """Set hash field"""
        try:
            serialized_value = json.dumps(value)
            return bool(self.client.hset(name, key, serialized_value))
        except (redis.RedisError, TypeError):
            return False

    def hash_get(self, name: str, key: str) -> Optional[Any]:
        """Get hash field"""
        try:
            value = self.client.hget(name, key)
            if value:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError):
            return None

    def list_push(self, name: str, *values: Any) -> Optional[int]:
        """Push to list"""
        try:
            serialized_values = [json.dumps(v) for v in values]
            return self.client.rpush(name, *serialized_values)
        except (redis.RedisError, TypeError):
            return None

    def list_pop(self, name: str) -> Optional[Any]:
        """Pop from list"""
        try:
            value = self.client.lpop(name)
            if value:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError):
            return None

# Usage Examples
cache = RedisCache()

# Basic caching
user_data = {"id": 123, "name": "John Doe", "email": "john@example.com"}
cache.set("user:123", user_data, ttl=1800)  # 30 minutes

retrieved_user = cache.get("user:123")
print(f"Retrieved user: {retrieved_user}")

# Counter example
cache.increment("page_views:home")
views = cache.get("page_views:home")
print(f"Home page views: {views}")

# Hash example (user sessions)
session_data = {"last_login": time.time(), "ip": "192.168.1.1"}
cache.hash_set("sessions", "user:123", session_data)

session = cache.hash_get("sessions", "user:123")
print(f"Session data: {session}")

# List example (recent activities)
cache.list_push("recent_activities:123", "logged_in", "viewed_profile", "updated_settings")
recent_activity = cache.list_pop("recent_activities:123")
print(f"Most recent activity: {recent_activity}")
```

#### Redis Cluster Configuration:

```python
from rediscluster import RedisCluster

class RedisClusterCache:
    def __init__(self, startup_nodes):
        self.client = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            skip_full_coverage_check=True,
            max_connections=20
        )

    def get_with_fallback(self, key: str, fallback_func=None) -> Optional[Any]:
        """Get with fallback to compute function"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)

            if fallback_func:
                computed_value = fallback_func()
                self.set(key, computed_value)
                return computed_value

            return None
        except Exception as e:
            print(f"Cache error: {e}")
            if fallback_func:
                return fallback_func()
            return None

# Cluster setup
startup_nodes = [
    {"host": "127.0.0.1", "port": "7000"},
    {"host": "127.0.0.1", "port": "7001"},
    {"host": "127.0.0.1", "port": "7002"}
]

cluster_cache = RedisClusterCache(startup_nodes)
```

### Memcached - High-Performance Simplicity

**Memcached** is a high-performance, distributed memory object caching system.

#### Key Features:
- **Simple**: Key-value store only
- **Fast**: Extremely low latency
- **Distributed**: Built-in distribution
- **LRU Eviction**: Automatic memory management

```python
import memcache
import json
import hashlib
from typing import Optional, Any, List

class MemcachedCache:
    def __init__(self, servers: List[str] = ['127.0.0.1:11211']):
        self.client = memcache.Client(servers, debug=0)

    def _make_key(self, key: str) -> str:
        """Ensure key is valid for Memcached"""
        if len(key) > 250:
            # Hash long keys
            return hashlib.md5(key.encode()).hexdigest()
        return key.replace(' ', '_')

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            safe_key = self._make_key(key)
            value = self.client.get(safe_key)
            if value:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, Exception):
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache"""
        try:
            safe_key = self._make_key(key)
            serialized_value = json.dumps(value)
            return self.client.set(safe_key, serialized_value, time=ttl)
        except (TypeError, Exception):
            return False

    def get_multi(self, keys: List[str]) -> dict:
        """Get multiple values"""
        try:
            safe_keys = [self._make_key(key) for key in keys]
            results = self.client.get_multi(safe_keys)

            # Convert back to original keys and deserialize
            output = {}
            for original_key, safe_key in zip(keys, safe_keys):
                if safe_key in results:
                    output[original_key] = json.loads(results[safe_key])

            return output
        except Exception:
            return {}

    def set_multi(self, mapping: dict, ttl: int = 3600) -> bool:
        """Set multiple values"""
        try:
            safe_mapping = {}
            for key, value in mapping.items():
                safe_key = self._make_key(key)
                safe_mapping[safe_key] = json.dumps(value)

            return self.client.set_multi(safe_mapping, time=ttl)
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Delete key"""
        try:
            safe_key = self._make_key(key)
            return bool(self.client.delete(safe_key))
        except Exception:
            return False

# Usage
memcached = MemcachedCache(['127.0.0.1:11211', '127.0.0.1:11212'])

# Batch operations for better performance
users = {
    f"user:{i}": {"id": i, "name": f"User {i}"}
    for i in range(1, 6)
}

memcached.set_multi(users)
retrieved_users = memcached.get_multi(list(users.keys()))
print(f"Retrieved {len(retrieved_users)} users")
```

## 🏢 Application-Level Caching

### Local In-Memory Cache

```python
import time
import threading
from typing import Any, Optional, Dict, Tuple
from collections import OrderedDict

class LocalCache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                value, expiry = self.cache[key]

                if time.time() < expiry:
                    # Move to end (LRU)
                    self.cache.move_to_end(key)
                    return value
                else:
                    # Expired
                    del self.cache[key]

            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self.lock:
            if ttl is None:
                ttl = self.default_ttl

            expiry = time.time() + ttl

            if key in self.cache:
                # Update existing
                self.cache[key] = (value, expiry)
                self.cache.move_to_end(key)
            else:
                # Add new
                if len(self.cache) >= self.max_size:
                    # Remove oldest
                    self.cache.popitem(last=False)

                self.cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    def clear(self) -> None:
        with self.lock:
            self.cache.clear()

    def size(self) -> int:
        with self.lock:
            return len(self.cache)

    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if current_time >= expiry
            ]

            for key in expired_keys:
                del self.cache[key]

            return len(expired_keys)

# Auto-cleanup thread
class CacheManager:
    def __init__(self):
        self.local_cache = LocalCache(max_size=5000)
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.running = True
        self.cleanup_thread.start()

    def _cleanup_loop(self):
        while self.running:
            expired_count = self.local_cache.cleanup_expired()
            if expired_count > 0:
                print(f"Cleaned up {expired_count} expired cache entries")
            time.sleep(60)  # Cleanup every minute

    def stop(self):
        self.running = False

# Usage
cache_manager = CacheManager()
cache = cache_manager.local_cache

cache.set("user:123", {"name": "John"}, ttl=300)  # 5 minutes
user = cache.get("user:123")
```

### Multi-Level Cache

```python
class MultiLevelCache:
    def __init__(self, l1_cache, l2_cache, l3_cache=None):
        self.l1 = l1_cache  # Fastest, smallest (local memory)
        self.l2 = l2_cache  # Medium speed, medium size (Redis)
        self.l3 = l3_cache  # Slowest, largest (Database)

        self.stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'l3_hits': 0,
            'misses': 0
        }

    def get(self, key: str) -> Optional[Any]:
        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            self.stats['l1_hits'] += 1
            return value

        # Try L2
        value = self.l2.get(key)
        if value is not None:
            self.stats['l2_hits'] += 1
            # Promote to L1
            self.l1.set(key, value, ttl=300)  # Short TTL for L1
            return value

        # Try L3 if available
        if self.l3:
            value = self.l3.get(key)
            if value is not None:
                self.stats['l3_hits'] += 1
                # Promote to both L1 and L2
                self.l1.set(key, value, ttl=300)
                self.l2.set(key, value, ttl=1800)
                return value

        self.stats['misses'] += 1
        return None

    def set(self, key: str, value: Any) -> None:
        # Set in all levels
        self.l1.set(key, value, ttl=300)
        self.l2.set(key, value, ttl=1800)
        if self.l3:
            self.l3.set(key, value)

    def invalidate(self, key: str) -> None:
        """Remove from all cache levels"""
        self.l1.delete(key)
        self.l2.delete(key)
        if self.l3:
            self.l3.delete(key)

    def get_stats(self) -> dict:
        total_requests = sum(self.stats.values())
        if total_requests == 0:
            return self.stats

        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_ratio': (total_requests - self.stats['misses']) / total_requests,
            'l1_hit_ratio': self.stats['l1_hits'] / total_requests,
            'l2_hit_ratio': self.stats['l2_hits'] / total_requests
        }

# Setup multi-level cache
local_cache = LocalCache(max_size=1000)
redis_cache = RedisCache()

multi_cache = MultiLevelCache(local_cache, redis_cache)

# Usage
multi_cache.set("user:123", {"name": "John", "role": "admin"})
user = multi_cache.get("user:123")  # L1 hit

print(multi_cache.get_stats())
```

## 🌐 CDN and Edge Caching

### CDN Cache Configuration

```python
class CDNConfiguration:
    def __init__(self):
        self.cache_policies = {
            'static_assets': {
                'pattern': r'\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2)$',
                'ttl': 31536000,  # 1 year
                'headers': {
                    'Cache-Control': 'public, max-age=31536000, immutable',
                    'Expires': self._get_future_date(365)
                }
            },
            'api_responses': {
                'pattern': r'^/api/',
                'ttl': 300,  # 5 minutes
                'headers': {
                    'Cache-Control': 'public, max-age=300',
                    'Vary': 'Accept, Authorization'
                }
            },
            'html_pages': {
                'pattern': r'\.html$|^/$',
                'ttl': 3600,  # 1 hour
                'headers': {
                    'Cache-Control': 'public, max-age=3600',
                    'Vary': 'Accept-Encoding'
                }
            }
        }

    def _get_future_date(self, days: int) -> str:
        from datetime import datetime, timedelta
        future_date = datetime.now() + timedelta(days=days)
        return future_date.strftime('%a, %d %b %Y %H:%M:%S GMT')

    def get_cache_policy(self, request_path: str, content_type: str) -> dict:
        import re

        for policy_name, policy in self.cache_policies.items():
            if re.search(policy['pattern'], request_path):
                return policy

        # Default policy
        return {
            'ttl': 0,
            'headers': {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        }

# CDN edge server simulation
class EdgeCache:
    def __init__(self, origin_server_url: str):
        self.origin_server = origin_server_url
        self.cache = LocalCache(max_size=10000)
        self.cdn_config = CDNConfiguration()

    def handle_request(self, request_path: str, headers: dict) -> dict:
        cache_key = self._generate_cache_key(request_path, headers)

        # Check cache first
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return {
                'status': 200,
                'body': cached_response['body'],
                'headers': {
                    **cached_response['headers'],
                    'X-Cache': 'HIT',
                    'X-Cache-Server': 'edge-server-1'
                }
            }

        # Cache miss - fetch from origin
        origin_response = self._fetch_from_origin(request_path, headers)

        # Determine cache policy
        policy = self.cdn_config.get_cache_policy(request_path,
                                                 origin_response.get('content_type', ''))

        # Cache if policy allows
        if policy['ttl'] > 0:
            self.cache.set(cache_key, {
                'body': origin_response['body'],
                'headers': origin_response['headers']
            }, ttl=policy['ttl'])

        return {
            'status': origin_response['status'],
            'body': origin_response['body'],
            'headers': {
                **origin_response['headers'],
                **policy['headers'],
                'X-Cache': 'MISS',
                'X-Cache-Server': 'edge-server-1'
            }
        }

    def _generate_cache_key(self, path: str, headers: dict) -> str:
        # Include relevant headers in cache key
        key_parts = [path]

        # Include vary headers
        if 'Accept-Encoding' in headers:
            key_parts.append(f"encoding:{headers['Accept-Encoding']}")
        if 'Accept' in headers:
            key_parts.append(f"accept:{headers['Accept']}")

        return ':'.join(key_parts)

    def _fetch_from_origin(self, path: str, headers: dict) -> dict:
        # Simulate origin server fetch
        # In real implementation, this would be an HTTP request
        return {
            'status': 200,
            'body': f'Content for {path}',
            'headers': {'Content-Type': 'text/html'},
            'content_type': 'text/html'
        }

# Usage
edge_server = EdgeCache('https://origin.example.com')

response1 = edge_server.handle_request('/index.html', {
    'Accept': 'text/html',
    'Accept-Encoding': 'gzip'
})
print(f"First request: {response1['headers']['X-Cache']}")

response2 = edge_server.handle_request('/index.html', {
    'Accept': 'text/html',
    'Accept-Encoding': 'gzip'
})
print(f"Second request: {response2['headers']['X-Cache']}")
```

## 🔄 Cache Invalidation Strategies

```python
import time
import threading
from typing import Set, Dict, List
from dataclasses import dataclass

@dataclass
class InvalidationEvent:
    event_type: str  # 'create', 'update', 'delete'
    resource_type: str  # 'user', 'post', 'comment'
    resource_id: str
    timestamp: float
    related_keys: List[str]

class CacheInvalidationManager:
    def __init__(self, cache_client):
        self.cache = cache_client
        self.tag_mappings: Dict[str, Set[str]] = {}  # tag -> set of cache keys
        self.key_tags: Dict[str, Set[str]] = {}      # cache key -> set of tags
        self.lock = threading.RLock()

    def set_with_tags(self, key: str, value: Any, tags: List[str], ttl: int = 3600):
        """Set cache value with associated tags for invalidation"""
        with self.lock:
            # Set in cache
            self.cache.set(key, value, ttl)

            # Update tag mappings
            self.key_tags[key] = set(tags)
            for tag in tags:
                if tag not in self.tag_mappings:
                    self.tag_mappings[tag] = set()
                self.tag_mappings[tag].add(key)

    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all cache entries with a specific tag"""
        with self.lock:
            if tag not in self.tag_mappings:
                return 0

            keys_to_invalidate = self.tag_mappings[tag].copy()
            invalidated_count = 0

            for key in keys_to_invalidate:
                if self.cache.delete(key):
                    invalidated_count += 1

                # Remove from mappings
                if key in self.key_tags:
                    for key_tag in self.key_tags[key]:
                        if key_tag in self.tag_mappings:
                            self.tag_mappings[key_tag].discard(key)
                    del self.key_tags[key]

            # Clean up empty tag mapping
            if not self.tag_mappings[tag]:
                del self.tag_mappings[tag]

            return invalidated_count

    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern"""
        # This would require cache backend support for pattern matching
        # Redis supports this with SCAN command
        if hasattr(self.cache, 'scan_iter'):
            deleted_count = 0
            for key in self.cache.scan_iter(match=pattern):
                if self.cache.delete(key):
                    deleted_count += 1
            return deleted_count
        return 0

    def handle_data_change(self, event: InvalidationEvent):
        """Handle data change events and invalidate related cache entries"""
        tags_to_invalidate = []

        if event.resource_type == 'user':
            tags_to_invalidate.extend([
                f"user:{event.resource_id}",
                "user_list",
                f"user_profile:{event.resource_id}"
            ])
        elif event.resource_type == 'post':
            tags_to_invalidate.extend([
                f"post:{event.resource_id}",
                "post_list",
                "trending_posts"
            ])
        elif event.resource_type == 'comment':
            tags_to_invalidate.extend([
                f"comment:{event.resource_id}",
                f"post_comments:{event.resource_id}",
                "recent_comments"
            ])

        # Add any explicitly related keys
        if event.related_keys:
            for key in event.related_keys:
                self.cache.delete(key)

        # Invalidate by tags
        total_invalidated = 0
        for tag in tags_to_invalidate:
            total_invalidated += self.invalidate_by_tag(tag)

        print(f"Invalidated {total_invalidated} cache entries for {event.resource_type}:{event.resource_id}")

# Database change listener simulation
class DatabaseChangeListener:
    def __init__(self, invalidation_manager: CacheInvalidationManager):
        self.invalidation_manager = invalidation_manager
        self.running = True
        self.event_queue = []
        self.lock = threading.Lock()

        # Start processing thread
        self.processor_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processor_thread.start()

    def on_data_change(self, resource_type: str, resource_id: str,
                      event_type: str, related_keys: List[str] = None):
        """Called when data changes in the database"""
        event = InvalidationEvent(
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=time.time(),
            related_keys=related_keys or []
        )

        with self.lock:
            self.event_queue.append(event)

    def _process_events(self):
        """Process invalidation events"""
        while self.running:
            events_to_process = []

            with self.lock:
                events_to_process = self.event_queue.copy()
                self.event_queue.clear()

            for event in events_to_process:
                self.invalidation_manager.handle_data_change(event)

            time.sleep(0.1)  # Small delay

# Usage example
cache = RedisCache()
invalidation_manager = CacheInvalidationManager(cache)
change_listener = DatabaseChangeListener(invalidation_manager)

# Cache some data with tags
invalidation_manager.set_with_tags(
    "user:123:profile",
    {"name": "John", "email": "john@example.com"},
    tags=["user:123", "user_list", "user_profile:123"]
)

invalidation_manager.set_with_tags(
    "user:123:posts",
    [{"id": 1, "title": "My Post"}],
    tags=["user:123", "post_list"]
)

# Simulate data change
change_listener.on_data_change("user", "123", "update")  # Invalidates related cache
```

## 📊 Cache Monitoring and Analytics

```python
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class CacheMetric:
    timestamp: float
    operation: str  # 'get', 'set', 'delete'
    key: str
    hit: bool
    response_time_ms: float
    cache_level: str  # 'L1', 'L2', 'L3'

class CacheAnalytics:
    def __init__(self, window_size: int = 1000):
        self.metrics: deque = deque(maxsize=window_size)
        self.hourly_stats = defaultdict(lambda: defaultdict(int))
        self.lock = threading.Lock()

    def record_metric(self, metric: CacheMetric):
        with self.lock:
            self.metrics.append(metric)

            # Update hourly stats
            hour_key = int(metric.timestamp // 3600)
            stats = self.hourly_stats[hour_key]

            stats['total_operations'] += 1
            stats[f'{metric.operation}_count'] += 1

            if metric.operation == 'get':
                if metric.hit:
                    stats['hits'] += 1
                else:
                    stats['misses'] += 1

                stats['total_response_time'] += metric.response_time_ms

    def get_current_stats(self) -> Dict:
        with self.lock:
            if not self.metrics:
                return {}

            recent_metrics = list(self.metrics)
            total_ops = len(recent_metrics)

            get_ops = [m for m in recent_metrics if m.operation == 'get']
            hits = [m for m in get_ops if m.hit]

            hit_ratio = len(hits) / len(get_ops) if get_ops else 0
            avg_response_time = sum(m.response_time_ms for m in get_ops) / len(get_ops) if get_ops else 0

            # Cache level distribution
            level_stats = defaultdict(int)
            for metric in recent_metrics:
                level_stats[metric.cache_level] += 1

            return {
                'total_operations': total_ops,
                'hit_ratio': hit_ratio,
                'avg_response_time_ms': avg_response_time,
                'cache_level_distribution': dict(level_stats),
                'operations_per_second': total_ops / (time.time() - recent_metrics[0].timestamp) if recent_metrics else 0
            }

    def get_hourly_report(self, hours_back: int = 24) -> List[Dict]:
        current_hour = int(time.time() // 3600)
        report = []

        for i in range(hours_back):
            hour_key = current_hour - i
            stats = self.hourly_stats.get(hour_key, {})

            if stats:
                hit_ratio = stats['hits'] / (stats['hits'] + stats['misses']) if (stats['hits'] + stats['misses']) > 0 else 0
                avg_response_time = stats['total_response_time'] / stats['get_count'] if stats['get_count'] > 0 else 0

                report.append({
                    'hour': hour_key,
                    'timestamp': hour_key * 3600,
                    'total_operations': stats['total_operations'],
                    'hit_ratio': hit_ratio,
                    'avg_response_time_ms': avg_response_time,
                    'gets': stats['get_count'],
                    'sets': stats['set_count'],
                    'deletes': stats['delete_count']
                })

        return report

class MonitoredCache:
    def __init__(self, cache_client, analytics: CacheAnalytics, cache_level: str = 'L1'):
        self.cache = cache_client
        self.analytics = analytics
        self.cache_level = cache_level

    def get(self, key: str) -> Optional[Any]:
        start_time = time.time()
        value = self.cache.get(key)
        response_time = (time.time() - start_time) * 1000  # Convert to ms

        self.analytics.record_metric(CacheMetric(
            timestamp=time.time(),
            operation='get',
            key=key,
            hit=value is not None,
            response_time_ms=response_time,
            cache_level=self.cache_level
        ))

        return value

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        start_time = time.time()
        result = self.cache.set(key, value, ttl)
        response_time = (time.time() - start_time) * 1000

        self.analytics.record_metric(CacheMetric(
            timestamp=time.time(),
            operation='set',
            key=key,
            hit=True,  # Set operations don't have hits/misses
            response_time_ms=response_time,
            cache_level=self.cache_level
        ))

        return result

    def delete(self, key: str) -> bool:
        start_time = time.time()
        result = self.cache.delete(key)
        response_time = (time.time() - start_time) * 1000

        self.analytics.record_metric(CacheMetric(
            timestamp=time.time(),
            operation='delete',
            key=key,
            hit=True,
            response_time_ms=response_time,
            cache_level=self.cache_level
        ))

        return result

# Usage
analytics = CacheAnalytics(window_size=10000)
monitored_cache = MonitoredCache(RedisCache(), analytics, 'Redis')

# Simulate some operations
for i in range(100):
    monitored_cache.set(f"key:{i}", f"value:{i}")

for i in range(150):  # Some cache misses
    monitored_cache.get(f"key:{i}")

# Get analytics
current_stats = analytics.get_current_stats()
print(f"Hit ratio: {current_stats['hit_ratio']:.2%}")
print(f"Average response time: {current_stats['avg_response_time_ms']:.2f}ms")
print(f"Operations per second: {current_stats['operations_per_second']:.2f}")
```

## 🛠️ Choosing the Right Caching Solution

### Decision Matrix

| Use Case | Local Memory | Redis | Memcached | CDN | Database Query Cache |
|----------|--------------|-------|-----------|-----|-------------------|
| **Session Storage** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Static Assets** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Database Query Results** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Real-time Data** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Cross-server Sharing** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Complex Data Structures** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Pub/Sub Messaging** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Geographic Distribution** | ❌ | ✅ | ✅ | ✅ | ❌ |

### Performance Characteristics

```python
class CachePerformanceComparison:
    @staticmethod
    def latency_comparison():
        return {
            'Local Memory': '0.01ms',
            'Redis (same datacenter)': '0.1-1ms',
            'Redis (cross-region)': '50-200ms',
            'Memcached (same datacenter)': '0.1-1ms',
            'CDN Edge': '10-50ms',
            'Database Query Cache': '1-10ms'
        }

    @staticmethod
    def throughput_comparison():
        return {
            'Local Memory': '1M+ ops/sec',
            'Redis': '100K-1M ops/sec',
            'Memcached': '500K+ ops/sec',
            'CDN': '10K-100K requests/sec',
            'Database Cache': '1K-10K queries/sec'
        }

    @staticmethod
    def scalability_comparison():
        return {
            'Local Memory': 'Single server only',
            'Redis': 'Cluster: 1000+ nodes',
            'Memcached': 'Distributed: unlimited',
            'CDN': 'Global: 100+ edge locations',
            'Database Cache': 'Per database instance'
        }

# Usage recommendations
def recommend_cache_solution(requirements: dict) -> str:
    score = {
        'local': 0,
        'redis': 0,
        'memcached': 0,
        'cdn': 0,
        'db_cache': 0
    }

    # Latency requirements
    if requirements.get('ultra_low_latency', False):
        score['local'] += 3
        score['redis'] += 2
        score['memcached'] += 2

    # Persistence requirements
    if requirements.get('persistence', False):
        score['redis'] += 3
        score['db_cache'] += 2

    # Distribution requirements
    if requirements.get('distributed', False):
        score['redis'] += 3
        score['memcached'] += 3
        score['cdn'] += 2

    # Data structure complexity
    if requirements.get('complex_data', False):
        score['redis'] += 3
        score['local'] += 2

    # Static content
    if requirements.get('static_content', False):
        score['cdn'] += 3

    # Geographic distribution
    if requirements.get('global', False):
        score['cdn'] += 3
        score['redis'] += 1

    best_solution = max(score, key=score.get)
    return best_solution

# Example usage
requirements = {
    'ultra_low_latency': True,
    'distributed': True,
    'complex_data': True,
    'persistence': False,
    'static_content': False,
    'global': False
}

recommendation = recommend_cache_solution(requirements)
print(f"Recommended solution: {recommendation}")
```

## ✅ Knowledge Check

After studying this section, you should be able to:

- [ ] Choose appropriate caching technology for specific use cases
- [ ] Configure Redis and Memcached for production use
- [ ] Implement cache invalidation strategies
- [ ] Design multi-level caching architectures
- [ ] Monitor and analyze cache performance
- [ ] Optimize cache hit ratios and response times

## 🔄 Next Steps

- Study [Message Queues](../message-queues/) for async processing patterns
- Learn [Database Technologies](../databases/) for data layer optimization
- Explore [Monitoring](../monitoring/) tools for cache observability
- Practice implementing caching in [Real-World Examples](../../04-real-world-examples/)