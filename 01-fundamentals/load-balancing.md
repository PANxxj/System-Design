# Load Balancing 🟢

## 🎯 Learning Objectives
- Understand different load balancing algorithms
- Learn when to use Layer 4 vs Layer 7 load balancers
- Implement health checks and failover mechanisms
- Design load balancing strategies for different scenarios

## 📖 What is Load Balancing?

**Load balancing** distributes incoming requests across multiple servers to ensure:
- No single server becomes overwhelmed
- High availability through redundancy
- Improved response times
- Better resource utilization

### Why Load Balancing Matters
- **Prevents bottlenecks**: Distributes traffic evenly
- **Increases availability**: If one server fails, others continue serving
- **Enables scaling**: Add more servers to handle more traffic
- **Improves performance**: Reduces response times

## ⚖️ Load Balancing Algorithms

### 1. Round Robin
Distributes requests sequentially across servers.

```python
class RoundRobinBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.current = 0

    def get_server(self):
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server

# Usage
balancer = RoundRobinBalancer(['server1', 'server2', 'server3'])
print(balancer.get_server())  # server1
print(balancer.get_server())  # server2
print(balancer.get_server())  # server3
print(balancer.get_server())  # server1 (cycles back)
```

**Pros:**
- ✅ Simple to implement
- ✅ Equal distribution (assuming equal server capacity)
- ✅ No server state needed

**Cons:**
- ❌ Doesn't consider server capacity differences
- ❌ Doesn't account for request complexity
- ❌ May overload slower servers

**Best for:** Servers with equal capacity and similar request types

### 2. Weighted Round Robin
Assigns different weights to servers based on their capacity.

```python
class WeightedRoundRobinBalancer:
    def __init__(self, servers_with_weights):
        # servers_with_weights = [("server1", 3), ("server2", 2), ("server3", 1)]
        self.servers = []
        for server, weight in servers_with_weights:
            self.servers.extend([server] * weight)
        self.current = 0

    def get_server(self):
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server

# Usage
balancer = WeightedRoundRobinBalancer([
    ("high_capacity_server", 5),
    ("medium_capacity_server", 3),
    ("low_capacity_server", 1)
])
```

**Best for:** Servers with different capacities or performance characteristics

### 3. Least Connections
Routes requests to the server with the fewest active connections.

```python
class LeastConnectionsBalancer:
    def __init__(self, servers):
        self.servers = {server: 0 for server in servers}

    def get_server(self):
        return min(self.servers, key=self.servers.get)

    def connection_started(self, server):
        self.servers[server] += 1

    def connection_ended(self, server):
        self.servers[server] -= 1

# Usage
balancer = LeastConnectionsBalancer(['server1', 'server2', 'server3'])
server = balancer.get_server()
balancer.connection_started(server)
# ... handle request ...
balancer.connection_ended(server)
```

**Best for:** Applications with varying request processing times

### 4. Weighted Least Connections
Combines least connections with server capacity weights.

```python
class WeightedLeastConnectionsBalancer:
    def __init__(self, servers_with_weights):
        self.servers = {server: {"weight": weight, "connections": 0}
                       for server, weight in servers_with_weights}

    def get_server(self):
        # Calculate ratio: connections / weight
        ratios = {server: info["connections"] / info["weight"]
                 for server, info in self.servers.items()}
        return min(ratios, key=ratios.get)

    def connection_started(self, server):
        self.servers[server]["connections"] += 1

    def connection_ended(self, server):
        self.servers[server]["connections"] -= 1
```

### 5. IP Hash
Routes requests based on client IP hash.

```python
import hashlib

class IPHashBalancer:
    def __init__(self, servers):
        self.servers = servers

    def get_server(self, client_ip):
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        return self.servers[hash_value % len(self.servers)]

# Usage
balancer = IPHashBalancer(['server1', 'server2', 'server3'])
server = balancer.get_server('192.168.1.100')  # Always same server
```

**Pros:**
- ✅ Session persistence (same client → same server)
- ✅ Good for stateful applications

**Cons:**
- ❌ Uneven distribution if IPs not diverse
- ❌ Difficult to handle server failures

### 6. Random
Selects servers randomly.

```python
import random

class RandomBalancer:
    def __init__(self, servers):
        self.servers = servers

    def get_server(self):
        return random.choice(self.servers)
```

**Best for:** Simple applications where other algorithms are overkill

## 🏗️ Load Balancer Types

### Layer 4 (Transport Layer) Load Balancer

Routes traffic based on IP addresses and ports (TCP/UDP level).

