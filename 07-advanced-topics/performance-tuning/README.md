# Performance Tuning and Optimization 🔴

## 🎯 Learning Objectives
- Master performance analysis and bottleneck identification
- Learn optimization techniques for different system layers
- Understand profiling tools and performance monitoring
- Implement caching strategies and database optimizations

## 📊 Performance Analysis Framework

### 1. Performance Metrics and Monitoring

```python
import time
import threading
import psutil
import statistics
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
import queue
import functools

@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class LatencyMeasurement:
    operation: str
    duration_ms: float
    timestamp: float
    success: bool = True
    tags: Dict[str, str] = field(default_factory=dict)

class PerformanceMonitor:
    """
    Comprehensive performance monitoring system
    """

    def __init__(self, collection_interval: float = 1.0):
        self.collection_interval = collection_interval
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.latency_measurements: deque = deque(maxlen=10000)
        self.system_metrics: deque = deque(maxlen=1000)
        self.running = False
        self.lock = threading.RLock()

        # Performance counters
        self.request_count = 0
        self.error_count = 0
        self.total_processing_time = 0.0

    def start_monitoring(self):
        """Start background monitoring"""
        self.running = True
        thread = threading.Thread(target=self._collect_system_metrics, daemon=True)
        thread.start()

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.running = False

    def record_metric(self, name: str, value: float, unit: str = "", tags: Dict[str, str] = None):
        """Record a custom metric"""
        with self.lock:
            metric = PerformanceMetric(name, value, unit, time.time(), tags or {})
            self.metrics[name].append(metric)

    def record_latency(self, operation: str, duration_ms: float, success: bool = True, tags: Dict[str, str] = None):
        """Record latency measurement"""
        with self.lock:
            measurement = LatencyMeasurement(operation, duration_ms, time.time(), success, tags or {})
            self.latency_measurements.append(measurement)

    def measure_execution_time(self, operation_name: str, tags: Dict[str, str] = None):
        """Decorator to measure function execution time"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    raise e
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    self.record_latency(operation_name, duration_ms, success, tags)

                    with self.lock:
                        self.request_count += 1
                        self.total_processing_time += duration_ms
                        if not success:
                            self.error_count += 1

            return wrapper
        return decorator

    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        while self.running:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                cpu_count = psutil.cpu_count()

                # Memory metrics
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_available = memory.available / (1024**3)  # GB

                # Disk metrics
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent

                # Network metrics (if available)
                try:
                    network = psutil.net_io_counters()
                    bytes_sent = network.bytes_sent
                    bytes_recv = network.bytes_recv
                except:
                    bytes_sent = bytes_recv = 0

                timestamp = time.time()
                system_metric = {
                    'timestamp': timestamp,
                    'cpu_percent': cpu_percent,
                    'cpu_count': cpu_count,
                    'memory_percent': memory_percent,
                    'memory_available_gb': memory_available,
                    'disk_percent': disk_percent,
                    'network_bytes_sent': bytes_sent,
                    'network_bytes_recv': bytes_recv
                }

                with self.lock:
                    self.system_metrics.append(system_metric)

            except Exception as e:
                print(f"Error collecting system metrics: {e}")

            time.sleep(self.collection_interval)

    def get_latency_percentiles(self, operation: str = None, time_window: float = 300) -> Dict[str, float]:
        """Get latency percentiles for operations"""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - time_window

            # Filter measurements
            measurements = [
                m for m in self.latency_measurements
                if m.timestamp >= cutoff_time and (operation is None or m.operation == operation)
            ]

            if not measurements:
                return {}

            durations = [m.duration_ms for m in measurements]
            durations.sort()

            return {
                'p50': statistics.median(durations),
                'p90': durations[int(0.9 * len(durations))] if durations else 0,
                'p95': durations[int(0.95 * len(durations))] if durations else 0,
                'p99': durations[int(0.99 * len(durations))] if durations else 0,
                'min': min(durations),
                'max': max(durations),
                'avg': statistics.mean(durations),
                'count': len(durations)
            }

    def get_throughput_metrics(self, time_window: float = 300) -> Dict[str, float]:
        """Get throughput metrics"""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - time_window

            # Count requests in time window
            recent_requests = [
                m for m in self.latency_measurements
                if m.timestamp >= cutoff_time
            ]

            if not recent_requests:
                return {'requests_per_second': 0, 'error_rate': 0}

            requests_per_second = len(recent_requests) / time_window
            error_count = sum(1 for m in recent_requests if not m.success)
            error_rate = error_count / len(recent_requests) if recent_requests else 0

            return {
                'requests_per_second': requests_per_second,
                'error_rate': error_rate,
                'total_requests': len(recent_requests),
                'total_errors': error_count
            }

    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        with self.lock:
            if not self.system_metrics:
                return {}

            latest = self.system_metrics[-1]

            # Calculate trends if we have enough data
            if len(self.system_metrics) >= 10:
                recent_cpu = [m['cpu_percent'] for m in list(self.system_metrics)[-10:]]
                recent_memory = [m['memory_percent'] for m in list(self.system_metrics)[-10:]]

                cpu_trend = recent_cpu[-1] - recent_cpu[0]
                memory_trend = recent_memory[-1] - recent_memory[0]
            else:
                cpu_trend = memory_trend = 0

            return {
                'current_metrics': latest,
                'trends': {
                    'cpu_trend': cpu_trend,
                    'memory_trend': memory_trend
                },
                'health_score': self._calculate_health_score(latest)
            }

    def _calculate_health_score(self, metrics: Dict) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0

        # Deduct points for high resource usage
        if metrics['cpu_percent'] > 80:
            score -= 20
        elif metrics['cpu_percent'] > 60:
            score -= 10

        if metrics['memory_percent'] > 90:
            score -= 30
        elif metrics['memory_percent'] > 70:
            score -= 15

        if metrics['disk_percent'] > 90:
            score -= 20
        elif metrics['disk_percent'] > 80:
            score -= 10

        return max(0, score)

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            'timestamp': time.time(),
            'latency_metrics': self.get_latency_percentiles(),
            'throughput_metrics': self.get_throughput_metrics(),
            'system_health': self.get_system_health(),
            'operation_breakdown': self._get_operation_breakdown()
        }

    def _get_operation_breakdown(self) -> Dict[str, Dict[str, float]]:
        """Get performance breakdown by operation"""
        operation_stats = defaultdict(list)

        with self.lock:
            for measurement in self.latency_measurements:
                operation_stats[measurement.operation].append(measurement.duration_ms)

        breakdown = {}
        for operation, durations in operation_stats.items():
            if durations:
                breakdown[operation] = {
                    'avg_ms': statistics.mean(durations),
                    'min_ms': min(durations),
                    'max_ms': max(durations),
                    'count': len(durations)
                }

        return breakdown

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
```

