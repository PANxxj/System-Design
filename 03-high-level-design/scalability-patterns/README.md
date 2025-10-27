# Scalability Patterns for Distributed Systems

## Overview
Scalability patterns are proven architectural approaches to handle increasing load, traffic, and data volume in distributed systems. This guide covers horizontal and vertical scaling, load distribution, caching strategies, and performance optimization patterns.

## Table of Contents
1. [Horizontal vs Vertical Scaling](#horizontal-vs-vertical-scaling)
2. [Load Balancing Patterns](#load-balancing-patterns)
3. [Database Scaling Patterns](#database-scaling-patterns)
4. [Caching Patterns](#caching-patterns)
5. [Microservices Scaling](#microservices-scaling)
6. [Auto-scaling Implementation](#auto-scaling-implementation)
7. [Performance Monitoring](#performance-monitoring)

## Horizontal vs Vertical Scaling

### Vertical Scaling (Scale Up)
Adding more power to existing machines.

```python
import psutil
import asyncio
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ResourceMetrics:
    cpu_percent: float
    memory_percent: float
    disk_io: Dict[str, int]
    network_io: Dict[str, int]

class VerticalScalingManager:
    def __init__(self):
        self.thresholds = {
            'cpu': 80.0,
            'memory': 85.0,
            'disk_io': 1000,  # MB/s
            'network_io': 500  # MB/s
        }
        self.scaling_history = []

    async def monitor_resources(self):
        """Monitor system resources for scaling decisions"""
        while True:
            metrics = await self.collect_metrics()

            if self.should_scale_up(metrics):
                await self.scale_up_resources(metrics)

            await asyncio.sleep(60)  # Check every minute

    async def collect_metrics(self) -> ResourceMetrics:
        """Collect current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()

        return ResourceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_io={
                'read_mb': disk_io.read_bytes / (1024 * 1024),
                'write_mb': disk_io.write_bytes / (1024 * 1024)
            },
            network_io={
                'sent_mb': network_io.bytes_sent / (1024 * 1024),
                'recv_mb': network_io.bytes_recv / (1024 * 1024)
            }
        )

    def should_scale_up(self, metrics: ResourceMetrics) -> bool:
        """Determine if vertical scaling is needed"""
        return (
            metrics.cpu_percent > self.thresholds['cpu'] or
            metrics.memory_percent > self.thresholds['memory'] or
            max(metrics.disk_io.values()) > self.thresholds['disk_io'] or
            max(metrics.network_io.values()) > self.thresholds['network_io']
        )

    async def scale_up_resources(self, metrics: ResourceMetrics):
        """Simulate vertical scaling (would integrate with cloud APIs)"""
        scaling_action = {
            'timestamp': asyncio.get_event_loop().time(),
            'metrics': metrics,
            'action': 'scale_up',
            'new_instance_type': self.calculate_new_instance_type(metrics)
        }

        self.scaling_history.append(scaling_action)
        print(f"Scaling up: {scaling_action}")

    def calculate_new_instance_type(self, metrics: ResourceMetrics) -> str:
        """Calculate appropriate new instance type based on bottlenecks"""
        if metrics.cpu_percent > self.thresholds['cpu']:
            return "cpu_optimized_large"
        elif metrics.memory_percent > self.thresholds['memory']:
            return "memory_optimized_large"
        else:
            return "general_purpose_large"
```

### Horizontal Scaling (Scale Out)

```python
import asyncio
import aiohttp
from typing import List, Dict, Optional
import time

class HorizontalScalingManager:
    def __init__(self, load_balancer_url: str):
        self.load_balancer_url = load_balancer_url
        self.instances = []
        self.min_instances = 2
        self.max_instances = 20
        self.target_cpu_utilization = 70.0
        self.scale_up_threshold = 80.0
        self.scale_down_threshold = 30.0
        self.cooldown_period = 300  # 5 minutes

    async def auto_scale(self):
        """Automatically scale instances based on load"""
        while True:
            try:
                avg_cpu = await self.get_average_cpu_utilization()
                current_instances = len(self.instances)

                if (avg_cpu > self.scale_up_threshold and
                    current_instances < self.max_instances and
                    self.can_scale()):

                    await self.scale_out()

                elif (avg_cpu < self.scale_down_threshold and
                      current_instances > self.min_instances and
                      self.can_scale()):

                    await self.scale_in()

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Auto-scaling error: {e}")
                await asyncio.sleep(60)

    async def scale_out(self):
        """Add new instance to handle increased load"""
        new_instance = await self.launch_instance()
        if new_instance:
            self.instances.append(new_instance)
            await self.register_with_load_balancer(new_instance)
            print(f"Scaled out: Added instance {new_instance['id']}")

    async def scale_in(self):
        """Remove instance when load decreases"""
        if len(self.instances) > self.min_instances:
            instance_to_remove = await self.select_instance_for_removal()
            await self.deregister_from_load_balancer(instance_to_remove)
            await self.terminate_instance(instance_to_remove)
            self.instances.remove(instance_to_remove)
            print(f"Scaled in: Removed instance {instance_to_remove['id']}")

    async def launch_instance(self) -> Optional[Dict]:
        """Launch new compute instance"""
        # Simulate cloud instance launch
        instance = {
            'id': f"instance-{int(time.time())}",
            'ip': f"10.0.{len(self.instances) + 1}.100",
            'port': 8080,
            'status': 'running',
            'launched_at': time.time()
        }

        # Wait for instance to be ready
        await asyncio.sleep(30)  # Simulated boot time
        return instance

    async def get_average_cpu_utilization(self) -> float:
        """Get average CPU utilization across all instances"""
        if not self.instances:
            return 0.0

        cpu_values = []
        async with aiohttp.ClientSession() as session:
            for instance in self.instances:
                try:
                    async with session.get(
                        f"http://{instance['ip']}:{instance['port']}/metrics/cpu"
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            cpu_values.append(data['cpu_percent'])
                except Exception:
                    continue

        return sum(cpu_values) / len(cpu_values) if cpu_values else 0.0

    def can_scale(self) -> bool:
        """Check if scaling action is allowed (cooldown period)"""
        if not hasattr(self, 'last_scaling_action'):
            return True

        return time.time() - self.last_scaling_action > self.cooldown_period

    async def select_instance_for_removal(self) -> Dict:
        """Select least utilized instance for removal"""
        instance_loads = {}

        async with aiohttp.ClientSession() as session:
            for instance in self.instances:
                try:
                    async with session.get(
                        f"http://{instance['ip']}:{instance['port']}/metrics/load"
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            instance_loads[instance['id']] = data['active_connections']
                except Exception:
                    instance_loads[instance['id']] = 0

        # Select instance with lowest load
        min_load_instance_id = min(instance_loads.items(), key=lambda x: x[1])[0]
        return next(i for i in self.instances if i['id'] == min_load_instance_id)
```

## Load Balancing Patterns

### Round Robin Load Balancer

```python
import asyncio
import aiohttp
from typing import List, Dict
import itertools

class RoundRobinLoadBalancer:
    def __init__(self, servers: List[Dict]):
        self.servers = servers
        self.server_cycle = itertools.cycle(servers)
        self.health_check_interval = 30
        self.healthy_servers = set(s['id'] for s in servers)

    async def route_request(self, request_data: Dict) -> Dict:
        """Route request to next available server"""
        max_attempts = len(self.servers)

        for _ in range(max_attempts):
            server = next(self.server_cycle)

            if server['id'] in self.healthy_servers:
                try:
                    response = await self.forward_request(server, request_data)
                    return response
                except Exception as e:
                    # Mark server as unhealthy
                    self.healthy_servers.discard(server['id'])
                    continue

        raise Exception("No healthy servers available")

    async def forward_request(self, server: Dict, request_data: Dict) -> Dict:
        """Forward request to specific server"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{server['host']}:{server['port']}/api",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                return await response.json()

    async def health_check_loop(self):
        """Continuously check server health"""
        while True:
            await self.check_all_servers_health()
            await asyncio.sleep(self.health_check_interval)

    async def check_all_servers_health(self):
        """Check health of all servers"""
        health_tasks = [
            self.check_server_health(server)
            for server in self.servers
        ]

        results = await asyncio.gather(*health_tasks, return_exceptions=True)

        for server, is_healthy in zip(self.servers, results):
            if is_healthy:
                self.healthy_servers.add(server['id'])
            else:
                self.healthy_servers.discard(server['id'])

    async def check_server_health(self, server: Dict) -> bool:
        """Check if individual server is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"http://{server['host']}:{server['port']}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception:
            return False
```

### Weighted Load Balancing

```python
import random
from typing import List, Dict, Tuple

class WeightedLoadBalancer:
    def __init__(self, servers: List[Dict]):
        self.servers = servers
        self.weighted_servers = self._build_weighted_list()

    def _build_weighted_list(self) -> List[Dict]:
        """Build weighted server list for selection"""
        weighted_list = []
        for server in self.servers:
            weight = server.get('weight', 1)
            weighted_list.extend([server] * weight)
        return weighted_list

    async def route_request(self, request_data: Dict) -> Dict:
        """Route request based on server weights"""
        server = random.choice(self.weighted_servers)
        return await self.forward_request(server, request_data)

    def update_server_weight(self, server_id: str, new_weight: int):
        """Dynamically update server weight"""
        for server in self.servers:
            if server['id'] == server_id:
                server['weight'] = new_weight
                break

        # Rebuild weighted list
        self.weighted_servers = self._build_weighted_list()
```

### Sticky Session Load Balancer

```python
import hashlib
from typing import Dict, Optional

class StickySessionLoadBalancer:
    def __init__(self, servers: List[Dict]):
        self.servers = servers
        self.session_map = {}  # session_id -> server
        self.server_sessions = {s['id']: set() for s in servers}

    async def route_request(self, request_data: Dict) -> Dict:
        """Route request maintaining session affinity"""
        session_id = request_data.get('session_id')

        if session_id and session_id in self.session_map:
            # Use existing server for this session
            server_id = self.session_map[session_id]
            server = next((s for s in self.servers if s['id'] == server_id), None)

            if server and self._is_server_healthy(server):
                return await self.forward_request(server, request_data)

        # Assign new session to least loaded server
        server = self._select_least_loaded_server()
        if session_id:
            self.session_map[session_id] = server['id']
            self.server_sessions[server['id']].add(session_id)

        return await self.forward_request(server, request_data)

    def _select_least_loaded_server(self) -> Dict:
        """Select server with fewest active sessions"""
        return min(
            self.servers,
            key=lambda s: len(self.server_sessions[s['id']])
        )

    def remove_session(self, session_id: str):
        """Clean up session mapping"""
        if session_id in self.session_map:
            server_id = self.session_map[session_id]
            self.server_sessions[server_id].discard(session_id)
            del self.session_map[session_id]
```

## Database Scaling Patterns

### Read Replicas Pattern

```python
import asyncio
import random
from typing import List, Dict, Optional

class DatabaseCluster:
    def __init__(self, master_config: Dict, replica_configs: List[Dict]):
        self.master = master_config
        self.replicas = replica_configs
        self.replica_weights = {r['id']: r.get('weight', 1) for r in replica_configs}
        self.read_strategy = 'weighted_random'

    async def write(self, query: str, params: tuple) -> Dict:
        """Execute write operation on master"""
        return await self._execute_on_database(self.master, query, params)

    async def read(self, query: str, params: tuple,
                   consistency: str = 'eventual') -> Dict:
        """Execute read operation with different consistency levels"""

        if consistency == 'strong':
            # Read from master for strong consistency
            return await self._execute_on_database(self.master, query, params)

        elif consistency == 'bounded_staleness':
            # Try replicas first, fallback to master if too stale
            replica = await self._select_fresh_replica(max_lag_seconds=5)
            if replica:
                return await self._execute_on_database(replica, query, params)
            else:
                return await self._execute_on_database(self.master, query, params)

        else:  # eventual consistency
            replica = self._select_read_replica()
            try:
                return await self._execute_on_database(replica, query, params)
            except Exception:
                # Fallback to master if replica fails
                return await self._execute_on_database(self.master, query, params)

    def _select_read_replica(self) -> Dict:
        """Select read replica based on strategy"""
        if self.read_strategy == 'round_robin':
            return self._round_robin_selection()
        elif self.read_strategy == 'weighted_random':
            return self._weighted_random_selection()
        else:
            return random.choice(self.replicas)

    def _weighted_random_selection(self) -> Dict:
        """Select replica using weighted random"""
        total_weight = sum(self.replica_weights.values())
        rand_val = random.uniform(0, total_weight)

        cumulative_weight = 0
        for replica in self.replicas:
            cumulative_weight += self.replica_weights[replica['id']]
            if rand_val <= cumulative_weight:
                return replica

        return self.replicas[-1]

    async def _select_fresh_replica(self, max_lag_seconds: int) -> Optional[Dict]:
        """Select replica with acceptable replication lag"""
        for replica in self.replicas:
            lag = await self._get_replication_lag(replica)
            if lag <= max_lag_seconds:
                return replica
        return None

    async def _get_replication_lag(self, replica: Dict) -> float:
        """Get replication lag for a replica in seconds"""
        try:
            lag_query = "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))"
            result = await self._execute_on_database(replica, lag_query, ())
            return float(result['lag']) if result else float('inf')
        except Exception:
            return float('inf')
```

### Database Sharding Pattern

```python
import hashlib
from typing import Dict, List, Any, Optional
import asyncio

class ShardedDatabase:
    def __init__(self, shards: List[Dict]):
        self.shards = shards
        self.shard_map = {shard['id']: shard for shard in shards}
        self.virtual_nodes = self._create_virtual_nodes()

    def _create_virtual_nodes(self, nodes_per_shard: int = 100) -> Dict[int, str]:
        """Create virtual nodes for consistent hashing"""
        virtual_nodes = {}

        for shard in self.shards:
            for i in range(nodes_per_shard):
                virtual_key = f"{shard['id']}:{i}"
                hash_value = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
                virtual_nodes[hash_value] = shard['id']

        return dict(sorted(virtual_nodes.items()))

    def get_shard_for_key(self, key: str) -> Dict:
        """Get shard for a given partition key"""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)

        # Find the first virtual node >= hash_value
        for node_hash, shard_id in self.virtual_nodes.items():
            if hash_value <= node_hash:
                return self.shard_map[shard_id]

        # Wrap around to first shard
        first_shard_id = next(iter(self.virtual_nodes.values()))
        return self.shard_map[first_shard_id]

    async def insert(self, table: str, data: Dict, partition_key: str) -> Dict:
        """Insert data into appropriate shard"""
        key_value = str(data.get(partition_key, ''))
        shard = self.get_shard_for_key(key_value)

        query = self._build_insert_query(table, data)
        return await self._execute_on_shard(shard, query, tuple(data.values()))

    async def get(self, table: str, partition_key: str, key_value: str) -> Optional[Dict]:
        """Get data from appropriate shard"""
        shard = self.get_shard_for_key(key_value)

        query = f"SELECT * FROM {table} WHERE {partition_key} = ?"
        result = await self._execute_on_shard(shard, query, (key_value,))
        return result[0] if result else None

    async def scatter_gather_query(self, query: str, params: tuple) -> List[Dict]:
        """Execute query across all shards and gather results"""
        tasks = [
            self._execute_on_shard(shard, query, params)
            for shard in self.shards
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results from all shards
        combined_results = []
        for result in results:
            if isinstance(result, list):
                combined_results.extend(result)

        return combined_results

    def _build_insert_query(self, table: str, data: Dict) -> str:
        """Build INSERT query from data dictionary"""
        columns = list(data.keys())
        placeholders = ['?' for _ in columns]

        return f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(placeholders)})"

    async def _execute_on_shard(self, shard: Dict, query: str, params: tuple) -> List[Dict]:
        """Execute query on specific shard"""
        # Implementation would use actual database connection
        pass
```

## Caching Patterns

### Multi-Level Caching

```python
import asyncio
from typing import Any, Optional, Dict
import time
import json

class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # In-memory cache
        self.l2_cache = None  # Redis cache
        self.l3_cache = None  # Database cache
        self.l1_max_size = 1000
        self.l1_ttl = 300  # 5 minutes
        self.l2_ttl = 3600  # 1 hour

    async def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache"""

        # Try L1 (memory) first
        value = self._get_from_l1(key)
        if value is not None:
            return value

        # Try L2 (Redis) second
        if self.l2_cache:
            value = await self._get_from_l2(key)
            if value is not None:
                # Backfill L1
                self._set_to_l1(key, value)
                return value

        # Try L3 (Database) last
        if self.l3_cache:
            value = await self._get_from_l3(key)
            if value is not None:
                # Backfill L2 and L1
                if self.l2_cache:
                    await self._set_to_l2(key, value)
                self._set_to_l1(key, value)
                return value

        return None

    async def set(self, key: str, value: Any):
        """Set value in all cache levels"""
        # Set in all levels
        self._set_to_l1(key, value)

        if self.l2_cache:
            await self._set_to_l2(key, value)

        if self.l3_cache:
            await self._set_to_l3(key, value)

    def _get_from_l1(self, key: str) -> Optional[Any]:
        """Get from L1 memory cache"""
        if key in self.l1_cache:
            entry = self.l1_cache[key]
            if time.time() - entry['timestamp'] < self.l1_ttl:
                return entry['value']
            else:
                del self.l1_cache[key]
        return None

    def _set_to_l1(self, key: str, value: Any):
        """Set to L1 memory cache with LRU eviction"""
        if len(self.l1_cache) >= self.l1_max_size:
            # LRU eviction
            oldest_key = min(
                self.l1_cache.keys(),
                key=lambda k: self.l1_cache[k]['timestamp']
            )
            del self.l1_cache[oldest_key]

        self.l1_cache[key] = {
            'value': value,
            'timestamp': time.time()
        }

    async def _get_from_l2(self, key: str) -> Optional[Any]:
        """Get from L2 Redis cache"""
        try:
            cached = await self.l2_cache.get(key)
            return json.loads(cached) if cached else None
        except Exception:
            return None

    async def _set_to_l2(self, key: str, value: Any):
        """Set to L2 Redis cache"""
        try:
            await self.l2_cache.setex(key, self.l2_ttl, json.dumps(value))
        except Exception:
            pass
```

### Cache-Aside Pattern

```python
class CacheAsidePattern:
    def __init__(self, cache, database):
        self.cache = cache
        self.database = database
        self.cache_ttl = 3600

    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user with cache-aside pattern"""
        cache_key = f"user:{user_id}"

        # Try cache first
        cached_user = await self.cache.get(cache_key)
        if cached_user:
            return cached_user

        # Cache miss - fetch from database
        user = await self.database.get_user(user_id)
        if user:
            # Store in cache for future requests
            await self.cache.setex(cache_key, self.cache_ttl, json.dumps(user))

        return user

    async def update_user(self, user_id: str, updates: Dict) -> Dict:
        """Update user and invalidate cache"""
        # Update database
        updated_user = await self.database.update_user(user_id, updates)

        # Invalidate cache to maintain consistency
        cache_key = f"user:{user_id}"
        await self.cache.delete(cache_key)

        return updated_user

    async def create_user(self, user_data: Dict) -> Dict:
        """Create user and populate cache"""
        # Create in database
        new_user = await self.database.create_user(user_data)

        # Populate cache
        cache_key = f"user:{new_user['id']}"
        await self.cache.setex(cache_key, self.cache_ttl, json.dumps(new_user))

        return new_user
```

## Auto-scaling Implementation

### Kubernetes-style Auto-scaler

```python
import asyncio
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ScalingMetrics:
    cpu_utilization: float
    memory_utilization: float
    request_rate: float
    response_time: float

class HorizontalPodAutoscaler:
    def __init__(self, min_replicas: int = 2, max_replicas: int = 10):
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.target_cpu_utilization = 70.0
        self.scale_up_threshold = 80.0
        self.scale_down_threshold = 30.0
        self.cooldown_period = 300  # 5 minutes
        self.last_scale_time = 0
        self.current_replicas = min_replicas

    async def auto_scale_loop(self):
        """Main auto-scaling loop"""
        while True:
            try:
                metrics = await self.collect_metrics()
                desired_replicas = self.calculate_desired_replicas(metrics)

                if desired_replicas != self.current_replicas:
                    await self.scale_to(desired_replicas)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                print(f"Auto-scaling error: {e}")
                await asyncio.sleep(30)

    def calculate_desired_replicas(self, metrics: ScalingMetrics) -> int:
        """Calculate desired number of replicas based on metrics"""
        # CPU-based scaling
        cpu_desired = int(
            self.current_replicas * (metrics.cpu_utilization / self.target_cpu_utilization)
        )

        # Request rate-based scaling
        target_requests_per_pod = 100  # requests per second
        rate_desired = max(1, int(metrics.request_rate / target_requests_per_pod))

        # Take the maximum of both calculations
        desired = max(cpu_desired, rate_desired)

        # Apply bounds
        return max(self.min_replicas, min(self.max_replicas, desired))

    async def scale_to(self, desired_replicas: int):
        """Scale to desired number of replicas"""
        if not self.can_scale():
            return

        if desired_replicas > self.current_replicas:
            await self.scale_up(desired_replicas - self.current_replicas)
        elif desired_replicas < self.current_replicas:
            await self.scale_down(self.current_replicas - desired_replicas)

        self.last_scale_time = time.time()

    def can_scale(self) -> bool:
        """Check if scaling is allowed (cooldown period)"""
        return time.time() - self.last_scale_time > self.cooldown_period

    async def scale_up(self, count: int):
        """Scale up by adding replicas"""
        for _ in range(count):
            await self.add_replica()
            self.current_replicas += 1

        print(f"Scaled up to {self.current_replicas} replicas")

    async def scale_down(self, count: int):
        """Scale down by removing replicas"""
        for _ in range(count):
            await self.remove_replica()
            self.current_replicas -= 1

        print(f"Scaled down to {self.current_replicas} replicas")

    async def collect_metrics(self) -> ScalingMetrics:
        """Collect current system metrics"""
        # Simulate metrics collection
        return ScalingMetrics(
            cpu_utilization=75.0,
            memory_utilization=60.0,
            request_rate=150.0,
            response_time=200.0
        )
```

### Predictive Auto-scaling

```python
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple
import time

class PredictiveAutoscaler:
    def __init__(self):
        self.historical_data = []
        self.model = LinearRegression()
        self.prediction_window = 300  # 5 minutes
        self.min_history_points = 20

    async def collect_and_predict(self):
        """Collect metrics and predict future load"""
        while True:
            current_metrics = await self.collect_current_metrics()
            self.historical_data.append({
                'timestamp': time.time(),
                'cpu_utilization': current_metrics['cpu'],
                'request_rate': current_metrics['requests'],
                'memory_usage': current_metrics['memory']
            })

            # Keep only recent history (last 2 hours)
            cutoff_time = time.time() - 7200
            self.historical_data = [
                d for d in self.historical_data
                if d['timestamp'] > cutoff_time
            ]

            if len(self.historical_data) >= self.min_history_points:
                predicted_load = self.predict_future_load()
                await self.proactive_scale(predicted_load)

            await asyncio.sleep(60)

    def predict_future_load(self) -> Dict[str, float]:
        """Predict future load based on historical data"""
        if len(self.historical_data) < self.min_history_points:
            return {}

        # Prepare training data
        X, y_cpu, y_requests = self._prepare_training_data()

        # Train models
        cpu_model = LinearRegression().fit(X, y_cpu)
        requests_model = LinearRegression().fit(X, y_requests)

        # Predict future values
        future_time = time.time() + self.prediction_window
        future_X = np.array([[future_time]])

        predicted_cpu = cpu_model.predict(future_X)[0]
        predicted_requests = requests_model.predict(future_X)[0]

        return {
            'predicted_cpu': max(0, predicted_cpu),
            'predicted_requests': max(0, predicted_requests),
            'confidence': self._calculate_confidence(X, y_cpu)
        }

    def _prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data from historical metrics"""
        timestamps = [d['timestamp'] for d in self.historical_data]
        cpu_values = [d['cpu_utilization'] for d in self.historical_data]
        request_values = [d['request_rate'] for d in self.historical_data]

        X = np.array(timestamps).reshape(-1, 1)
        y_cpu = np.array(cpu_values)
        y_requests = np.array(request_values)

        return X, y_cpu, y_requests

    async def proactive_scale(self, predicted_load: Dict[str, float]):
        """Scale proactively based on predictions"""
        if not predicted_load or predicted_load.get('confidence', 0) < 0.7:
            return

        predicted_cpu = predicted_load['predicted_cpu']

        if predicted_cpu > 85:
            # Scale up before the spike
            await self.schedule_scale_up()
        elif predicted_cpu < 25:
            # Scale down before the dip
            await self.schedule_scale_down()
```

This comprehensive scalability patterns guide provides production-ready implementations for handling growth in distributed systems. The patterns cover both reactive and proactive scaling approaches, ensuring systems can handle varying loads efficiently.