```python
class Layer4LoadBalancer:
    def __init__(self, backend_servers):
        self.backend_servers = backend_servers
        self.algorithm = RoundRobinBalancer(backend_servers)

    def route_request(self, client_ip, client_port, dest_ip, dest_port):
        """Route based on network information only"""
        backend_server = self.algorithm.get_server()

        # Forward TCP/UDP packet to backend server
        return {
            'backend_server': backend_server,
            'client_ip': client_ip,
            'client_port': client_port
        }
```

**Characteristics:**
- ✅ **Fast**: Minimal processing overhead
- ✅ **Secure**: Cannot see application data
- ✅ **Protocol agnostic**: Works with any TCP/UDP traffic
- ❌ **Limited routing**: Cannot make decisions based on content

**Use cases:**
- High-throughput applications
- Non-HTTP protocols
- Simple traffic distribution

### Layer 7 (Application Layer) Load Balancer

Routes traffic based on application data (HTTP headers, URLs, cookies).

```python
class Layer7LoadBalancer:
    def __init__(self):
        self.routes = {}
        self.default_balancer = RoundRobinBalancer(['default1', 'default2'])

    def add_route(self, pattern, servers):
        self.routes[pattern] = RoundRobinBalancer(servers)

    def route_request(self, http_request):
        """Route based on HTTP content"""
        path = http_request.get('path', '/')

        # Route API requests to API servers
        if path.startswith('/api/'):
            if '/api/users' in self.routes:
                return self.routes['/api/users'].get_server()

        # Route static content to CDN
        if path.startswith('/static/'):
            return 'cdn.example.com'

        # Default routing
        return self.default_balancer.get_server()

# Usage
lb = Layer7LoadBalancer()
lb.add_route('/api/users', ['user-service-1', 'user-service-2'])
lb.add_route('/api/orders', ['order-service-1', 'order-service-2'])

request = {'path': '/api/users/123', 'method': 'GET'}
server = lb.route_request(request)
```

**Advanced Layer 7 Features:**
```python
class AdvancedLayer7LoadBalancer:
    def route_request(self, http_request):
        # Route based on user type
        if http_request.get('headers', {}).get('X-User-Type') == 'premium':
            return 'premium-server-pool'

        # Route based on geographical location
        if http_request.get('headers', {}).get('CF-IPCountry') == 'US':
            return 'us-server-pool'

        # Route based on device type
        user_agent = http_request.get('headers', {}).get('User-Agent', '')
        if 'Mobile' in user_agent:
            return 'mobile-optimized-servers'

        # A/B testing routing
        if hash(http_request.get('session_id', '')) % 100 < 10:
            return 'experimental-feature-servers'

        return 'default-servers'
```

**Characteristics:**
- ✅ **Intelligent routing**: Content-based decisions
- ✅ **Advanced features**: SSL termination, compression, caching
- ✅ **Application awareness**: Can modify requests/responses
- ❌ **Higher overhead**: More processing required
- ❌ **Protocol specific**: Typically HTTP/HTTPS only

## 🏥 Health Checks and Failover

### Health Check Implementation

```python
import time
import requests
from threading import Thread

class HealthChecker:
    def __init__(self, servers, check_interval=30):
        self.servers = servers
        self.healthy_servers = set(servers)
        self.check_interval = check_interval
        self.running = True

    def start_health_checks(self):
        Thread(target=self._health_check_loop, daemon=True).start()

    def _health_check_loop(self):
        while self.running:
            for server in self.servers:
                if self._check_server_health(server):
                    self.healthy_servers.add(server)
                else:
                    self.healthy_servers.discard(server)

            time.sleep(self.check_interval)

    def _check_server_health(self, server):
        try:
            # HTTP health check
            response = requests.get(f"http://{server}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_healthy_servers(self):
        return list(self.healthy_servers)

class HealthAwareLoadBalancer:
    def __init__(self, servers):
        self.all_servers = servers
        self.health_checker = HealthChecker(servers)
        self.health_checker.start_health_checks()
        self.balancer = RoundRobinBalancer(servers)

    def get_server(self):
        healthy_servers = self.health_checker.get_healthy_servers()
        if not healthy_servers:
            raise Exception("No healthy servers available")

        # Update balancer with only healthy servers
        self.balancer.servers = healthy_servers
        return self.balancer.get_server()
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
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def _should_attempt_reset(self):
        return (time.time() - self.last_failure_time) >= self.timeout
```

## 🌐 Load Balancer Placement Strategies

### 1. Single Load Balancer
```
[Internet] → [Load Balancer] → [Server 1]
                             → [Server 2]
                             → [Server 3]
```

**Pros:** Simple setup
**Cons:** Single point of failure

### 2. Multiple Load Balancers with Failover
```
[Internet] → [Primary LB] → [Servers]
           → [Backup LB]  → [Servers]
```

### 3. Geographic Distribution
```
[Global DNS] → [US Load Balancer] → [US Servers]
             → [EU Load Balancer] → [EU Servers]
             → [Asia Load Balancer] → [Asia Servers]
```