### 2. Application-Level Profiling

```python
import cProfile
import pstats
import io
from functools import wraps
import tracemalloc
import linecache
import os

class PerformanceProfiler:
    """
    Application-level performance profiler
    """

    def __init__(self):
        self.profiles = {}
        self.memory_snapshots = {}

    def profile_function(self, func_name: str = None):
        """Decorator to profile function execution"""
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"

            @wraps(func)
            def wrapper(*args, **kwargs):
                # CPU profiling
                profiler = cProfile.Profile()
                profiler.enable()

                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    profiler.disable()

                    # Store profile
                    s = io.StringIO()
                    ps = pstats.Stats(profiler, stream=s)
                    ps.sort_stats('cumulative')
                    ps.print_stats()

                    self.profiles[name] = {
                        'timestamp': time.time(),
                        'profile_data': s.getvalue(),
                        'stats': ps
                    }

            return wrapper
        return decorator

    def start_memory_profiling(self):
        """Start memory profiling"""
        tracemalloc.start()

    def take_memory_snapshot(self, name: str):
        """Take memory snapshot"""
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            self.memory_snapshots[name] = {
                'timestamp': time.time(),
                'snapshot': snapshot
            }

    def compare_memory_snapshots(self, name1: str, name2: str) -> List[str]:
        """Compare two memory snapshots"""
        if name1 not in self.memory_snapshots or name2 not in self.memory_snapshots:
            return []

        snapshot1 = self.memory_snapshots[name1]['snapshot']
        snapshot2 = self.memory_snapshots[name2]['snapshot']

        top_stats = snapshot2.compare_to(snapshot1, 'lineno')

        result = []
        for stat in top_stats[:20]:  # Top 20 differences
            result.append(str(stat))

        return result

    def get_top_memory_consumers(self, snapshot_name: str, top_n: int = 10) -> List[str]:
        """Get top memory consuming lines"""
        if snapshot_name not in self.memory_snapshots:
            return []

        snapshot = self.memory_snapshots[snapshot_name]['snapshot']
        top_stats = snapshot.statistics('lineno')

        result = []
        for stat in top_stats[:top_n]:
            result.append(str(stat))

        return result

    def get_profile_summary(self, func_name: str) -> Dict[str, Any]:
        """Get profile summary for function"""
        if func_name not in self.profiles:
            return {}

        profile_data = self.profiles[func_name]
        stats = profile_data['stats']

        # Extract key statistics
        total_calls = stats.total_calls
        primitive_calls = stats.prim_calls
        total_time = stats.total_tt

        # Get top functions by cumulative time
        s = io.StringIO()
        stats.print_stats(10)
        top_functions = s.getvalue()

        return {
            'timestamp': profile_data['timestamp'],
            'total_calls': total_calls,
            'primitive_calls': primitive_calls,
            'total_time': total_time,
            'top_functions': top_functions
        }

# Performance testing utilities
class LoadTester:
    """
    Simple load testing utility for performance evaluation
    """

    def __init__(self, target_function: Callable, monitor: PerformanceMonitor):
        self.target_function = target_function
        self.monitor = monitor
        self.results = []

    def run_load_test(self, num_requests: int, concurrency: int = 10,
                      request_data: List[Any] = None) -> Dict[str, Any]:
        """Run load test with specified parameters"""
        request_queue = queue.Queue()
        result_queue = queue.Queue()

        # Prepare test data
        test_data = request_data or [{}] * num_requests
        for i, data in enumerate(test_data[:num_requests]):
            request_queue.put((i, data))

        # Worker function
        def worker():
            while True:
                try:
                    request_id, data = request_queue.get_nowait()

                    start_time = time.time()
                    success = True
                    error = None

                    try:
                        if isinstance(data, dict):
                            result = self.target_function(**data)
                        else:
                            result = self.target_function(data)
                    except Exception as e:
                        success = False
                        error = str(e)
                        result = None

                    end_time = time.time()
                    duration_ms = (end_time - start_time) * 1000

                    result_queue.put({
                        'request_id': request_id,
                        'duration_ms': duration_ms,
                        'success': success,
                        'error': error,
                        'timestamp': start_time
                    })

                    # Record in monitor
                    self.monitor.record_latency('load_test', duration_ms, success)

                    request_queue.task_done()

                except queue.Empty:
                    break

        # Start workers
        threads = []
        for _ in range(concurrency):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)

        # Wait for completion
        request_queue.join()
        for thread in threads:
            thread.join()

        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())

        # Calculate statistics
        durations = [r['duration_ms'] for r in results]
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]

        if durations:
            avg_duration = statistics.mean(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            p95_duration = durations[int(0.95 * len(durations))] if len(durations) > 20 else max_duration
        else:
            avg_duration = min_duration = max_duration = p95_duration = 0

        total_time = max([r['timestamp'] for r in results]) - min([r['timestamp'] for r in results]) if results else 0
        requests_per_second = len(results) / total_time if total_time > 0 else 0

        return {
            'total_requests': len(results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / len(results) if results else 0,
            'avg_duration_ms': avg_duration,
            'min_duration_ms': min_duration,
            'max_duration_ms': max_duration,
            'p95_duration_ms': p95_duration,
            'requests_per_second': requests_per_second,
            'total_time_seconds': total_time,
            'errors': [r['error'] for r in failed_requests if r['error']]
        }
```

