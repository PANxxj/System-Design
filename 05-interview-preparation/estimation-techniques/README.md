# Estimation Techniques for System Design 🟡

## 🎯 Learning Objectives
- Master back-of-envelope calculations for system design
- Learn capacity estimation techniques
- Understand performance metrics and scaling factors
- Practice real-world estimation scenarios

## 📐 Fundamental Estimation Principles

### Core Numbers Every Engineer Should Know

```python
import math
from typing import Dict, Tuple, List
from dataclasses import dataclass
from enum import Enum

class TimeUnit(Enum):
    NANOSECOND = 1e-9
    MICROSECOND = 1e-6
    MILLISECOND = 1e-3
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    MONTH = 2592000  # 30 days
    YEAR = 31536000  # 365 days

class StorageUnit(Enum):
    BYTE = 1
    KILOBYTE = 1024
    MEGABYTE = 1024 ** 2
    GIGABYTE = 1024 ** 3
    TERABYTE = 1024 ** 4
    PETABYTE = 1024 ** 5

@dataclass
class SystemNumbers:
    """
    Essential numbers for system design calculations
    """
    # Latency (seconds)
    l1_cache_read = 0.5e-9          # 0.5 ns
    branch_mispredict = 5e-9        # 5 ns
    l2_cache_read = 7e-9            # 7 ns
    mutex_lock_unlock = 25e-9       # 25 ns
    main_memory_read = 100e-9       # 100 ns
    compress_1kb = 3e-6             # 3 μs
    ssd_read_4kb = 150e-6          # 150 μs
    memory_read_1mb = 250e-6       # 250 μs
    ssd_read_1mb = 1e-3            # 1 ms
    disk_seek = 10e-3              # 10 ms
    disk_read_1mb = 20e-3          # 20 ms
    packet_roundtrip_ca_nl = 150e-3 # 150 ms (CA to Netherlands)

    # Throughput
    gigabit_ethernet = 125 * 1024 * 1024    # 125 MB/s
    ssd_sequential_read = 500 * 1024 * 1024  # 500 MB/s
    main_memory_bandwidth = 4 * 1024 * 1024 * 1024  # 4 GB/s

    # Scale factors
    requests_per_user_per_day = 100
    avg_web_page_size = 2 * 1024 * 1024  # 2 MB
    avg_mobile_image = 200 * 1024        # 200 KB
    avg_tweet_size = 300                 # 300 bytes

class EstimationCalculator:
    """
    Calculator for system design estimations
    """

    def __init__(self):
        self.numbers = SystemNumbers()

    def calculate_storage_requirements(self,
                                    users: int,
                                    data_per_user_per_day: int,
                                    retention_days: int = 365,
                                    replication_factor: int = 3) -> Dict[str, float]:
        """
        Calculate storage requirements for a system

        Args:
            users: Number of users
            data_per_user_per_day: Data generated per user per day (bytes)
            retention_days: How long to keep data
            replication_factor: Number of replicas for redundancy
        """
        daily_data = users * data_per_user_per_day
        total_data = daily_data * retention_days
        total_with_replication = total_data * replication_factor

        return {
            'daily_data_gb': daily_data / StorageUnit.GIGABYTE.value,
            'total_data_tb': total_data / StorageUnit.TERABYTE.value,
            'total_with_replication_tb': total_with_replication / StorageUnit.TERABYTE.value,
            'monthly_growth_gb': (daily_data * 30) / StorageUnit.GIGABYTE.value
        }

    def calculate_bandwidth_requirements(self,
                                       daily_active_users: int,
                                       requests_per_user: int,
                                       avg_request_size: int,
                                       avg_response_size: int,
                                       peak_factor: float = 3.0) -> Dict[str, float]:
        """
        Calculate bandwidth requirements

        Args:
            daily_active_users: Number of daily active users
            requests_per_user: Average requests per user per day
            avg_request_size: Average request size in bytes
            avg_response_size: Average response size in bytes
            peak_factor: Peak traffic multiplier
        """
        # Calculate daily traffic
        daily_requests = daily_active_users * requests_per_user
        daily_ingress = daily_requests * avg_request_size
        daily_egress = daily_requests * avg_response_size

        # Calculate per-second averages
        avg_rps = daily_requests / TimeUnit.DAY.value
        avg_ingress_bps = daily_ingress / TimeUnit.DAY.value
        avg_egress_bps = daily_egress / TimeUnit.DAY.value

        # Calculate peak requirements
        peak_rps = avg_rps * peak_factor
        peak_ingress_mbps = (avg_ingress_bps * peak_factor) / (1024 * 1024)
        peak_egress_mbps = (avg_egress_bps * peak_factor) / (1024 * 1024)

        return {
            'avg_requests_per_second': round(avg_rps, 2),
            'peak_requests_per_second': round(peak_rps, 2),
            'avg_ingress_mbps': round(avg_ingress_mbps, 2),
            'avg_egress_mbps': round(avg_egress_mbps, 2),
            'peak_ingress_mbps': round(peak_ingress_mbps, 2),
            'peak_egress_mbps': round(peak_egress_mbps, 2),
            'daily_data_transfer_gb': (daily_ingress + daily_egress) / StorageUnit.GIGABYTE.value
        }

    def calculate_server_requirements(self,
                                    peak_rps: float,
                                    server_capacity_rps: float = 1000,
                                    cpu_intensive: bool = False,
                                    safety_margin: float = 1.5) -> Dict[str, int]:
        """
        Calculate server requirements

        Args:
            peak_rps: Peak requests per second
            server_capacity_rps: Requests per second one server can handle
            cpu_intensive: Whether the workload is CPU intensive
            safety_margin: Safety margin multiplier
        """
        if cpu_intensive:
            server_capacity_rps *= 0.5  # Reduce capacity for CPU-intensive tasks

        base_servers = math.ceil(peak_rps / server_capacity_rps)
        servers_with_margin = math.ceil(base_servers * safety_margin)

        return {
            'minimum_servers': base_servers,
            'recommended_servers': servers_with_margin,
            'servers_per_az': math.ceil(servers_with_margin / 3),  # 3 AZs
            'total_capacity_rps': servers_with_margin * server_capacity_rps
        }

    def calculate_database_requirements(self,
                                      write_rps: float,
                                      read_rps: float,
                                      data_size_gb: float,
                                      read_write_ratio: float = 10) -> Dict[str, any]:
        """
        Calculate database requirements

        Args:
            write_rps: Write requests per second
            read_rps: Read requests per second
            data_size_gb: Total data size in GB
            read_write_ratio: Read to write ratio
        """
        # Database capacity assumptions
        db_write_capacity = 1000  # writes per second per instance
        db_read_capacity = 5000   # reads per second per instance

        write_instances = math.ceil(write_rps / db_write_capacity)
        read_replicas = math.ceil(read_rps / db_read_capacity)

        # Storage calculations
        storage_with_indexes = data_size_gb * 1.5  # 50% overhead for indexes
        storage_with_replication = storage_with_indexes * 3  # Master + 2 replicas

        return {
            'write_instances': write_instances,
            'read_replicas': read_replicas,
            'total_instances': write_instances + read_replicas,
            'storage_gb': round(storage_with_replication, 2),
            'estimated_iops': write_rps * 3 + read_rps,  # Rough IOPS estimate
            'sharding_needed': data_size_gb > 500  # Shard if > 500GB
        }

    def calculate_cache_requirements(self,
                                   read_rps: float,
                                   avg_object_size: int,
                                   cache_hit_ratio: float = 0.8,
                                   cache_duration_hours: int = 24) -> Dict[str, any]:
        """
        Calculate cache requirements

        Args:
            read_rps: Read requests per second
            avg_object_size: Average cached object size in bytes
            cache_hit_ratio: Expected cache hit ratio
            cache_duration_hours: How long to keep objects in cache
        """
        cache_requests_per_second = read_rps * cache_hit_ratio
        objects_cached_per_hour = cache_requests_per_second * TimeUnit.HOUR.value
        total_objects_in_cache = objects_cached_per_hour * cache_duration_hours

        cache_size_bytes = total_objects_in_cache * avg_object_size
        cache_size_gb = cache_size_bytes / StorageUnit.GIGABYTE.value

        # Redis/Memcached capacity planning
        memory_per_instance = 16  # GB per cache instance
        instances_needed = math.ceil(cache_size_gb / memory_per_instance)

        return {
            'cache_hit_ratio': cache_hit_ratio,
            'cache_rps': round(cache_requests_per_second, 2),
            'cache_size_gb': round(cache_size_gb, 2),
            'cache_instances': instances_needed,
            'memory_efficiency': 0.75,  # 75% memory utilization
            'eviction_policy': 'LRU'
        }

    def estimate_cost(self,
                     servers: int,
                     storage_tb: float,
                     bandwidth_tb_month: float,
                     cache_instances: int = 0) -> Dict[str, float]:
        """
        Rough cost estimation (AWS pricing)

        Args:
            servers: Number of application servers
            storage_tb: Total storage in TB
            bandwidth_tb_month: Monthly bandwidth in TB
            cache_instances: Number of cache instances
        """
        # Rough AWS pricing (as of 2024)
        server_cost_per_month = 100  # per server
        storage_cost_per_tb_month = 20  # per TB
        bandwidth_cost_per_tb = 90  # per TB
        cache_cost_per_instance = 50  # per cache instance

        monthly_cost = (
            servers * server_cost_per_month +
            storage_tb * storage_cost_per_tb_month +
            bandwidth_tb_month * bandwidth_cost_per_tb +
            cache_instances * cache_cost_per_instance
        )

        return {
            'monthly_cost_usd': round(monthly_cost, 2),
            'annual_cost_usd': round(monthly_cost * 12, 2),
            'cost_breakdown': {
                'servers': servers * server_cost_per_month,
                'storage': storage_tb * storage_cost_per_tb_month,
                'bandwidth': bandwidth_tb_month * bandwidth_cost_per_tb,
                'cache': cache_instances * cache_cost_per_instance
            }
        }

# Practical estimation examples
class SystemEstimationExamples:
    """
    Real-world estimation examples for common systems
    """

    def __init__(self):
        self.calculator = EstimationCalculator()

    def estimate_twitter_like_system(self) -> Dict[str, any]:
        """
        Estimate requirements for Twitter-like social media system
        """
        # Assumptions
        total_users = 300_000_000
        daily_active_users = 150_000_000
        tweets_per_user_per_day = 2
        tweet_reads_per_user_per_day = 200
        avg_tweet_size = 300  # bytes
        media_percentage = 0.1  # 10% tweets have media
        avg_media_size = 1024 * 1024  # 1 MB

        # Calculate writes
        daily_tweets = daily_active_users * tweets_per_user_per_day
        tweets_per_second = daily_tweets / TimeUnit.DAY.value
        peak_tweets_per_second = tweets_per_second * 3

        # Calculate reads
        daily_reads = daily_active_users * tweet_reads_per_user_per_day
        reads_per_second = daily_reads / TimeUnit.DAY.value
        peak_reads_per_second = reads_per_second * 5  # Higher read peak

        # Storage calculations
        daily_tweet_storage = daily_tweets * avg_tweet_size
        daily_media_storage = daily_tweets * media_percentage * avg_media_size
        total_daily_storage = daily_tweet_storage + daily_media_storage

        storage_req = self.calculator.calculate_storage_requirements(
            users=total_users,
            data_per_user_per_day=total_daily_storage / daily_active_users,
            retention_days=365 * 5,  # 5 years
            replication_factor=3
        )

        # Bandwidth calculations
        bandwidth_req = self.calculator.calculate_bandwidth_requirements(
            daily_active_users=daily_active_users,
            requests_per_user=tweet_reads_per_user_per_day + tweets_per_user_per_day,
            avg_request_size=500,  # bytes
            avg_response_size=2000,  # bytes including metadata
            peak_factor=5
        )

        # Server requirements
        server_req = self.calculator.calculate_server_requirements(
            peak_rps=bandwidth_req['peak_requests_per_second'],
            server_capacity_rps=2000,
            safety_margin=2.0
        )

        # Database requirements
        db_req = self.calculator.calculate_database_requirements(
            write_rps=peak_tweets_per_second,
            read_rps=peak_reads_per_second,
            data_size_gb=storage_req['total_data_tb'] * 1024
        )

        # Cache requirements
        cache_req = self.calculator.calculate_cache_requirements(
            read_rps=peak_reads_per_second,
            avg_object_size=2000,  # cached tweet with metadata
            cache_hit_ratio=0.8,
            cache_duration_hours=24
        )

        # Cost estimation
        cost_req = self.calculator.estimate_cost(
            servers=server_req['recommended_servers'],
            storage_tb=storage_req['total_with_replication_tb'],
            bandwidth_tb_month=bandwidth_req['daily_data_transfer_gb'] * 30 / 1024,
            cache_instances=cache_req['cache_instances']
        )

        return {
            'system_type': 'Twitter-like Social Media',
            'scale_assumptions': {
                'total_users': total_users,
                'daily_active_users': daily_active_users,
                'tweets_per_day': daily_tweets,
                'reads_per_day': daily_reads
            },
            'performance_requirements': {
                'peak_writes_per_second': round(peak_tweets_per_second, 2),
                'peak_reads_per_second': round(peak_reads_per_second, 2),
                'read_write_ratio': round(peak_reads_per_second / peak_tweets_per_second, 1)
            },
            'storage_requirements': storage_req,
            'bandwidth_requirements': bandwidth_req,
            'server_requirements': server_req,
            'database_requirements': db_req,
            'cache_requirements': cache_req,
            'cost_estimation': cost_req
        }

    def estimate_url_shortener_system(self) -> Dict[str, any]:
        """
        Estimate requirements for URL shortener like bit.ly
        """
        # Assumptions
        daily_url_shortens = 100_000_000  # 100M new URLs per day
        read_write_ratio = 100  # 100:1 read to write
        url_length_avg = 2048  # average URL length
        shortened_url_length = 7  # base62 encoding
        metadata_size = 500  # additional metadata per URL

        # Calculate traffic
        writes_per_second = daily_url_shortens / TimeUnit.DAY.value
        reads_per_second = writes_per_second * read_write_ratio
        peak_writes_per_second = writes_per_second * 2
        peak_reads_per_second = reads_per_second * 5

        # Storage per URL
        storage_per_url = url_length_avg + shortened_url_length + metadata_size
        daily_storage = daily_url_shortens * storage_per_url

        storage_req = self.calculator.calculate_storage_requirements(
            users=1,  # treat as single entity
            data_per_user_per_day=daily_storage,
            retention_days=365 * 5,  # 5 years retention
            replication_factor=3
        )

        bandwidth_req = self.calculator.calculate_bandwidth_requirements(
            daily_active_users=1,
            requests_per_user=daily_url_shortens * (1 + read_write_ratio),
            avg_request_size=url_length_avg,
            avg_response_size=shortened_url_length + 200,  # response overhead
            peak_factor=5
        )

        server_req = self.calculator.calculate_server_requirements(
            peak_rps=bandwidth_req['peak_requests_per_second'],
            server_capacity_rps=10000,  # simple operations, higher capacity
            safety_margin=1.5
        )

        db_req = self.calculator.calculate_database_requirements(
            write_rps=peak_writes_per_second,
            read_rps=peak_reads_per_second,
            data_size_gb=storage_req['total_data_tb'] * 1024
        )

        cache_req = self.calculator.calculate_cache_requirements(
            read_rps=peak_reads_per_second,
            avg_object_size=url_length_avg + 200,
            cache_hit_ratio=0.9,  # Higher cache hit ratio for URL shortener
            cache_duration_hours=24
        )

        cost_req = self.calculator.estimate_cost(
            servers=server_req['recommended_servers'],
            storage_tb=storage_req['total_with_replication_tb'],
            bandwidth_tb_month=bandwidth_req['daily_data_transfer_gb'] * 30 / 1024,
            cache_instances=cache_req['cache_instances']
        )

        return {
            'system_type': 'URL Shortener',
            'scale_assumptions': {
                'daily_new_urls': daily_url_shortens,
                'read_write_ratio': read_write_ratio,
                'url_retention_years': 5
            },
            'performance_requirements': {
                'peak_writes_per_second': round(peak_writes_per_second, 2),
                'peak_reads_per_second': round(peak_reads_per_second, 2),
                'total_urls_5_years': daily_url_shortens * 365 * 5
            },
            'storage_requirements': storage_req,
            'bandwidth_requirements': bandwidth_req,
            'server_requirements': server_req,
            'database_requirements': db_req,
            'cache_requirements': cache_req,
            'cost_estimation': cost_req
        }

    def estimate_video_streaming_system(self) -> Dict[str, any]:
        """
        Estimate requirements for video streaming system like YouTube
        """
        # Assumptions
        total_users = 1_000_000_000  # 1B users
        daily_active_users = 100_000_000  # 100M DAU
        videos_watched_per_user_day = 5
        avg_video_duration_minutes = 10
        video_upload_ratio = 0.001  # 0.1% of users upload daily

        # Video storage assumptions
        video_qualities = {
            '360p': 1 * 1024 * 1024,    # 1 MB per minute
            '720p': 3 * 1024 * 1024,    # 3 MB per minute
            '1080p': 6 * 1024 * 1024,   # 6 MB per minute
            '4K': 25 * 1024 * 1024      # 25 MB per minute
        }

        # Calculate storage for all qualities
        total_video_size_per_minute = sum(video_qualities.values())
        daily_video_uploads = daily_active_users * video_upload_ratio
        daily_video_minutes = daily_video_uploads * avg_video_duration_minutes
        daily_storage = daily_video_minutes * total_video_size_per_minute

        # Calculate streaming bandwidth
        daily_video_views = daily_active_users * videos_watched_per_user_day
        daily_streaming_minutes = daily_video_views * avg_video_duration_minutes
        avg_streaming_bandwidth = 3 * 1024 * 1024  # 3 MB/min average quality

        daily_streaming_data = daily_streaming_minutes * avg_streaming_bandwidth

        storage_req = self.calculator.calculate_storage_requirements(
            users=1,
            data_per_user_per_day=daily_storage,
            retention_days=365 * 10,  # 10 years retention
            replication_factor=3
        )

        # Bandwidth for video streaming is different
        peak_concurrent_viewers = daily_active_users * 0.1  # 10% peak concurrency
        peak_bandwidth_bps = peak_concurrent_viewers * (avg_streaming_bandwidth / 60)  # per second

        server_req = self.calculator.calculate_server_requirements(
            peak_rps=daily_video_views / TimeUnit.DAY.value * 10,  # 10x peak factor
            server_capacity_rps=500,  # Lower due to video processing overhead
            safety_margin=2.0
        )

        # CDN requirements for video streaming
        cdn_storage_tb = storage_req['total_data_tb'] * 0.3  # 30% of content cached at edge
        monthly_bandwidth_tb = (daily_streaming_data * 30) / StorageUnit.TERABYTE.value

        cost_req = self.calculator.estimate_cost(
            servers=server_req['recommended_servers'],
            storage_tb=storage_req['total_with_replication_tb'],
            bandwidth_tb_month=monthly_bandwidth_tb,
            cache_instances=50  # Large CDN cache deployment
        )

        # Add CDN costs (major cost for video streaming)
        cost_req['monthly_cost_usd'] += cdn_storage_tb * 30  # CDN storage cost
        cost_req['monthly_cost_usd'] += monthly_bandwidth_tb * 120  # CDN bandwidth cost

        return {
            'system_type': 'Video Streaming Platform',
            'scale_assumptions': {
                'total_users': total_users,
                'daily_active_users': daily_active_users,
                'daily_video_uploads': daily_video_uploads,
                'daily_video_views': daily_video_views
            },
            'performance_requirements': {
                'peak_concurrent_viewers': peak_concurrent_viewers,
                'peak_bandwidth_gbps': round(peak_bandwidth_bps / (1024**3), 2),
                'storage_growth_tb_day': round(daily_storage / StorageUnit.TERABYTE.value, 2)
            },
            'storage_requirements': storage_req,
            'server_requirements': server_req,
            'cdn_requirements': {
                'edge_storage_tb': round(cdn_storage_tb, 2),
                'monthly_bandwidth_tb': round(monthly_bandwidth_tb, 2),
                'edge_locations_needed': 200
            },
            'cost_estimation': cost_req
        }

# Usage example and testing
def run_estimation_examples():
    """
    Run all estimation examples and display results
    """
    estimator = SystemEstimationExamples()

    print("🐦 TWITTER-LIKE SYSTEM ESTIMATION")
    print("=" * 50)
    twitter_est = estimator.estimate_twitter_like_system()
    print(f"Peak Reads/sec: {twitter_est['performance_requirements']['peak_reads_per_second']:,}")
    print(f"Peak Writes/sec: {twitter_est['performance_requirements']['peak_writes_per_second']:,}")
    print(f"Storage (5 years): {twitter_est['storage_requirements']['total_with_replication_tb']:.1f} TB")
    print(f"Servers needed: {twitter_est['server_requirements']['recommended_servers']}")
    print(f"Monthly cost: ${twitter_est['cost_estimation']['monthly_cost_usd']:,.0f}")

    print("\n🔗 URL SHORTENER SYSTEM ESTIMATION")
    print("=" * 50)
    url_est = estimator.estimate_url_shortener_system()
    print(f"Peak Reads/sec: {url_est['performance_requirements']['peak_reads_per_second']:,}")
    print(f"Peak Writes/sec: {url_est['performance_requirements']['peak_writes_per_second']:,}")
    print(f"Storage (5 years): {url_est['storage_requirements']['total_with_replication_tb']:.1f} TB")
    print(f"Servers needed: {url_est['server_requirements']['recommended_servers']}")
    print(f"Monthly cost: ${url_est['cost_estimation']['monthly_cost_usd']:,.0f}")

    print("\n📺 VIDEO STREAMING SYSTEM ESTIMATION")
    print("=" * 50)
    video_est = estimator.estimate_video_streaming_system()
    print(f"Peak Concurrent Viewers: {video_est['performance_requirements']['peak_concurrent_viewers']:,}")
    print(f"Peak Bandwidth: {video_est['performance_requirements']['peak_bandwidth_gbps']} Gbps")
    print(f"Storage (10 years): {video_est['storage_requirements']['total_with_replication_tb']:.1f} TB")
    print(f"Monthly CDN Bandwidth: {video_est['cdn_requirements']['monthly_bandwidth_tb']:.1f} TB")
    print(f"Monthly cost: ${video_est['cost_estimation']['monthly_cost_usd']:,.0f}")

if __name__ == "__main__":
    run_estimation_examples()
```

