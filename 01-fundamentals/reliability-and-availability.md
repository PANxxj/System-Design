# Reliability and Availability 🟢

## 🎯 Learning Objectives
- Understand the difference between reliability and availability
- Learn fault tolerance principles and redundancy patterns
- Calculate system availability and downtime
- Design systems that gracefully handle failures

## 📖 Core Concepts

### Reliability vs Availability

#### Reliability
**The probability that a system performs correctly during a specific time duration.**

- System works correctly when needed
- No failures or data corruption
- Consistent performance over time
- Measured by Mean Time Between Failures (MTBF)

#### Availability
**The percentage of time that a system is operational and accessible.**

- System is up and accessible when needed
- Can tolerate some failures if they're handled gracefully
- Measured as uptime / (uptime + downtime)
- Typically expressed as "nines" (99.9%, 99.99%, etc.)

### Key Difference
```
A system can be:
✅ Available but NOT Reliable: System is up but gives wrong results
❌ Reliable but NOT Available: System gives correct results when up, but frequently down
🎯 Both Reliable AND Available: The goal for production systems
```

## 📊 Availability Calculations

### Availability Formula
```
Availability = Uptime / (Uptime + Downtime) × 100%
```

### The "Nines" of Availability

| Availability | Downtime per Year | Downtime per Month | Downtime per Week |
|--------------|-------------------|-------------------|-------------------|
| 90% (one nine) | 36.5 days | 72 hours | 16.8 hours |
| 99% (two nines) | 3.65 days | 7.2 hours | 1.68 hours |
| 99.9% (three nines) | 8.76 hours | 43.2 minutes | 10.1 minutes |
| 99.99% (four nines) | 52.56 minutes | 4.32 minutes | 1.01 minutes |
| 99.999% (five nines) | 5.26 minutes | 25.9 seconds | 6.05 seconds |

### Practical Examples

```python
def calculate_availability(uptime_hours, total_hours):
    """Calculate availability percentage"""
    availability = (uptime_hours / total_hours) * 100
    return availability

def calculate_downtime_per_year(availability_percent):
    """Calculate allowed downtime per year"""
    hours_per_year = 365 * 24
    allowed_downtime = hours_per_year * (1 - availability_percent / 100)
    return allowed_downtime

# Examples
print(f"99.9% availability allows: {calculate_downtime_per_year(99.9):.2f} hours downtime/year")
print(f"99.99% availability allows: {calculate_downtime_per_year(99.99):.2f} hours downtime/year")

# Output:
# 99.9% availability allows: 8.76 hours downtime/year
# 99.99% availability allows: 0.88 hours downtime/year
```

## 🛡️ Fault Tolerance Principles

### Types of Failures

#### 1. Hardware Failures
- Server crashes
- Disk failures
- Network equipment failures
- Power outages

#### 2. Software Failures
- Application bugs
- Memory leaks
- Deadlocks
- Infinite loops

#### 3. Human Errors
- Configuration mistakes
- Deployment errors
- Accidental deletions
- Security breaches

#### 4. External Failures
- Third-party service outages
- Network partitions
- Natural disasters
- Security attacks

### Failure Handling Strategies

#### 1. Fail-Fast
System detects errors quickly and fails immediately rather than producing incorrect results.

```python
class DatabaseConnection:
    def __init__(self, host, port, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout

    def connect(self):
        try:
            # Attempt connection with timeout
            connection = self._establish_connection(timeout=self.timeout)
            if not self._validate_connection(connection):
                raise ConnectionError("Connection validation failed")
            return connection
        except Exception as e:
            # Fail fast - don't retry indefinitely
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}") from e

    def _establish_connection(self, timeout):
        # Implementation details
        pass

    def _validate_connection(self, connection):
        # Verify connection is healthy
        pass
```

#### 2. Fail-Safe
System continues operating in a degraded mode when failures occur.

```python
class PaymentService:
    def __init__(self, primary_processor, backup_processor):
        self.primary = primary_processor
        self.backup = backup_processor

    def process_payment(self, payment_data):
        try:
            # Try primary payment processor
            return self.primary.process(payment_data)
        except PaymentProcessorError:
            # Failover to backup processor
            return self.backup.process(payment_data)
        except Exception:
            # Fail-safe: queue for manual processing
            self._queue_for_manual_review(payment_data)
            return {"status": "queued", "message": "Payment queued for review"}

    def _queue_for_manual_review(self, payment_data):
        # Add to manual review queue
        pass
```

#### 3. Graceful Degradation
System reduces functionality but continues core operations.