## 🗄️ Database Performance Optimization

### 1. Query Optimization and Indexing

```python
import sqlite3
import time
from typing import List, Tuple, Dict, Any
import json

class DatabaseOptimizer:
    """
    Database performance optimization utilities
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.query_cache = {}
        self.query_stats = defaultdict(list)
        self.lock = threading.Lock()

    def execute_query(self, query: str, params: Tuple = (), cache_key: str = None) -> List[Dict]:
        """Execute query with performance monitoring"""
        start_time = time.time()

        # Check cache first
        if cache_key and cache_key in self.query_cache:
            cache_hit = True
            result = self.query_cache[cache_key]
        else:
            cache_hit = False
            cursor = self.connection.cursor()
            cursor.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                result = [dict(row) for row in cursor.fetchall()]
                # Cache SELECT queries
                if cache_key:
                    self.query_cache[cache_key] = result
            else:
                result = cursor.rowcount
                self.connection.commit()

        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        # Record query statistics
        with self.lock:
            self.query_stats[query].append({
                'duration_ms': duration_ms,
                'timestamp': start_time,
                'cache_hit': cache_hit,
                'row_count': len(result) if isinstance(result, list) else result
            })

        return result

    def analyze_query_performance(self, query: str) -> Dict[str, Any]:
        """Analyze performance statistics for a query"""
        with self.lock:
            if query not in self.query_stats:
                return {}

            stats = self.query_stats[query]
            durations = [s['duration_ms'] for s in stats]
            cache_hits = sum(1 for s in stats if s['cache_hit'])

            return {
                'total_executions': len(stats),
                'avg_duration_ms': statistics.mean(durations),
                'min_duration_ms': min(durations),
                'max_duration_ms': max(durations),
                'cache_hit_rate': cache_hits / len(stats) if stats else 0,
                'total_cache_hits': cache_hits
            }

    def create_index(self, table: str, columns: List[str], unique: bool = False) -> bool:
        """Create database index"""
        try:
            index_name = f"idx_{table}_{'_'.join(columns)}"
            unique_str = "UNIQUE " if unique else ""
            columns_str = ", ".join(columns)

            query = f"CREATE {unique_str}INDEX {index_name} ON {table} ({columns_str})"
            self.execute_query(query)
            return True
        except sqlite3.Error as e:
            print(f"Error creating index: {e}")
            return False

    def explain_query(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Get query execution plan"""
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        return self.execute_query(explain_query, params)

    def suggest_indexes(self, query: str) -> List[str]:
        """Suggest indexes based on query pattern"""
        suggestions = []

        # Simple heuristics for index suggestions
        query_upper = query.upper()

        # Look for WHERE clauses
        if "WHERE" in query_upper:
            # Extract table and column names (simplified)
            # In a real implementation, use SQL parsing library
            parts = query_upper.split("WHERE")[1].split("AND")
            for part in parts:
                if "=" in part or ">" in part or "<" in part:
                    # Extract column name (very simplified)
                    for op in ["=", ">", "<", ">=", "<=", "LIKE"]:
                        if op in part:
                            column = part.split(op)[0].strip()
                            suggestions.append(f"Consider index on column: {column}")
                            break

        # Look for ORDER BY clauses
        if "ORDER BY" in query_upper:
            order_part = query_upper.split("ORDER BY")[1].split("LIMIT")[0] if "LIMIT" in query_upper else query_upper.split("ORDER BY")[1]
            suggestions.append(f"Consider index for ORDER BY: {order_part.strip()}")

        # Look for JOIN conditions
        if "JOIN" in query_upper:
            suggestions.append("Consider indexes on JOIN columns")

        return suggestions

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get table statistics"""
        try:
            # Row count
            count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = count_result[0]['count'] if count_result else 0

            # Table info
            info_result = self.execute_query(f"PRAGMA table_info({table_name})")
            columns = [row['name'] for row in info_result]

            # Index info
            index_result = self.execute_query(f"PRAGMA index_list({table_name})")
            indexes = [row['name'] for row in index_result]

            return {
                'table_name': table_name,
                'row_count': row_count,
                'column_count': len(columns),
                'columns': columns,
                'indexes': indexes,
                'index_count': len(indexes)
            }
        except sqlite3.Error as e:
            return {'error': str(e)}

# Example usage and testing
class DatabasePerformanceTest:
    """
    Database performance testing scenarios
    """

    def __init__(self):
        self.optimizer = DatabaseOptimizer()
        self.setup_test_data()

    def setup_test_data(self):
        """Setup test database with sample data"""
        # Create users table
        self.optimizer.execute_query("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create orders table
        self.optimizer.execute_query("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product_name TEXT,
                quantity INTEGER,
                price DECIMAL(10,2),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Insert sample data
        import random
        import string

        # Insert users
        for i in range(10000):
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
            email = f"{username}@example.com"
            age = random.randint(18, 80)

            self.optimizer.execute_query(
                "INSERT INTO users (username, email, age) VALUES (?, ?, ?)",
                (username, email, age)
            )

        # Insert orders
        for i in range(50000):
            user_id = random.randint(1, 10000)
            product_name = f"Product_{random.randint(1, 1000)}"
            quantity = random.randint(1, 10)
            price = round(random.uniform(10.0, 500.0), 2)

            self.optimizer.execute_query(
                "INSERT INTO orders (user_id, product_name, quantity, price) VALUES (?, ?, ?, ?)",
                (user_id, product_name, quantity, price)
            )

    def test_query_performance(self):
        """Test various query performance scenarios"""
        test_queries = [
            # Without index
            ("SELECT * FROM users WHERE email = 'user123@example.com'", "email_lookup_no_index"),

            # Range query
            ("SELECT * FROM users WHERE age BETWEEN 25 AND 35", "age_range_no_index"),

            # JOIN query
            ("SELECT u.username, COUNT(o.id) as order_count FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id", "join_query"),

            # ORDER BY query
            ("SELECT * FROM orders ORDER BY price DESC LIMIT 100", "order_by_price")
        ]

        print("Testing query performance without indexes...")
        results_before = {}

        for query, test_name in test_queries:
            start_time = time.time()
            result = self.optimizer.execute_query(query, cache_key=test_name)
            duration = time.time() - start_time
            results_before[test_name] = duration
            print(f"{test_name}: {duration:.3f}s ({len(result) if isinstance(result, list) else result} rows)")

        # Create indexes
        print("\nCreating indexes...")
        self.optimizer.create_index("users", ["email"], unique=True)
        self.optimizer.create_index("users", ["age"])
        self.optimizer.create_index("orders", ["user_id"])
        self.optimizer.create_index("orders", ["price"])

        # Clear cache to test real performance
        self.optimizer.query_cache.clear()

        print("\nTesting query performance with indexes...")
        results_after = {}

        for query, test_name in test_queries:
            start_time = time.time()
            result = self.optimizer.execute_query(query)
            duration = time.time() - start_time
            results_after[test_name] = duration
            print(f"{test_name}: {duration:.3f}s ({len(result) if isinstance(result, list) else result} rows)")

        # Show improvement
        print("\nPerformance improvements:")
        for test_name in results_before:
            before = results_before[test_name]
            after = results_after[test_name]
            improvement = ((before - after) / before) * 100 if before > 0 else 0
            print(f"{test_name}: {improvement:.1f}% faster")

    def analyze_slow_queries(self):
        """Analyze slow queries and suggest optimizations"""
        print("\nAnalyzing query performance...")

        for query, stats_list in self.optimizer.query_stats.items():
            analysis = self.optimizer.analyze_query_performance(query)
            if analysis and analysis['avg_duration_ms'] > 100:  # Queries slower than 100ms
                print(f"\nSlow query detected:")
                print(f"Query: {query[:100]}...")
                print(f"Average duration: {analysis['avg_duration_ms']:.2f}ms")
                print(f"Executions: {analysis['total_executions']}")

                # Get suggestions
                suggestions = self.optimizer.suggest_indexes(query)
                if suggestions:
                    print("Optimization suggestions:")
                    for suggestion in suggestions:
                        print(f"  - {suggestion}")

# Test the database optimization
def test_database_performance():
    """Run database performance tests"""
    print("Starting database performance tests...")

    tester = DatabasePerformanceTest()
    tester.test_query_performance()
    tester.analyze_slow_queries()

if __name__ == "__main__":
    test_database_performance()
```