## 🎯 Estimation Strategies and Patterns

### 1. **The Power of 10 Rule**
- Always think in powers of 10 for initial estimates
- 10^6 = 1 Million, 10^9 = 1 Billion, 10^12 = 1 Trillion
- Use this for quick sanity checks

### 2. **80/20 Rule Applications**
- 80% of traffic comes from 20% of users
- 80% of data is accessed 20% of the time
- 80% of requests hit 20% of the cache

### 3. **Safety Margins**
- Always add 50-100% safety margin for production systems
- Peak traffic can be 10x average traffic
- Plan for 3-5 years of growth

### 4. **Common Ratios**
- Read:Write ratios: 100:1 (social media), 10:1 (typical web app)
- Cache hit ratios: 80-95% depending on access patterns
- Peak to average traffic: 3-10x depending on use case

## 📊 Quick Reference Tables

### Latency Numbers
| Operation | Latency |
|-----------|---------|
| L1 cache reference | 0.5 ns |
| Branch mispredict | 5 ns |
| L2 cache reference | 7 ns |
| Main memory reference | 100 ns |
| SSD read (4KB) | 150 μs |
| Disk read (4KB) | 10 ms |
| Internet round trip (US) | 150 ms |

### Throughput Numbers
| System | Throughput |
|--------|------------|
| Gigabit Ethernet | 125 MB/s |
| SSD sequential read | 500 MB/s |
| Disk sequential read | 100 MB/s |
| Main memory bandwidth | 4 GB/s |