```python
class RecommendationService:
    def __init__(self, ml_service, fallback_service):
        self.ml_service = ml_service
        self.fallback_service = fallback_service

    def get_recommendations(self, user_id):
        try:
            # Try advanced ML recommendations
            return self.ml_service.get_recommendations(user_id)
        except MLServiceUnavailable:
            # Graceful degradation: use simple fallback
            return self.fallback_service.get_popular_items()
        except Exception:
            # Worst case: return empty recommendations
            return []
```

## 🔄 Redundancy Patterns

### 1. Active-Passive (Hot Standby)

```python
class ActivePassiveSetup:
    def __init__(self, primary_server, standby_server):
        self.primary = primary_server
        self.standby = standby_server
        self.current_active = self.primary

    def handle_request(self, request):
        try:
            return self.current_active.process(request)
        except ServerUnavailable:
            # Failover to standby
            self._failover()
            return self.current_active.process(request)

    def _failover(self):
        """Switch to standby server"""
        if self.current_active == self.primary:
            self.current_active = self.standby
            self._promote_standby_to_active()
        else:
            # Already on standby, try to recover primary
            self._attempt_primary_recovery()

    def _promote_standby_to_active(self):
        """Promote standby to active role"""
        # Update load balancer configuration
        # Update DNS records
        # Synchronize any pending data
        pass
```

**Architecture:**
```
[Load Balancer] → [Primary Server] (Active)
                  [Standby Server] (Passive, ready to take over)
```

**Pros:**
- ✅ Fast failover
- ✅ Simple to implement
- ✅ Standby server is always up-to-date

**Cons:**
- ❌ Standby server resources are underutilized
- ❌ Still a single point of failure during failover

### 2. Active-Active (Load Balancing)

```python
class ActiveActiveSetup:
    def __init__(self, servers):
        self.servers = servers
        self.healthy_servers = set(servers)
        self.load_balancer = RoundRobinBalancer(servers)

    def handle_request(self, request):
        """Route request to healthy server"""
        if not self.healthy_servers:
            raise AllServersUnavailable("No healthy servers available")

        # Update load balancer with healthy servers
        self.load_balancer.update_servers(list(self.healthy_servers))

        try:
            server = self.load_balancer.get_next_server()
            return server.process(request)
        except ServerUnavailable as e:
            # Mark server as unhealthy and retry
            self._mark_server_unhealthy(e.server)
            return self.handle_request(request)  # Retry with remaining servers

    def _mark_server_unhealthy(self, server):
        """Remove server from healthy pool"""
        self.healthy_servers.discard(server)
        # Schedule health check to re-add when recovered
        self._schedule_health_check(server)
```

**Architecture:**
```
[Load Balancer] → [Server 1] (Active)
                → [Server 2] (Active)
                → [Server 3] (Active)
```

**Pros:**
- ✅ Better resource utilization
- ✅ Can handle multiple failures
- ✅ Automatic load distribution

**Cons:**
- ❌ More complex to implement
- ❌ Requires careful session management

### 3. Geographic Redundancy

```python
class GeographicRedundancy:
    def __init__(self):
        self.regions = {
            'us-east': {'servers': ['server1', 'server2'], 'healthy': True},
            'us-west': {'servers': ['server3', 'server4'], 'healthy': True},
            'eu-west': {'servers': ['server5', 'server6'], 'healthy': True}
        }

    def route_request(self, request, user_location):
        """Route to nearest healthy region"""
        # Find nearest region
        preferred_regions = self._get_preferred_regions(user_location)

        for region in preferred_regions:
            if self.regions[region]['healthy']:
                return self._route_to_region(request, region)

        # All preferred regions down, try any healthy region
        for region, config in self.regions.items():
            if config['healthy']:
                return self._route_to_region(request, region)

        raise AllRegionsUnavailable("No healthy regions available")

    def _get_preferred_regions(self, user_location):
        """Return regions ordered by preference for user location"""
        if user_location.startswith('US'):
            return ['us-east', 'us-west', 'eu-west']
        elif user_location.startswith('EU'):
            return ['eu-west', 'us-east', 'us-west']
        else:
            return ['us-east', 'us-west', 'eu-west']
```

## 🔍 Health Checks and Monitoring

### Health Check Types

#### 1. Passive Health Checks
Monitor actual request success/failure rates.