## 🚀 Caching Optimization Strategies

### 1. Multi-Level Caching System

```python
import hashlib
import pickle
from abc import ABC, abstractmethod
from enum import Enum

class CacheLevel(Enum):
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DATABASE = "l3_database"

class EvictionPolicy(Enum):
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"

@dataclass
class CacheEntry:
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    ttl: Optional[float] = None

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

class CacheInterface(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: float = None) -> bool:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    def clear(self) -> bool:
        pass

class LRUCache(CacheInterface):
    """
    LRU (Least Recently Used) cache implementation
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: deque = deque()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]

                if entry.is_expired():
                    del self.cache[key]
                    self.access_order.remove(key)
                    self.misses += 1
                    return None

                # Move to end (most recently used)
                self.access_order.remove(key)
                self.access_order.append(key)
                entry.access_count += 1
                self.hits += 1
                return entry.value

            self.misses += 1
            return None

    def set(self, key: str, value: Any, ttl: float = None) -> bool:
        with self.lock:
            # Remove if already exists
            if key in self.cache:
                self.access_order.remove(key)

            # Evict if at capacity
            elif len(self.cache) >= self.max_size:
                oldest_key = self.access_order.popleft()
                del self.cache[oldest_key]

            # Add new entry
            entry = CacheEntry(key, value, time.time(), 0, ttl)
            self.cache[key] = entry
            self.access_order.append(key)
            return True

    def delete(self, key: str) -> bool:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.access_order.remove(key)
                return True
            return False

    def clear(self) -> bool:
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            return True

    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0

            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'utilization': len(self.cache) / self.max_size
            }

class MultiLevelCache:
    """
    Multi-level caching system with automatic promotion/demotion
    """

    def __init__(self, l1_size: int = 100, l2_size: int = 1000):
        self.l1_cache = LRUCache(l1_size)  # Fastest, smallest
        self.l2_cache = LRUCache(l2_size)  # Slower, larger
        self.promotion_threshold = 3  # Promote to L1 after 3 L2 hits
        self.access_counts: Dict[str, int] = defaultdict(int)
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            # Try L1 first
            value = self.l1_cache.get(key)
            if value is not None:
                return value

            # Try L2
            value = self.l2_cache.get(key)
            if value is not None:
                self.access_counts[key] += 1

                # Promote to L1 if accessed frequently
                if self.access_counts[key] >= self.promotion_threshold:
                    self.l1_cache.set(key, value)
                    self.access_counts[key] = 0  # Reset counter

                return value

            return None

    def set(self, key: str, value: Any, ttl: float = None) -> bool:
        with self.lock:
            # Set in L2 by default
            success = self.l2_cache.set(key, value, ttl)

            # Reset access count
            self.access_counts[key] = 0

            return success

    def delete(self, key: str) -> bool:
        with self.lock:
            l1_deleted = self.l1_cache.delete(key)
            l2_deleted = self.l2_cache.delete(key)

            if key in self.access_counts:
                del self.access_counts[key]

            return l1_deleted or l2_deleted

    def clear(self) -> bool:
        with self.lock:
            self.l1_cache.clear()
            self.l2_cache.clear()
            self.access_counts.clear()
            return True

    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            return {
                'l1_stats': self.l1_cache.get_stats(),
                'l2_stats': self.l2_cache.get_stats(),
                'promotion_threshold': self.promotion_threshold,
                'pending_promotions': len([k for k, count in self.access_counts.items()
                                         if count >= self.promotion_threshold])
            }

class CacheWarming:
    """
    Cache warming strategies for improved performance
    """

    def __init__(self, cache: CacheInterface, data_loader: Callable[[str], Any]):
        self.cache = cache
        self.data_loader = data_loader
        self.warming_stats = {
            'items_warmed': 0,
            'warming_time': 0.0,
            'errors': 0
        }

    def warm_cache_bulk(self, keys: List[str]) -> Dict[str, Any]:
        """Warm cache with bulk data loading"""
        start_time = time.time()

        for key in keys:
            try:
                value = self.data_loader(key)
                if value is not None:
                    self.cache.set(key, value)
                    self.warming_stats['items_warmed'] += 1
            except Exception as e:
                self.warming_stats['errors'] += 1
                print(f"Error warming cache for key {key}: {e}")

        self.warming_stats['warming_time'] = time.time() - start_time
        return self.warming_stats.copy()

    def warm_cache_predictive(self, pattern_func: Callable[[], List[str]]) -> Dict[str, Any]:
        """Warm cache based on predicted access patterns"""
        predicted_keys = pattern_func()
        return self.warm_cache_bulk(predicted_keys)

# Cache performance testing
def test_cache_performance():
    """Test cache performance with different strategies"""
    print("Testing cache performance...")

    # Test different cache sizes
    cache_sizes = [100, 500, 1000, 5000]
    test_data = [(f"key_{i}", f"value_{i}") for i in range(10000)]

    for size in cache_sizes:
        cache = LRUCache(size)
        start_time = time.time()

        # Simulate access pattern
        for i, (key, value) in enumerate(test_data):
            # Set every item
            cache.set(key, value)

            # Random access pattern
            if i > 0 and random.random() < 0.3:
                random_key = f"key_{random.randint(0, min(i, size-1))}"
                cache.get(random_key)

        duration = time.time() - start_time
        stats = cache.get_stats()

        print(f"Cache size {size}: {duration:.3f}s, hit rate: {stats['hit_rate']:.2%}")

    # Test multi-level cache
    print("\nTesting multi-level cache...")
    ml_cache = MultiLevelCache(l1_size=100, l2_size=1000)

    # Simulate realistic access pattern
    for i in range(5000):
        key = f"key_{i}"
        value = f"value_{i}"
        ml_cache.set(key, value)

    # Simulate hot data access
    hot_keys = [f"key_{i}" for i in range(50)]  # First 50 keys are "hot"

    for _ in range(1000):
        # 80% hot data, 20% random
        if random.random() < 0.8:
            key = random.choice(hot_keys)
        else:
            key = f"key_{random.randint(0, 4999)}"

        ml_cache.get(key)

    ml_stats = ml_cache.get_stats()
    print(f"Multi-level cache L1 hit rate: {ml_stats['l1_stats']['hit_rate']:.2%}")
    print(f"Multi-level cache L2 hit rate: {ml_stats['l2_stats']['hit_rate']:.2%}")

if __name__ == "__main__":
    test_cache_performance()
```