### 4. Hierarchical Load Balancing
```
[Internet] → [Global LB] → [Regional LB 1] → [Local LB] → [Servers]
                         → [Regional LB 2] → [Local LB] → [Servers]
```

## 🛠️ Practical Implementation

### Simple HTTP Load Balancer in Python

```python
import socket
import threading
import time
from urllib.parse import urlparse

class SimpleLoadBalancer:
    def __init__(self, port, backend_servers):
        self.port = port
        self.backend_servers = backend_servers
        self.balancer = RoundRobinBalancer(backend_servers)
        self.health_checker = HealthChecker(backend_servers)

    def start(self):
        self.health_checker.start_health_checks()

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(5)

        print(f"Load balancer listening on port {self.port}")

        while True:
            client_socket, address = server_socket.accept()
            thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket,)
            )
            thread.start()

    def handle_client(self, client_socket):
        try:
            # Get a healthy backend server
            healthy_servers = self.health_checker.get_healthy_servers()
            if not healthy_servers:
                self.send_error_response(client_socket, 503)
                return

            backend_server = self.balancer.get_server()

            # Forward request to backend server
            self.forward_request(client_socket, backend_server)

        finally:
            client_socket.close()

    def forward_request(self, client_socket, backend_server):
        # Implementation would forward HTTP request to backend
        # and return response to client
        pass

    def send_error_response(self, client_socket, status_code):
        response = f"HTTP/1.1 {status_code} Service Unavailable\r\n\r\n"
        client_socket.send(response.encode())

# Usage
if __name__ == "__main__":
    backend_servers = ['127.0.0.1:8001', '127.0.0.1:8002', '127.0.0.1:8003']
    lb = SimpleLoadBalancer(8000, backend_servers)
    lb.start()
```

## 🚀 Advanced Features

### Session Persistence (Sticky Sessions)

```python
class StickySessionBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.session_map = {}  # session_id -> server
        self.balancer = RoundRobinBalancer(servers)

    def get_server(self, session_id=None):
        if session_id and session_id in self.session_map:
            return self.session_map[session_id]

        # New session or no session_id
        server = self.balancer.get_server()
        if session_id:
            self.session_map[session_id] = server

        return server
```

### SSL Termination

```python
class SSLTerminatingLoadBalancer:
    def __init__(self, ssl_cert_path, ssl_key_path, backend_servers):
        self.ssl_cert_path = ssl_cert_path
        self.ssl_key_path = ssl_key_path
        self.backend_servers = backend_servers

    def handle_https_request(self, encrypted_request):
        # 1. Decrypt HTTPS request
        decrypted_request = self.decrypt_ssl(encrypted_request)

        # 2. Route to backend server (HTTP)
        backend_server = self.get_backend_server()
        response = self.forward_http_request(backend_server, decrypted_request)

        # 3. Encrypt response
        encrypted_response = self.encrypt_ssl(response)

        return encrypted_response
```

## 📊 Performance Considerations

### Load Balancer Metrics

```python
class LoadBalancerMetrics:
    def __init__(self):
        self.request_count = 0
        self.response_times = []
        self.error_count = 0
        self.server_utilization = {}

    def record_request(self, server, response_time, success):
        self.request_count += 1
        self.response_times.append(response_time)

        if not success:
            self.error_count += 1

        if server not in self.server_utilization:
            self.server_utilization[server] = 0
        self.server_utilization[server] += 1

    def get_average_response_time(self):
        return sum(self.response_times) / len(self.response_times)

    def get_error_rate(self):
        return self.error_count / self.request_count

    def get_throughput(self, time_window_seconds):
        return self.request_count / time_window_seconds
```

## ✅ Knowledge Check

After studying this section, you should be able to:

- [ ] Choose the appropriate load balancing algorithm for different scenarios
- [ ] Understand the trade-offs between Layer 4 and Layer 7 load balancing
- [ ] Implement health checks and handle server failures
- [ ] Design load balancing strategies for high availability
- [ ] Calculate load balancer capacity requirements

## 🔄 Quick Review Questions

1. **When would you use Weighted Round Robin over Round Robin?**
2. **What's the main advantage of Least Connections algorithm?**
3. **Why might you choose Layer 4 over Layer 7 load balancing?**
4. **How do you handle session persistence in a stateless architecture?**
5. **What's the difference between active and passive health checks?**

## 🚀 Next Steps

- Study [Caching Strategies](caching-strategies.md) to complement load balancing
- Learn about [Database Concepts](database-concepts.md) for backend scaling
- Practice designing load balancing for [Real-World Examples](../04-real-world-examples/)

---

**Remember**: Load balancing is just one piece of the scalability puzzle. Combine it with caching, database optimization, and proper architecture for maximum effectiveness!