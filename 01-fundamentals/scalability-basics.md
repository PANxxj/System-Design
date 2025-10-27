# Scalability Basics 🟢

## 🎯 Learning Objectives
- Understand vertical vs horizontal scaling
- Learn capacity estimation techniques
- Identify common performance bottlenecks
- Apply scalability patterns effectively

## 📖 What is Scalability?

**Scalability** is the ability of a system to handle increased load gracefully. It's about growing your system's capacity to serve more users, process more data, or handle more transactions without degrading performance.

### Types of Load Growth
1. **User Growth**: More concurrent users
2. **Data Growth**: Larger datasets to process
3. **Feature Growth**: More complex functionality
4. **Geographic Growth**: Users from different regions

## ⚖️ Scaling Strategies

### Vertical Scaling (Scale Up)
Adding more power to existing machines.

```
Before: [4 CPU, 8GB RAM] → After: [8 CPU, 16GB RAM]
```

**Advantages:**
- ✅ Simple implementation - no code changes
- ✅ No distributed system complexity
- ✅ Maintains data consistency easily
- ✅ Existing tools work without modification

**Disadvantages:**
- ❌ Hardware limits (can't scale infinitely)
- ❌ Single point of failure
- ❌ Expensive at high end
- ❌ Downtime required for upgrades

**When to Use:**
- Small to medium applications
- Legacy systems that can't be easily distributed
- When development resources are limited
- Applications with strong consistency requirements

### Horizontal Scaling (Scale Out)
Adding more servers to handle the load.

```
Before: [Server 1] → After: [Server 1] + [Server 2] + [Server 3]
```

**Advantages:**
- ✅ Theoretically unlimited scaling
- ✅ Cost-effective (commodity hardware)
- ✅ Fault tolerant (failure of one server doesn't kill system)
- ✅ Can handle massive loads

**Disadvantages:**
- ❌ Application complexity increases
- ❌ Data consistency challenges
- ❌ Network latency between servers
- ❌ Load distribution complexity

**When to Use:**
- High-growth applications
- Systems requiring high availability
- Applications that can be easily partitioned
- When cost optimization is important

## 🧮 Capacity Estimation

### Back-of-the-Envelope Calculations

Learn these standard numbers for quick estimation:

| Operation | Latency |
|-----------|---------|
| L1 cache reference | 0.5 ns |
| Branch mispredict | 5 ns |
| L2 cache reference | 7 ns |
| Mutex lock/unlock | 25 ns |
| Main memory reference | 100 ns |
| Send 1K bytes over network | 10,000 ns |
| Read 1 MB from memory | 250,000 ns |
| Round trip within datacenter | 500,000 ns |
| Read 1 MB from SSD | 1,000,000 ns |
| Disk seek | 10,000,000 ns |
| Read 1 MB from disk | 20,000,000 ns |
| Send packet CA→Netherlands→CA | 150,000,000 ns |

### Example: Estimation for URL Shortener

**Given Requirements:**
- 500 million URLs created per month
- 100:1 read/write ratio
- 5 years of data retention

**Calculations:**

**Traffic Estimation:**
```
Write QPS: 500M URLs/month ÷ (30 days × 24 hours × 3600 seconds) = ~200 URLs/second
Read QPS: 200 × 100 = 20,000 redirections/second
Peak QPS: 2 × average = 40,000 redirections/second
```

**Storage Estimation:**
```
Total URLs (5 years): 500M × 12 months × 5 = 30 billion URLs
Storage per URL: ~500 bytes (URL + metadata)
Total storage: 30B × 500 bytes = 15 TB
```

**Bandwidth Estimation:**
```
Incoming: 200 writes/sec × 500 bytes = 100 KB/s
Outgoing: 20,000 reads/sec × 500 bytes = 10 MB/s
```

**Memory Estimation (80-20 rule):**
```
Daily read requests: 20K × 24 × 3600 = 1.7 billion
Cache 20% of hot URLs: 1.7B × 0.2 × 500 bytes = 170 GB
```

## 🚧 Common Bottlenecks

### 1. Database Bottlenecks
**Symptoms:**
- Slow query response times
- High CPU usage on database server
- Connection pool exhaustion

**Solutions:**
- Database indexing
- Query optimization
- Read replicas
- Database sharding
- Connection pooling

### 2. Application Server Bottlenecks
**Symptoms:**
- High response times
- Server CPU/Memory maxed out
- Request queuing

**Solutions:**
- Load balancing
- Auto-scaling
- Code optimization
- Caching
- Asynchronous processing

### 3. Network Bottlenecks
**Symptoms:**
- High latency between services
- Bandwidth limitations
- Packet loss

**Solutions:**
- CDN implementation
- Geographic distribution
- Data compression
- Network optimization
- Service colocation

### 4. Storage Bottlenecks
**Symptoms:**
- Slow disk I/O
- Storage space exhaustion
- Backup performance issues

**Solutions:**
- SSD adoption
- Data archiving
- Distributed storage
- Compression
- Storage tiering

## 🏗️ Scalability Patterns

### 1. Load Distribution
```
[Users] → [Load Balancer] → [Server 1]
                          → [Server 2]
                          → [Server 3]
```

### 2. Data Partitioning
```
Users A-H → [Database Shard 1]
Users I-P → [Database Shard 2]
Users Q-Z → [Database Shard 3]
```

### 3. Caching Layers
```
[Client] → [CDN] → [Load Balancer] → [App Server] → [Cache] → [Database]
```

### 4. Asynchronous Processing
```
[User Request] → [Web Server] → [Queue] → [Worker] → [Database]
                              ↓
                    [Immediate Response]
```

## 📊 Scalability Metrics

### Performance Metrics
- **Throughput**: Requests processed per second
- **Latency**: Time to process a single request
- **Response Time**: Total time from request to response
- **Availability**: Percentage of time system is operational

### Scalability Metrics
- **Linear Scalability**: Performance increases proportionally with resources
- **Horizontal Scalability**: Can add more machines effectively
- **Elasticity**: Can scale up and down based on demand

### Example Calculations
```python
# Throughput calculation
def calculate_throughput(total_requests, time_period_seconds):
    return total_requests / time_period_seconds

# Latency percentiles
def calculate_percentiles(response_times):
    sorted_times = sorted(response_times)
    n = len(sorted_times)

    p50 = sorted_times[int(0.5 * n)]   # Median
    p95 = sorted_times[int(0.95 * n)]  # 95th percentile
    p99 = sorted_times[int(0.99 * n)]  # 99th percentile

    return p50, p95, p99

# Availability calculation
def calculate_availability(uptime_hours, total_hours):
    return (uptime_hours / total_hours) * 100
```

## 🛠️ Practical Exercises

### Exercise 1: Capacity Planning
Design capacity for a social media platform:
- 10 million daily active users
- Each user posts 2 times per day
- Each user views 50 posts per day
- Average post size: 1KB

Calculate:
1. Daily write QPS
2. Daily read QPS
3. Storage requirements per year
4. Required bandwidth

### Exercise 2: Bottleneck Identification
Given this system:
```
[Users] → [Load Balancer] → [App Server] → [Database]
```

If the database can handle 1000 QPS but you're receiving 5000 QPS, identify:
1. The bottleneck
2. Three possible solutions
3. Which solution you'd implement first and why

### Exercise 3: Scaling Strategy
Design a scaling strategy for an e-commerce site during Black Friday:
- Normal traffic: 1000 QPS
- Black Friday traffic: 50000 QPS
- Must maintain <100ms response time
- Budget constraints exist

## ✅ Knowledge Check

After studying this section, you should be able to:

- [ ] Explain when to use vertical vs horizontal scaling
- [ ] Perform basic capacity estimation calculations
- [ ] Identify common system bottlenecks
- [ ] Calculate throughput, latency, and availability metrics
- [ ] Apply appropriate scalability patterns to different scenarios

## 🔄 Quick Review

1. **What's the main advantage of horizontal scaling?** (Answer: Fault tolerance and unlimited scaling potential)

2. **If a database can handle 1000 QPS and you need 10000 QPS, what are three solutions?** (Answer: Read replicas, sharding, caching)

3. **How do you calculate the storage needed for 1 million users posting 10 photos/day for 1 year, with each photo being 2MB?** (Answer: 1M × 10 × 365 × 2MB = 7.3 PB)

## 🚀 Next Steps

- Study [Load Balancing](load-balancing.md) to learn about distributing traffic
- Learn [Caching Strategies](caching-strategies.md) to improve performance
- Practice more capacity estimation with real-world examples

---

**Remember**: Scalability is not just about handling more load - it's about maintaining performance, reliability, and cost-effectiveness as your system grows!