## 🔧 System-Level Optimizations

### 1. Resource Management and Concurrency

```python
import asyncio
import concurrent.futures
from multiprocessing import Pool, cpu_count
import resource

class ResourceManager:
    """
    System resource management and optimization
    """

    def __init__(self):
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=cpu_count() * 2)
        self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count())

    def set_memory_limit(self, limit_gb: float):
        """Set memory limit for the process"""
        limit_bytes = int(limit_gb * 1024 * 1024 * 1024)
        resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))

    def optimize_for_cpu_bound(self, func: Callable, data_list: List[Any]) -> List[Any]:
        """Optimize CPU-bound tasks using multiprocessing"""
        with self.process_pool as executor:
            results = list(executor.map(func, data_list))
        return results

    def optimize_for_io_bound(self, func: Callable, data_list: List[Any]) -> List[Any]:
        """Optimize I/O-bound tasks using threading"""
        with self.thread_pool as executor:
            futures = [executor.submit(func, data) for data in data_list]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        return results

    async def optimize_for_async_io(self, async_func: Callable, data_list: List[Any]) -> List[Any]:
        """Optimize async I/O operations"""
        tasks = [async_func(data) for data in data_list]
        results = await asyncio.gather(*tasks)
        return results

    def get_system_resources(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        memory_usage = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=1)
        disk_usage = psutil.disk_usage('/')

        return {
            'cpu_percent': cpu_usage,
            'memory_percent': memory_usage.percent,
            'memory_available_gb': memory_usage.available / (1024**3),
            'disk_percent': disk_usage.percent,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }

# Connection pooling for database optimization
class ConnectionPool:
    """
    Database connection pool for improved performance
    """

    def __init__(self, connection_factory: Callable, max_connections: int = 20):
        self.connection_factory = connection_factory
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()

        # Pre-populate pool
        for _ in range(min(5, max_connections)):
            self.pool.put(self.connection_factory())
            self.active_connections += 1

    def get_connection(self, timeout: float = 30.0):
        """Get connection from pool"""
        try:
            # Try to get existing connection
            connection = self.pool.get(timeout=timeout)
            return connection
        except queue.Empty:
            # Create new connection if under limit
            with self.lock:
                if self.active_connections < self.max_connections:
                    connection = self.connection_factory()
                    self.active_connections += 1
                    return connection
                else:
                    raise Exception("Connection pool exhausted")

    def return_connection(self, connection):
        """Return connection to pool"""
        try:
            self.pool.put_nowait(connection)
        except queue.Full:
            # Close connection if pool is full
            if hasattr(connection, 'close'):
                connection.close()
            with self.lock:
                self.active_connections -= 1

    def close_all(self):
        """Close all connections in pool"""
        while not self.pool.empty():
            try:
                connection = self.pool.get_nowait()
                if hasattr(connection, 'close'):
                    connection.close()
            except queue.Empty:
                break

        with self.lock:
            self.active_connections = 0

# Batch processing optimization
class BatchProcessor:
    """
    Optimize operations through batching
    """

    def __init__(self, batch_size: int = 100, flush_interval: float = 5.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch_queue = queue.Queue()
        self.processors: Dict[str, Callable] = {}
        self.running = False
        self.last_flush = time.time()

    def register_processor(self, operation_type: str, processor: Callable[[List], None]):
        """Register batch processor for operation type"""
        self.processors[operation_type] = processor

    def add_operation(self, operation_type: str, data: Any):
        """Add operation to batch"""
        self.batch_queue.put((operation_type, data))

    def start_processing(self):
        """Start batch processing in background"""
        self.running = True
        thread = threading.Thread(target=self._process_batches, daemon=True)
        thread.start()

    def stop_processing(self):
        """Stop batch processing"""
        self.running = False

    def _process_batches(self):
        """Process batches in background"""
        batches = defaultdict(list)

        while self.running:
            try:
                # Collect items for batching
                while not self.batch_queue.empty():
                    operation_type, data = self.batch_queue.get_nowait()
                    batches[operation_type].append(data)

                # Process batches when full or time interval reached
                current_time = time.time()
                should_flush = current_time - self.last_flush >= self.flush_interval

                for operation_type, batch_data in batches.items():
                    if len(batch_data) >= self.batch_size or (should_flush and batch_data):
                        if operation_type in self.processors:
                            try:
                                self.processors[operation_type](batch_data)
                                batches[operation_type] = []  # Clear processed batch
                            except Exception as e:
                                print(f"Error processing batch for {operation_type}: {e}")

                if should_flush:
                    self.last_flush = current_time

                time.sleep(0.1)  # Small delay

            except Exception as e:
                print(f"Error in batch processing: {e}")
                time.sleep(1)
```