### Availability Numbers
| Availability | Downtime/Year | Downtime/Month |
|--------------|---------------|----------------|
| 99% | 3.65 days | 7.31 hours |
| 99.9% | 8.77 hours | 43.83 minutes |
| 99.99% | 52.60 minutes | 4.38 minutes |
| 99.999% | 5.26 minutes | 26.30 seconds |

## 🧮 Estimation Techniques

### 1. **Bottom-Up Approach**
```python
# Start with individual components and build up
user_requests = 1000  # per second
avg_response_size = 2048  # bytes
bandwidth_needed = user_requests * avg_response_size  # bytes/sec
```

### 2. **Top-Down Approach**
```python
# Start with total system requirements and break down
total_users = 1_000_000
active_ratio = 0.1  # 10% daily active
daily_active = total_users * active_ratio
peak_concurrent = daily_active * 0.05  # 5% peak concurrency
```

### 3. **Comparative Analysis**
```python
# Compare with known systems
# Twitter: 500M users, 6000 tweets/sec peak
# Your system: 50M users
# Estimated peak: (50M / 500M) * 6000 = 600 tweets/sec
```

## ✅ Estimation Checklist

### Before Starting
- [ ] Clarify the problem scope and requirements
- [ ] Identify key metrics (users, requests, data size)
- [ ] Determine time horizon (current vs 5-year growth)
- [ ] Understand access patterns (read/write ratio)

