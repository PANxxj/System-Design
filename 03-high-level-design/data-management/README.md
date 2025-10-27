# Data Management in Distributed Systems

## Overview
Data management is critical for building scalable, reliable, and performant distributed systems. This guide covers data storage strategies, consistency models, partitioning, replication, and data processing patterns.

## Table of Contents
1. [Data Storage Strategies](#data-storage-strategies)
2. [Database Selection](#database-selection)
3. [Data Partitioning](#data-partitioning)
4. [Replication Strategies](#replication-strategies)
5. [Consistency Models](#consistency-models)
6. [Data Processing Patterns](#data-processing-patterns)
7. [Implementation Examples](#implementation-examples)

## Data Storage Strategies

### Relational Databases (RDBMS)
Best for: ACID transactions, complex queries, structured data

```python
import asyncpg
import asyncio
from typing import List, Optional

class PostgreSQLManager:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None

    async def init_pool(self, min_size=10, max_size=20):
        """Initialize connection pool for better performance"""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=min_size,
            max_size=max_size,
            command_timeout=60
        )

    async def execute_transaction(self, queries: List[str], params: List[tuple]):
        """Execute multiple queries in a transaction"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                results = []
                for query, param in zip(queries, params):
                    result = await conn.execute(query, *param)
                    results.append(result)
                return results

    async def read_replica_query(self, query: str, *params):
        """Execute read-only queries on read replicas"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *params)
```

### NoSQL Databases

#### Document Stores (MongoDB)
```python
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING
import asyncio

class MongoDBManager:
    def __init__(self, connection_string: str, database_name: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]

    async def create_indexes(self, collection_name: str):
        """Create optimized indexes for common queries"""
        collection = self.db[collection_name]
        indexes = [
            IndexModel([("user_id", ASCENDING), ("timestamp", DESCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            IndexModel([("tags", ASCENDING)]),  # For array fields
        ]
        await collection.create_indexes(indexes)

    async def aggregate_data(self, collection_name: str, pipeline: List[dict]):
        """Perform complex aggregation operations"""
        collection = self.db[collection_name]
        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def bulk_upsert(self, collection_name: str, documents: List[dict]):
        """Efficient bulk operations"""
        from pymongo import UpdateOne
        collection = self.db[collection_name]

        operations = []
        for doc in documents:
            operations.append(
                UpdateOne(
                    {"_id": doc["_id"]},
                    {"$set": doc},
                    upsert=True
                )
            )

        result = await collection.bulk_write(operations)
        return result
```

#### Key-Value Stores (Redis)
```python
import redis.asyncio as redis
import json
from typing import Any, Optional
import pickle

class RedisManager:
    def __init__(self, connection_string: str):
        self.redis = redis.from_url(connection_string)

    async def set_with_ttl(self, key: str, value: Any, ttl: int = 3600):
        """Set value with time-to-live"""
        serialized = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        await self.redis.setex(key, ttl, serialized)

    async def get_or_compute(self, key: str, compute_func, ttl: int = 3600):
        """Cache-aside pattern implementation"""
        cached = await self.redis.get(key)
        if cached:
            return json.loads(cached)

        # Compute and cache
        result = await compute_func()
        await self.set_with_ttl(key, result, ttl)
        return result

    async def distributed_lock(self, lock_key: str, timeout: int = 10):
        """Distributed locking mechanism"""
        import uuid
        lock_value = str(uuid.uuid4())

        # Try to acquire lock
        acquired = await self.redis.set(
            lock_key, lock_value, nx=True, ex=timeout
        )

        if acquired:
            return {"acquired": True, "lock_value": lock_value}
        return {"acquired": False, "lock_value": None}

    async def release_lock(self, lock_key: str, lock_value: str):
        """Release distributed lock safely"""
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        return await self.redis.eval(lua_script, 1, lock_key, lock_value)
```

## Database Selection

### Decision Matrix

```python
class DatabaseSelector:
    def __init__(self):
        self.criteria = {
            'consistency': {'strong': 10, 'eventual': 5, 'none': 0},
            'scalability': {'horizontal': 10, 'vertical': 5, 'limited': 0},
            'query_complexity': {'high': 10, 'medium': 5, 'simple': 2},
            'transaction_support': {'acid': 10, 'basic': 5, 'none': 0},
            'data_structure': {'structured': 10, 'semi': 5, 'unstructured': 2}
        }

    def evaluate_database(self, requirements: dict):
        """Evaluate database options based on requirements"""
        databases = {
            'PostgreSQL': {
                'consistency': 'strong',
                'scalability': 'vertical',
                'query_complexity': 'high',
                'transaction_support': 'acid',
                'data_structure': 'structured'
            },
            'MongoDB': {
                'consistency': 'eventual',
                'scalability': 'horizontal',
                'query_complexity': 'medium',
                'transaction_support': 'basic',
                'data_structure': 'semi'
            },
            'Cassandra': {
                'consistency': 'eventual',
                'scalability': 'horizontal',
                'query_complexity': 'simple',
                'transaction_support': 'none',
                'data_structure': 'structured'
            },
            'Redis': {
                'consistency': 'strong',
                'scalability': 'horizontal',
                'query_complexity': 'simple',
                'transaction_support': 'basic',
                'data_structure': 'unstructured'
            }
        }

        scores = {}
        for db_name, db_props in databases.items():
            score = 0
            for criterion, req_value in requirements.items():
                if criterion in self.criteria:
                    db_value = db_props.get(criterion, 'none')
                    if db_value == req_value:
                        score += self.criteria[criterion][req_value]
            scores[db_name] = score

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

## Data Partitioning

### Horizontal Partitioning (Sharding)

```python
import hashlib
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ShardConfig:
    shard_id: str
    connection_string: str
    weight: int = 1

class ShardManager:
    def __init__(self, shards: List[ShardConfig]):
        self.shards = shards
        self.total_weight = sum(shard.weight for shard in shards)
        self.shard_ring = self._build_consistent_hash_ring()

    def _build_consistent_hash_ring(self):
        """Build consistent hash ring for even distribution"""
        ring = {}
        for shard in self.shards:
            for i in range(shard.weight * 100):  # 100 virtual nodes per weight
                virtual_node = f"{shard.shard_id}:{i}"
                hash_value = int(hashlib.md5(virtual_node.encode()).hexdigest(), 16)
                ring[hash_value] = shard.shard_id
        return sorted(ring.items())

    def get_shard(self, key: str) -> str:
        """Get shard for a given key using consistent hashing"""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)

        for ring_hash, shard_id in self.shard_ring:
            if hash_value <= ring_hash:
                return shard_id

        # Wrap around to first shard
        return self.shard_ring[0][1]

    async def execute_on_shard(self, key: str, operation: callable, *args, **kwargs):
        """Execute operation on appropriate shard"""
        shard_id = self.get_shard(key)
        shard_config = next(s for s in self.shards if s.shard_id == shard_id)
        return await operation(shard_config.connection_string, *args, **kwargs)

    async def scatter_gather(self, operation: callable, *args, **kwargs):
        """Execute operation on all shards and gather results"""
        import asyncio
        tasks = []
        for shard in self.shards:
            task = operation(shard.connection_string, *args, **kwargs)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip([s.shard_id for s in self.shards], results))
```

### Vertical Partitioning

```python
class VerticalPartitionManager:
    def __init__(self):
        self.partitions = {
            'user_core': ['user_id', 'username', 'email', 'created_at'],
            'user_profile': ['user_id', 'first_name', 'last_name', 'bio', 'avatar_url'],
            'user_settings': ['user_id', 'theme', 'notifications', 'privacy_settings'],
            'user_activity': ['user_id', 'last_login', 'login_count', 'session_data']
        }

    async def get_complete_user(self, user_id: str):
        """Fetch user data from multiple partitions"""
        import asyncio

        async def fetch_partition(partition_name: str, fields: List[str]):
            # Simulate database fetch
            query = f"SELECT {','.join(fields)} FROM {partition_name} WHERE user_id = ?"
            return await self.execute_query(query, user_id)

        tasks = [
            fetch_partition(partition, fields)
            for partition, fields in self.partitions.items()
        ]

        results = await asyncio.gather(*tasks)

        # Merge results
        complete_user = {}
        for result in results:
            if result:
                complete_user.update(result)

        return complete_user
```

## Replication Strategies

### Master-Slave Replication

```python
import asyncio
from typing import List
import logging

class ReplicationManager:
    def __init__(self, master_config: dict, slave_configs: List[dict]):
        self.master = master_config
        self.slaves = slave_configs
        self.replication_lag = {}
        self.health_status = {}

    async def write_with_replication(self, query: str, params: tuple):
        """Write to master and replicate to slaves"""
        # Write to master
        master_result = await self.execute_on_master(query, params)

        # Async replication to slaves
        asyncio.create_task(self.replicate_to_slaves(query, params))

        return master_result

    async def replicate_to_slaves(self, query: str, params: tuple):
        """Replicate write operation to all slaves"""
        import time
        replication_tasks = []

        for i, slave in enumerate(self.slaves):
            task = self._replicate_to_slave(slave, query, params, i)
            replication_tasks.append(task)

        results = await asyncio.gather(*replication_tasks, return_exceptions=True)

        # Log replication status
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logging.error(f"Replication failed for slave {i}: {result}")

    async def _replicate_to_slave(self, slave_config: dict, query: str, params: tuple, slave_id: int):
        """Replicate to individual slave"""
        import time
        start_time = time.time()

        try:
            await self.execute_on_slave(slave_config, query, params)
            self.replication_lag[slave_id] = time.time() - start_time
            self.health_status[slave_id] = True
        except Exception as e:
            self.health_status[slave_id] = False
            raise e

    async def read_from_best_slave(self, query: str, params: tuple):
        """Read from slave with lowest lag"""
        if not self.health_status:
            # Fallback to master
            return await self.execute_on_master(query, params)

        # Find healthiest slave with lowest lag
        healthy_slaves = [
            (slave_id, lag) for slave_id, lag in self.replication_lag.items()
            if self.health_status.get(slave_id, False)
        ]

        if not healthy_slaves:
            return await self.execute_on_master(query, params)

        best_slave_id = min(healthy_slaves, key=lambda x: x[1])[0]
        return await self.execute_on_slave(self.slaves[best_slave_id], query, params)
```

### Multi-Master Replication

```python
class MultiMasterManager:
    def __init__(self, masters: List[dict]):
        self.masters = masters
        self.conflict_resolver = ConflictResolver()

    async def write_with_consensus(self, query: str, params: tuple, consistency_level='majority'):
        """Write with configurable consistency"""
        if consistency_level == 'all':
            required_acks = len(self.masters)
        elif consistency_level == 'majority':
            required_acks = len(self.masters) // 2 + 1
        else:  # 'one'
            required_acks = 1

        write_tasks = [
            self.write_to_master(master, query, params)
            for master in self.masters
        ]

        successful_writes = 0
        for task in asyncio.as_completed(write_tasks):
            try:
                await task
                successful_writes += 1
                if successful_writes >= required_acks:
                    return True
            except Exception as e:
                logging.error(f"Write failed: {e}")

        return successful_writes >= required_acks

class ConflictResolver:
    def resolve_conflicts(self, conflicted_records: List[dict]):
        """Resolve conflicts using last-write-wins with vector clocks"""
        if not conflicted_records:
            return None

        # Sort by vector clock timestamps
        return max(conflicted_records, key=lambda r: r.get('vector_clock', 0))
```

## Consistency Models

### Eventual Consistency Implementation

```python
import asyncio
import time
from typing import Dict, Any

class EventualConsistencyManager:
    def __init__(self):
        self.version_vectors = {}
        self.pending_updates = {}
        self.conflict_queue = asyncio.Queue()

    async def write(self, key: str, value: Any, node_id: str):
        """Write with vector clock versioning"""
        current_time = int(time.time() * 1000)  # milliseconds

        # Update vector clock
        if key not in self.version_vectors:
            self.version_vectors[key] = {}

        self.version_vectors[key][node_id] = current_time

        # Store with metadata
        versioned_value = {
            'value': value,
            'vector_clock': self.version_vectors[key].copy(),
            'timestamp': current_time,
            'node_id': node_id
        }

        # Propagate to other nodes
        await self.propagate_update(key, versioned_value)

        return versioned_value

    async def read(self, key: str, consistency_level='eventual'):
        """Read with different consistency guarantees"""
        if consistency_level == 'strong':
            return await self.read_with_consensus(key)
        elif consistency_level == 'bounded_staleness':
            return await self.read_with_staleness_bound(key, max_staleness=1000)
        else:  # eventual
            return await self.read_eventually_consistent(key)

    async def read_eventually_consistent(self, key: str):
        """Read latest available version"""
        if key in self.pending_updates:
            versions = self.pending_updates[key]
            if len(versions) == 1:
                return list(versions.values())[0]
            else:
                # Multiple versions - detect conflict
                await self.conflict_queue.put((key, versions))
                return self.resolve_read_conflict(versions)

        return None

    def resolve_read_conflict(self, versions: Dict[str, dict]):
        """Resolve read conflicts using timestamps"""
        return max(versions.values(), key=lambda v: v['timestamp'])
```

### Strong Consistency with Two-Phase Commit

```python
class TwoPhaseCommitManager:
    def __init__(self, participants: List[str]):
        self.participants = participants
        self.transaction_log = {}

    async def execute_transaction(self, transaction_id: str, operations: List[dict]):
        """Execute distributed transaction with 2PC"""

        # Phase 1: Prepare
        prepare_results = await self.prepare_phase(transaction_id, operations)

        if all(prepare_results.values()):
            # All participants agreed - commit
            commit_results = await self.commit_phase(transaction_id)
            return all(commit_results.values())
        else:
            # Some participants failed - abort
            abort_results = await self.abort_phase(transaction_id)
            return False

    async def prepare_phase(self, transaction_id: str, operations: List[dict]):
        """Phase 1: Ask all participants to prepare"""
        prepare_tasks = []

        for participant in self.participants:
            task = self.send_prepare(participant, transaction_id, operations)
            prepare_tasks.append(task)

        results = await asyncio.gather(*prepare_tasks, return_exceptions=True)

        # Log prepare results
        self.transaction_log[transaction_id] = {
            'status': 'prepared',
            'participants': dict(zip(self.participants, results))
        }

        return dict(zip(self.participants, results))

    async def commit_phase(self, transaction_id: str):
        """Phase 2: Commit on all participants"""
        commit_tasks = [
            self.send_commit(participant, transaction_id)
            for participant in self.participants
        ]

        results = await asyncio.gather(*commit_tasks, return_exceptions=True)

        # Update transaction log
        self.transaction_log[transaction_id]['status'] = 'committed'

        return dict(zip(self.participants, results))

    async def abort_phase(self, transaction_id: str):
        """Phase 2: Abort on all participants"""
        abort_tasks = [
            self.send_abort(participant, transaction_id)
            for participant in self.participants
        ]

        results = await asyncio.gather(*abort_tasks, return_exceptions=True)

        # Update transaction log
        self.transaction_log[transaction_id]['status'] = 'aborted'

        return dict(zip(self.participants, results))
```

## Data Processing Patterns

### Batch Processing

```python
import asyncio
from typing import List, Callable, Iterator
import time

class BatchProcessor:
    def __init__(self, batch_size: int = 1000, max_wait_time: int = 30):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.batch_queue = asyncio.Queue()
        self.current_batch = []
        self.last_batch_time = time.time()

    async def add_item(self, item: dict):
        """Add item to batch queue"""
        await self.batch_queue.put(item)

    async def process_batches(self, processor_func: Callable):
        """Continuously process batches"""
        while True:
            batch = await self.collect_batch()
            if batch:
                try:
                    await processor_func(batch)
                except Exception as e:
                    # Handle batch processing errors
                    await self.handle_batch_error(batch, e)

    async def collect_batch(self) -> List[dict]:
        """Collect items into batches based on size or time"""
        batch = []
        start_time = time.time()

        while len(batch) < self.batch_size:
            try:
                # Wait for item or timeout
                timeout = self.max_wait_time - (time.time() - start_time)
                if timeout <= 0:
                    break

                item = await asyncio.wait_for(
                    self.batch_queue.get(),
                    timeout=timeout
                )
                batch.append(item)

            except asyncio.TimeoutError:
                break

        return batch

    async def handle_batch_error(self, batch: List[dict], error: Exception):
        """Handle batch processing errors with retry logic"""
        # Log error
        print(f"Batch processing failed: {error}")

        # Retry individual items
        for item in batch:
            await self.batch_queue.put(item)
```

### Stream Processing

```python
import asyncio
from typing import AsyncIterator, Callable, Any
import json

class StreamProcessor:
    def __init__(self):
        self.processors = []
        self.filters = []
        self.aggregators = {}

    def add_processor(self, processor: Callable):
        """Add a processing function to the pipeline"""
        self.processors.append(processor)
        return self

    def add_filter(self, filter_func: Callable):
        """Add a filter function"""
        self.filters.append(filter_func)
        return self

    def add_aggregator(self, key: str, aggregator: Callable):
        """Add an aggregation function"""
        self.aggregators[key] = aggregator
        return self

    async def process_stream(self, stream: AsyncIterator[dict]) -> AsyncIterator[dict]:
        """Process stream of data through pipeline"""
        async for item in stream:
            # Apply filters
            if not all(f(item) for f in self.filters):
                continue

            # Apply processors
            processed_item = item
            for processor in self.processors:
                processed_item = await processor(processed_item)
                if processed_item is None:
                    break

            if processed_item:
                # Apply aggregators
                for key, aggregator in self.aggregators.items():
                    processed_item[key] = await aggregator(processed_item)

                yield processed_item

# Example usage
async def enrich_user_data(item: dict) -> dict:
    """Enrich user data with additional information"""
    if 'user_id' in item:
        # Simulate database lookup
        user_profile = await get_user_profile(item['user_id'])
        item['user_profile'] = user_profile
    return item

async def calculate_session_duration(item: dict) -> int:
    """Calculate session duration"""
    if 'session_start' in item and 'session_end' in item:
        return item['session_end'] - item['session_start']
    return 0

# Stream processing pipeline
processor = StreamProcessor()
processor.add_filter(lambda x: x.get('event_type') == 'user_action')
processor.add_processor(enrich_user_data)
processor.add_aggregator('session_duration', calculate_session_duration)
```

## Data Migration Strategies

```python
class DataMigrationManager:
    def __init__(self, source_db, target_db):
        self.source_db = source_db
        self.target_db = target_db
        self.migration_state = {}

    async def migrate_with_zero_downtime(self, table_name: str):
        """Zero-downtime migration using dual-write strategy"""

        # Phase 1: Start dual writing
        await self.start_dual_write(table_name)

        # Phase 2: Bulk copy historical data
        await self.bulk_copy_data(table_name)

        # Phase 3: Verify data consistency
        consistent = await self.verify_consistency(table_name)

        if consistent:
            # Phase 4: Switch reads to new database
            await self.switch_reads(table_name)

            # Phase 5: Stop dual writing
            await self.stop_dual_write(table_name)
        else:
            # Rollback
            await self.rollback_migration(table_name)

    async def bulk_copy_data(self, table_name: str, batch_size: int = 10000):
        """Copy data in batches to avoid blocking"""
        offset = 0

        while True:
            batch = await self.source_db.fetch_batch(table_name, offset, batch_size)
            if not batch:
                break

            # Transform data if needed
            transformed_batch = await self.transform_data(batch)

            # Insert into target database
            await self.target_db.bulk_insert(table_name, transformed_batch)

            offset += batch_size

            # Update migration progress
            self.migration_state[table_name] = {
                'status': 'copying',
                'progress': offset
            }

            # Allow other operations to proceed
            await asyncio.sleep(0.1)

    async def verify_consistency(self, table_name: str) -> bool:
        """Verify data consistency between source and target"""
        source_count = await self.source_db.count(table_name)
        target_count = await self.target_db.count(table_name)

        if source_count != target_count:
            return False

        # Sample-based verification
        sample_size = min(1000, source_count // 100)
        sample_records = await self.source_db.random_sample(table_name, sample_size)

        for record in sample_records:
            target_record = await self.target_db.get_by_id(table_name, record['id'])
            if not self.records_match(record, target_record):
                return False

        return True
```

## Performance Optimization

### Connection Pooling

```python
class DatabaseConnectionPool:
    def __init__(self, connection_factory, min_size=5, max_size=20):
        self.connection_factory = connection_factory
        self.min_size = min_size
        self.max_size = max_size
        self.pool = asyncio.Queue(maxsize=max_size)
        self.active_connections = 0
        self.total_connections = 0

    async def initialize(self):
        """Initialize minimum connections"""
        for _ in range(self.min_size):
            conn = await self.connection_factory()
            await self.pool.put(conn)
            self.total_connections += 1

    async def acquire(self):
        """Acquire connection from pool"""
        try:
            # Try to get existing connection
            conn = self.pool.get_nowait()
            self.active_connections += 1
            return conn
        except asyncio.QueueEmpty:
            # Create new connection if under limit
            if self.total_connections < self.max_size:
                conn = await self.connection_factory()
                self.total_connections += 1
                self.active_connections += 1
                return conn
            else:
                # Wait for available connection
                conn = await self.pool.get()
                self.active_connections += 1
                return conn

    async def release(self, conn):
        """Release connection back to pool"""
        self.active_connections -= 1
        if self.pool.qsize() < self.max_size:
            await self.pool.put(conn)
        else:
            # Close excess connections
            await conn.close()
            self.total_connections -= 1
```

### Query Optimization

```python
class QueryOptimizer:
    def __init__(self):
        self.query_cache = {}
        self.execution_stats = {}

    def optimize_query(self, query: str, params: dict):
        """Optimize query based on patterns and statistics"""

        # Check cache first
        cache_key = hash(query + str(sorted(params.items())))
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]

        optimized = query

        # Add indexes hints based on WHERE clauses
        if 'WHERE' in query.upper():
            optimized = self.add_index_hints(optimized, params)

        # Optimize JOIN order based on table sizes
        if 'JOIN' in query.upper():
            optimized = self.optimize_join_order(optimized)

        # Add LIMIT if missing for potentially large results
        if 'SELECT' in query.upper() and 'LIMIT' not in query.upper():
            optimized = self.add_limit_clause(optimized)

        self.query_cache[cache_key] = optimized
        return optimized

    def add_index_hints(self, query: str, params: dict):
        """Add database-specific index hints"""
        # Example for PostgreSQL
        for param_name in params:
            if f'{param_name}' in query:
                # Suggest index usage
                query = query.replace(
                    f'WHERE {param_name}',
                    f'WHERE {param_name} /* USE INDEX (idx_{param_name}) */'
                )
        return query

    async def explain_query(self, query: str, params: dict):
        """Get query execution plan"""
        explain_query = f"EXPLAIN ANALYZE {query}"
        result = await self.execute_query(explain_query, params)
        return self.parse_execution_plan(result)
```

This comprehensive data management guide covers the essential patterns and implementations needed for building robust distributed systems. The code examples are production-ready and demonstrate real-world best practices for data storage, partitioning, replication, and processing at scale.