## ✅ Performance Optimization Checklist

### Application Level
- [ ] Profile code to identify bottlenecks
- [ ] Optimize algorithm complexity
- [ ] Implement efficient data structures
- [ ] Use connection pooling
- [ ] Enable response compression
- [ ] Implement proper caching strategies

### Database Level
- [ ] Add appropriate indexes
- [ ] Optimize query performance
- [ ] Use query result caching
- [ ] Implement read replicas
- [ ] Consider database sharding
- [ ] Monitor slow query logs

### System Level
- [ ] Optimize memory usage
- [ ] Use appropriate concurrency models
- [ ] Implement load balancing
- [ ] Monitor system resources
- [ ] Configure OS-level optimizations
- [ ] Use CDN for static content

### Network Level
- [ ] Minimize network round trips
- [ ] Use persistent connections
- [ ] Implement request batching
- [ ] Optimize payload sizes
- [ ] Consider geographic distribution

## 🎯 Performance Testing Strategies

### 1. **Load Testing**
- Gradual load increase
- Sustained load testing
- Spike testing

### 2. **Stress Testing**
- Maximum capacity testing
- Breaking point identification
- Recovery testing

### 3. **Performance Monitoring**
- Real-time metrics collection
- Alerting on performance degradation
- Capacity planning

## ✅ Key Takeaways

1. **Measure First**: Always profile before optimizing
2. **Optimize Bottlenecks**: Focus on the slowest components
3. **Cache Strategically**: Implement appropriate caching layers
4. **Database Optimization**: Proper indexing and query optimization
5. **Resource Management**: Efficient use of CPU, memory, and I/O
6. **Monitor Continuously**: Ongoing performance monitoring
7. **Test Under Load**: Regular performance testing

## 🚀 Next Steps

- Study [Cost Optimization](../cost-optimization/) for efficiency
- Learn [Security at Scale](../security-at-scale/) considerations
- Practice [System Design Interviews](../../05-interview-preparation/)
- Explore [Multi-Region Deployment](../multi-region-deployment/) strategies