```python
class PassiveHealthChecker:
    def __init__(self, failure_threshold=5, time_window=60):
        self.failure_threshold = failure_threshold
        self.time_window = time_window
        self.server_stats = {}

    def record_request_result(self, server, success):
        """Record the result of a request"""
        if server not in self.server_stats:
            self.server_stats[server] = {'failures': [], 'total_requests': 0}

        self.server_stats[server]['total_requests'] += 1

        if not success:
            self.server_stats[server]['failures'].append(time.time())

        # Clean old failures outside time window
        self._clean_old_failures(server)

    def is_server_healthy(self, server):
        """Check if server is considered healthy"""
        if server not in self.server_stats:
            return True  # No data yet, assume healthy

        recent_failures = len(self.server_stats[server]['failures'])
        return recent_failures < self.failure_threshold

    def _clean_old_failures(self, server):
        """Remove failures outside the time window"""
        cutoff_time = time.time() - self.time_window
        self.server_stats[server]['failures'] = [
            failure_time for failure_time in self.server_stats[server]['failures']
            if failure_time > cutoff_time
        ]
```

#### 2. Active Health Checks
Proactively ping servers to check health.

```python
import asyncio
import aiohttp

class ActiveHealthChecker:
    def __init__(self, servers, check_interval=30):
        self.servers = servers
        self.check_interval = check_interval
        self.server_health = {server: True for server in servers}
        self.running = False

    async def start_health_checks(self):
        """Start background health checking"""
        self.running = True
        while self.running:
            await self._check_all_servers()
            await asyncio.sleep(self.check_interval)

    async def _check_all_servers(self):
        """Check health of all servers concurrently"""
        tasks = [self._check_server_health(server) for server in self.servers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            server = self.servers[i]
            self.server_health[server] = not isinstance(result, Exception) and result

    async def _check_server_health(self, server):
        """Check individual server health"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"http://{server}/health") as response:
                    return response.status == 200
        except Exception:
            return False

    def get_healthy_servers(self):
        """Get list of currently healthy servers"""
        return [server for server, healthy in self.server_health.items() if healthy]
```

### Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open" # Testing if service recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60, success_threshold=3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def _should_attempt_reset(self):
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout

# Usage example
class ExternalServiceClient:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

    def make_api_call(self, data):
        """Make API call with circuit breaker protection"""
        return self.circuit_breaker.call(self._actual_api_call, data)

    def _actual_api_call(self, data):
        # Actual implementation of API call
        # This would make HTTP request to external service
        pass
```

## 🏗️ Designing for Reliability

### 1. Idempotency

Ensure operations can be safely retried without side effects.

```python
class IdempotentOperationHandler:
    def __init__(self, cache):
        self.cache = cache

    def process_payment(self, payment_request):
        """Idempotent payment processing"""
        idempotency_key = payment_request.get('idempotency_key')
        if not idempotency_key:
            raise ValueError("Idempotency key required")

        # Check if already processed
        cached_result = self.cache.get(f"payment:{idempotency_key}")
        if cached_result:
            return cached_result

        # Process payment
        result = self._process_payment_internal(payment_request)

        # Cache result for future requests
        self.cache.set(f"payment:{idempotency_key}", result, ttl=3600)

        return result

    def _process_payment_internal(self, payment_request):
        # Actual payment processing logic
        pass
```

### 2. Retry with Exponential Backoff

```python
import time
import random

class RetryHandler:
    def __init__(self, max_retries=3, base_delay=1, max_delay=60):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (ConnectionError, TimeoutError) as e:
                last_exception = e

                if attempt == self.max_retries:
                    break  # No more retries

                # Calculate delay with exponential backoff and jitter
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                jitter = random.uniform(0, 0.1) * delay  # Add 10% jitter
                total_delay = delay + jitter

                print(f"Attempt {attempt + 1} failed, retrying in {total_delay:.2f}s")
                time.sleep(total_delay)

        # All retries exhausted
        raise last_exception

# Usage
retry_handler = RetryHandler(max_retries=3, base_delay=1)

def unreliable_api_call():
    # Simulated unreliable operation
    if random.random() < 0.7:  # 70% failure rate
        raise ConnectionError("Network error")
    return "Success"

try:
    result = retry_handler.execute_with_retry(unreliable_api_call)
    print(f"Operation succeeded: {result}")
except Exception as e:
    print(f"Operation failed after all retries: {e}")
```

### 3. Bulkhead Pattern

Isolate different parts of the system to prevent cascade failures.

```python
import threading
from concurrent.futures import ThreadPoolExecutor
import queue