### During Estimation
- [ ] Start with order-of-magnitude calculations
- [ ] Make reasonable assumptions and state them clearly
- [ ] Consider peak vs average traffic
- [ ] Factor in data replication and safety margins
- [ ] Think about geographic distribution

### After Estimation
- [ ] Sanity check your numbers
- [ ] Compare with known systems
- [ ] Consider bottlenecks and failure points
- [ ] Estimate costs and operational complexity

## 🚀 Practice Problems

### Problem 1: Chat Application
Estimate the requirements for a WhatsApp-like messaging app:
- 1 billion users globally
- 50 messages per user per day average
- 10% of messages include media (images/videos)
- Messages stored for 2 years

### Problem 2: Search Engine
Estimate the requirements for a Google-like search engine:
- 8 billion searches per day globally
- Average query response time < 200ms
- Index 50 billion web pages
- Each page averages 100KB

### Problem 3: Food Delivery App
Estimate the requirements for an Uber Eats-like platform:
- 10 million active users
- 2 orders per user per week
- Real-time location tracking for drivers
- Order history for 5 years

## 🎓 Advanced Topics

### Queuing Theory for Capacity Planning
```python
import math

def calculate_server_utilization(arrival_rate, service_rate):
    """
    Calculate server utilization using M/M/1 queue model
    arrival_rate: requests per second
    service_rate: requests server can handle per second
    """
    utilization = arrival_rate / service_rate
    avg_response_time = 1 / (service_rate - arrival_rate)

    return {
        'utilization': utilization,
        'avg_response_time': avg_response_time,
        'recommended_capacity': service_rate * 1.5  # 50% headroom
    }
```

### Growth Modeling
```python
def project_growth(initial_users, growth_rate_monthly, months):
    """
    Project user growth using compound growth
    """
    return initial_users * ((1 + growth_rate_monthly) ** months)

# Example: 1M users growing at 10% monthly for 2 years
future_users = project_growth(1_000_000, 0.10, 24)
print(f"Projected users in 2 years: {future_users:,.0f}")
```

## ✅ Key Takeaways

1. **Start Simple**: Begin with order-of-magnitude estimates
2. **State Assumptions**: Always clarify your assumptions
3. **Think in Layers**: Storage, compute, network, caching
4. **Consider Peaks**: Plan for peak traffic, not average
5. **Add Margins**: Include safety margins for production
6. **Validate**: Sanity check against known systems
7. **Iterate**: Refine estimates as you learn more

## 🚀 Next Steps

- Practice with [Common Interview Questions](../common-questions/)
- Study [Real-World Examples](../../04-real-world-examples/)
- Learn [Advanced Performance Tuning](../../07-advanced-topics/performance-tuning/)
- Master [Cost Optimization](../../07-advanced-topics/cost-optimization/)