class BulkheadExecutor:
    def __init__(self, pool_configs):
        """
        pool_configs = {
            'critical': {'max_workers': 10, 'queue_size': 100},
            'normal': {'max_workers': 5, 'queue_size': 50},
            'batch': {'max_workers': 2, 'queue_size': 20}
        }
        """
        self.pools = {}
        for pool_name, config in pool_configs.items():
            self.pools[pool_name] = ThreadPoolExecutor(
                max_workers=config['max_workers']
            )

    def submit_task(self, pool_name, func, *args, **kwargs):
        """Submit task to specific resource pool"""
        if pool_name not in self.pools:
            raise ValueError(f"Unknown pool: {pool_name}")

        return self.pools[pool_name].submit(func, *args, **kwargs)

    def shutdown(self):
        """Shutdown all pools"""
        for pool in self.pools.values():
            pool.shutdown(wait=True)

# Usage
bulkhead = BulkheadExecutor({
    'user_requests': {'max_workers': 10, 'queue_size': 100},
    'admin_requests': {'max_workers': 5, 'queue_size': 50},
    'background_jobs': {'max_workers': 2, 'queue_size': 20}
})

# Submit tasks to isolated pools
user_future = bulkhead.submit_task('user_requests', process_user_request, request_data)
admin_future = bulkhead.submit_task('admin_requests', process_admin_request, admin_data)
```

## 📊 Disaster Recovery

### Recovery Time Objectives

#### RTO (Recovery Time Objective)
Maximum acceptable time to restore service after a disaster.

#### RPO (Recovery Point Objective)
Maximum acceptable amount of data loss measured in time.

```python
class DisasterRecoveryPlan:
    def __init__(self, rto_minutes=60, rpo_minutes=15):
        self.rto = rto_minutes  # Must restore service within 60 minutes
        self.rpo = rpo_minutes  # Can lose at most 15 minutes of data

    def calculate_backup_frequency(self):
        """Determine backup frequency based on RPO"""
        # Backup more frequently than RPO to ensure we meet the objective
        return max(1, self.rpo // 2)  # Backup every 7.5 minutes for 15-minute RPO

    def validate_recovery_plan(self, actual_recovery_time, data_loss_minutes):
        """Validate if recovery met objectives"""
        rto_met = actual_recovery_time <= self.rto
        rpo_met = data_loss_minutes <= self.rpo

        return {
            'rto_met': rto_met,
            'rpo_met': rpo_met,
            'passed': rto_met and rpo_met
        }
```

### Backup and Restore Strategies

```python
class BackupStrategy:
    def __init__(self, database, storage):
        self.database = database
        self.storage = storage

    def full_backup(self):
        """Complete database backup"""
        backup_data = self.database.export_all_data()
        backup_id = f"full_backup_{int(time.time())}"
        self.storage.store(backup_id, backup_data)
        return backup_id

    def incremental_backup(self, last_backup_timestamp):
        """Backup only changes since last backup"""
        changes = self.database.get_changes_since(last_backup_timestamp)
        backup_id = f"incremental_backup_{int(time.time())}"
        self.storage.store(backup_id, changes)
        return backup_id

    def restore_from_backup(self, backup_id):
        """Restore database from backup"""
        backup_data = self.storage.retrieve(backup_id)
        self.database.restore_from_data(backup_data)

    def point_in_time_recovery(self, target_timestamp):
        """Restore to specific point in time"""
        # Find latest full backup before target time
        full_backup = self._find_latest_full_backup(target_timestamp)

        # Apply incremental backups up to target time
        incremental_backups = self._find_incremental_backups(
            full_backup.timestamp, target_timestamp
        )

        # Restore full backup
        self.restore_from_backup(full_backup.id)

        # Apply incremental changes
        for incremental in incremental_backups:
            self._apply_incremental_backup(incremental)
```

## ✅ Knowledge Check

After studying this section, you should be able to:

- [ ] Calculate system availability and understand the cost of "nines"
- [ ] Distinguish between reliability and availability
- [ ] Implement health checks and circuit breakers
- [ ] Design redundant systems with proper failover mechanisms
- [ ] Create disaster recovery plans with RTO/RPO objectives
- [ ] Handle failures gracefully using various fault tolerance patterns

## 🔄 Quick Review Questions

1. **What's the difference between 99.9% and 99.99% availability in terms of downtime?**
2. **When would you use Active-Passive vs Active-Active redundancy?**
3. **How does a circuit breaker pattern help with system reliability?**
4. **What's the trade-off between RTO and cost in disaster recovery?**
5. **Why is idempotency important for reliability?**

## 🚀 Next Steps

- Study [Consistency Patterns](consistency-patterns.md) to understand data consistency in reliable systems
- Learn [Database Concepts](database-concepts.md) for reliable data storage
- Practice designing reliable systems in [Real-World Examples](../04-real-world-examples/)

---

**Remember**: Perfect reliability is impossible and infinitely expensive. The goal is to understand the trade-offs and design systems that meet your specific reliability and availability requirements cost-effectively!