# Design a URL Shortener (like bit.ly) 🟢

## 🎯 Problem Statement

"Design a URL shortener service like bit.ly or tinyurl.com that can shorten long URLs and redirect users to the original URL when they click the shortened link."

## 📋 Step 1: Clarify Requirements (5 minutes)

### Questions to Ask
- **Functional Requirements**: What features should the system support?
- **Scale**: How many URLs will be shortened per month?
- **Custom URLs**: Should users be able to create custom short URLs?
- **Analytics**: Do we need click tracking and analytics?
- **Expiration**: Should URLs expire after a certain time?
- **User accounts**: Do users need to register, or can it be anonymous?

### Agreed Requirements

#### Functional Requirements
1. **Shorten URL**: Given a long URL, return a much shorter URL
2. **Redirect**: When someone accesses the short URL, redirect to original URL
3. **Custom Aliases**: Allow users to create custom short URLs (optional)
4. **URL Expiration**: URLs expire after a default time period

#### Non-Functional Requirements
- **Scale**: 100 million URLs generated per month
- **Read/Write Ratio**: 100:1 (more redirects than URL creation)
- **Availability**: 99.9% uptime
- **Latency**: URL redirection should be < 100ms
- **Storage**: URLs should be stored for 5 years

#### Extended Requirements (Nice to Have)
- Analytics and click tracking
- User registration and management
- Rate limiting to prevent abuse

## 🧮 Step 2: Estimate Scale (5 minutes)

### Traffic Estimation
```
URLs created per month: 100 million
URLs created per second: 100M / (30 * 24 * 3600) = ~40 URLs/sec

Read/Write ratio: 100:1
URL redirections per second: 40 * 100 = 4,000 redirections/sec

Peak traffic (assuming 2x): 80 URLs/sec, 8,000 redirections/sec
```

### Storage Estimation
```
URLs to store for 5 years: 100M * 12 * 5 = 6 billion URLs

Storage per URL object:
- Short URL: 7 characters = 7 bytes
- Long URL: 2KB (average)
- Created timestamp: 8 bytes
- Expiration timestamp: 8 bytes
- User ID: 8 bytes
Total: ~2KB per URL object

Total storage: 6B * 2KB = 12TB
```

### Bandwidth Estimation
```
Write requests: 40 URLs/sec * 2KB = 80KB/sec
Read requests: 4,000 redirections/sec * 2KB = 8MB/sec
```

### Memory Estimation
```
Cache 20% of hot URLs: 0.2 * 6B * 2KB = 2.4TB
Daily cache (if we cache for 24 hours):
4,000 redirections/sec * 86,400 sec * 2KB * 0.2 = 138GB
```

## 🔌 Step 3: System Interface (5 minutes)

### API Design

```python
# Shorten URL
POST /api/shorten
Request:
{
    "long_url": "https://www.example.com/very/long/url/path",
    "custom_alias": "my-link",  # optional
    "expiration_date": "2025-12-31T23:59:59Z"  # optional
}

Response:
{
    "short_url": "https://short.ly/abc123",
    "long_url": "https://www.example.com/very/long/url/path",
    "created_at": "2024-10-18T10:30:00Z",
    "expires_at": "2025-10-18T10:30:00Z"
}

# Redirect (handled by web server, not API)
GET /{short_code}
Response: HTTP 302 Redirect to long_url

# Get URL info (optional)
GET /api/info/{short_code}
Response:
{
    "short_url": "https://short.ly/abc123",
    "long_url": "https://www.example.com/very/long/url/path",
    "created_at": "2024-10-18T10:30:00Z",
    "expires_at": "2025-10-18T10:30:00Z",
    "click_count": 1250
}

# Delete URL (optional)
DELETE /api/{short_code}
Response: HTTP 204 No Content
```

## 🏗️ Step 4: High-Level Design (15 minutes)

### Basic Architecture

```
[Client] → [Load Balancer] → [Web Servers] → [Cache] → [Database]
                                          ↓
                                    [URL Encoding Service]
```

### Core Components

1. **Load Balancer**: Distribute incoming requests
2. **Web Servers**: Handle HTTP requests and business logic
3. **URL Encoding Service**: Generate short codes
4. **Cache Layer**: Store frequently accessed URLs
5. **Database**: Persistent storage for URL mappings
6. **Analytics Service**: Track clicks and usage (optional)

### Data Flow

#### URL Shortening Flow
```
1. User submits long URL
2. Web server validates URL
3. Generate unique short code
4. Store mapping in database
5. Cache the mapping
6. Return short URL to user
```

#### URL Redirection Flow
```
1. User clicks short URL
2. Web server extracts short code
3. Check cache for mapping
4. If not in cache, query database
5. Update cache with result
6. Redirect user to long URL
7. Log analytics data (optional)
```

## 🗄️ Step 5: Database Design (10 minutes)

### Database Schema

```sql
-- URL mappings table
CREATE TABLE url_mappings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(7) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    user_id BIGINT NULL,  -- null for anonymous users
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    click_count BIGINT DEFAULT 0,
    INDEX idx_short_code (short_code),
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
);

-- Users table (optional)
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics table (optional)
CREATE TABLE click_analytics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code VARCHAR(7) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    referer TEXT,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_short_code_time (short_code, clicked_at)
);
```

### SQL vs NoSQL Decision

**Choose SQL (PostgreSQL/MySQL) because:**
- ✅ Simple, well-defined schema
- ✅ ACID properties ensure data consistency
- ✅ Strong consistency for URL mappings is important
- ✅ Easy to implement with existing tools
- ✅ Query flexibility for analytics

**NoSQL Alternative (if needed for scale):**
```javascript
// MongoDB/DynamoDB document
{
  "_id": "abc123",  // short_code as primary key
  "long_url": "https://www.example.com/very/long/url",
  "user_id": "user123",
  "created_at": "2024-10-18T10:30:00Z",
  "expires_at": "2025-10-18T10:30:00Z",
  "click_count": 1250
}
```

## 🔧 Step 6: Detailed Component Design (15 minutes)

### URL Encoding Algorithms

#### Base62 Encoding
```python
import random
import string

class Base62Encoder:
    def __init__(self):
        self.alphabet = string.ascii_letters + string.digits  # 62 characters

    def encode(self, number):
        """Convert number to base62 string"""
        if number == 0:
            return self.alphabet[0]

        result = []
        while number > 0:
            result.append(self.alphabet[number % 62])
            number //= 62

        return ''.join(reversed(result))

    def decode(self, encoded):
        """Convert base62 string back to number"""
        number = 0
        for char in encoded:
            number = number * 62 + self.alphabet.index(char)
        return number

# Usage
encoder = Base62Encoder()
short_code = encoder.encode(12345)  # "dnh"
original_number = encoder.decode("dnh")  # 12345
```

#### Counter-Based Approach
```python
class CounterBasedGenerator:
    def __init__(self, database):
        self.db = database
        self.encoder = Base62Encoder()

    def generate_short_code(self):
        """Generate short code using incrementing counter"""
        # Get next counter value atomically
        counter = self.db.increment_counter("url_counter")

        # Encode counter to base62
        short_code = self.encoder.encode(counter)

        # Ensure minimum length (pad with random characters if needed)
        while len(short_code) < 6:
            short_code = random.choice(self.encoder.alphabet) + short_code

        return short_code
```

#### Random String Approach
```python
import random
import string

class RandomGenerator:
    def __init__(self, database):
        self.db = database
        self.alphabet = string.ascii_letters + string.digits

    def generate_short_code(self, length=6):
        """Generate random short code"""
        max_attempts = 10

        for _ in range(max_attempts):
            # Generate random string
            short_code = ''.join(
                random.choice(self.alphabet) for _ in range(length)
            )

            # Check if already exists
            if not self.db.exists(short_code):
                return short_code

        # If we can't find unique code, increase length
        return self.generate_short_code(length + 1)
```

### URL Shortening Service

```python
import hashlib
from datetime import datetime, timedelta

class URLShortenerService:
    def __init__(self, database, cache, code_generator):
        self.db = database
        self.cache = cache
        self.code_generator = code_generator

    def shorten_url(self, long_url, user_id=None, custom_alias=None, expiration_days=365):
        """Shorten a long URL"""
        # Validate URL
        if not self._is_valid_url(long_url):
            raise ValueError("Invalid URL")

        # Check if URL already exists for this user
        existing = self.db.find_existing_url(long_url, user_id)
        if existing and not existing.is_expired():
            return existing.short_code

        # Generate short code
        if custom_alias:
            if self.db.exists(custom_alias):
                raise ValueError("Custom alias already exists")
            short_code = custom_alias
        else:
            short_code = self.code_generator.generate_short_code()

        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=expiration_days)

        # Store in database
        url_mapping = {
            'short_code': short_code,
            'long_url': long_url,
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'expires_at': expires_at,
            'click_count': 0
        }

        self.db.save_url_mapping(url_mapping)

        # Cache the mapping
        self.cache.set(f"url:{short_code}", long_url, ttl=3600)

        return short_code

    def get_long_url(self, short_code):
        """Get long URL from short code"""
        # Check cache first
        cache_key = f"url:{short_code}"
        long_url = self.cache.get(cache_key)

        if long_url:
            # Update click count asynchronously
            self._increment_click_count(short_code)
            return long_url

        # Cache miss - check database
        url_mapping = self.db.get_url_mapping(short_code)

        if not url_mapping:
            raise ValueError("Short URL not found")

        if url_mapping.is_expired():
            raise ValueError("Short URL has expired")

        # Cache the result
        self.cache.set(cache_key, url_mapping.long_url, ttl=3600)

        # Update click count
        self._increment_click_count(short_code)

        return url_mapping.long_url

    def _increment_click_count(self, short_code):
        """Increment click count (can be async)"""
        # This can be done asynchronously to avoid blocking redirect
        self.db.increment_click_count(short_code)

    def _is_valid_url(self, url):
        """Validate URL format"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
```

### Caching Strategy

```python
class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client

    def get_url(self, short_code):
        """Get URL from cache"""
        return self.redis.get(f"url:{short_code}")

    def set_url(self, short_code, long_url, ttl=3600):
        """Cache URL mapping"""
        self.redis.setex(f"url:{short_code}", ttl, long_url)

    def cache_popular_urls(self):
        """Pre-warm cache with popular URLs"""
        popular_urls = self.db.get_most_clicked_urls(limit=10000)

        for url_mapping in popular_urls:
            self.set_url(
                url_mapping.short_code,
                url_mapping.long_url,
                ttl=7200  # 2 hours for popular URLs
            )
```

## ⚡ Step 7: Scale the Design (10 minutes)

### Scaling Challenges

#### 1. Database Bottlenecks

**Read Scaling:**
```
[Application] → [Master DB] (writes)
              → [Read Replica 1] (reads)
              → [Read Replica 2] (reads)
              → [Read Replica 3] (reads)
```

**Write Scaling (Sharding):**
```
Short codes A-H → [Shard 1]
Short codes I-P → [Shard 2]
Short codes Q-Z → [Shard 3]
```

#### 2. Hot URLs Problem

**Solution: Multi-level Caching**
```python
class MultiLevelCache:
    def __init__(self, local_cache, redis_cache, database):
        self.local_cache = local_cache  # In-memory (very fast)
        self.redis_cache = redis_cache  # Distributed cache
        self.database = database

    def get_url(self, short_code):
        # L1: Check local cache
        url = self.local_cache.get(short_code)
        if url:
            return url

        # L2: Check Redis cache
        url = self.redis_cache.get(short_code)
        if url:
            # Promote to L1 cache
            self.local_cache.set(short_code, url, ttl=300)  # 5 minutes
            return url

        # L3: Check database
        url_mapping = self.database.get_url_mapping(short_code)
        if url_mapping:
            # Cache in both levels
            self.redis_cache.set(short_code, url_mapping.long_url, ttl=3600)
            self.local_cache.set(short_code, url_mapping.long_url, ttl=300)
            return url_mapping.long_url

        return None
```

#### 3. Geographic Distribution

```
Global CDN Architecture:
[US Users] → [CDN Edge US] → [US Load Balancer] → [US App Servers]
[EU Users] → [CDN Edge EU] → [EU Load Balancer] → [EU App Servers]
[Asia Users] → [CDN Edge Asia] → [Asia LB] → [Asia App Servers]

All regions share the same database cluster
```

### Advanced Scaling Solutions

#### Microservices Architecture
```
[API Gateway] → [URL Shortening Service] → [URL Database]
              → [Redirect Service] → [Cache Cluster]
              → [Analytics Service] → [Analytics DB]
              → [User Service] → [User Database]
```

#### Database Partitioning Strategy
```python
class ShardManager:
    def __init__(self, shard_configs):
        self.shards = shard_configs

    def get_shard_for_code(self, short_code):
        """Determine which shard contains this short code"""
        # Use first character for simple partitioning
        first_char = short_code[0].lower()

        if first_char in 'abcdefgh':
            return self.shards['shard_1']
        elif first_char in 'ijklmnop':
            return self.shards['shard_2']
        else:
            return self.shards['shard_3']

    def get_shard_for_write(self):
        """Round-robin for writes to distribute load"""
        # Implementation would cycle through shards
        pass
```

## 📊 Step 8: Monitor & Additional Considerations (5 minutes)

### Monitoring and Analytics

#### Key Metrics
```python
# System Metrics
- Request rate (URLs shortened per second)
- Redirect rate (redirections per second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx responses)
- Cache hit ratio

# Business Metrics
- Total URLs created
- Active URLs (non-expired)
- Top domains being shortened
- Geographic distribution of clicks
- Peak usage times
```

#### Analytics Implementation
```python
class AnalyticsService:
    def __init__(self, message_queue, analytics_db):
        self.queue = message_queue
        self.analytics_db = analytics_db

    def track_click(self, short_code, request_info):
        """Track URL click asynchronously"""
        click_data = {
            'short_code': short_code,
            'ip_address': request_info.get('ip'),
            'user_agent': request_info.get('user_agent'),
            'referer': request_info.get('referer'),
            'timestamp': datetime.utcnow(),
            'country': self._get_country_from_ip(request_info.get('ip'))
        }

        # Queue for async processing
        self.queue.publish('click_analytics', click_data)

    def generate_daily_report(self):
        """Generate daily analytics report"""
        return {
            'total_clicks': self.analytics_db.count_clicks_today(),
            'top_urls': self.analytics_db.get_top_clicked_urls(limit=10),
            'top_countries': self.analytics_db.get_top_countries(limit=10),
            'hourly_distribution': self.analytics_db.get_hourly_click_distribution()
        }
```

### Security Considerations

#### Rate Limiting
```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    def is_allowed(self, user_ip, limit=100, window=3600):
        """Rate limit by IP address"""
        key = f"rate_limit:{user_ip}"
        current = self.redis.incr(key)

        if current == 1:
            self.redis.expire(key, window)

        return current <= limit
```

#### URL Validation and Security
```python
def validate_and_sanitize_url(url):
    """Validate URL and check for malicious content"""
    # Basic validation
    if not _is_valid_url_format(url):
        raise ValueError("Invalid URL format")

    # Check against blacklist
    if _is_blacklisted_domain(url):
        raise ValueError("Domain is blacklisted")

    # Check for malicious patterns
    if _contains_malicious_patterns(url):
        raise ValueError("URL contains suspicious content")

    return url
```

### Deployment and Operations

#### Blue-Green Deployment
```
Production Traffic:
[Load Balancer] → [Blue Environment] (current)
                  [Green Environment] (new version, idle)

During Deployment:
1. Deploy new version to Green
2. Test Green environment
3. Switch traffic from Blue to Green
4. Keep Blue as rollback option
```

## 🎯 Alternative Approaches

### Different Encoding Strategies

#### MD5 Hash Approach
```python
def generate_short_code_md5(long_url):
    """Generate short code using MD5 hash"""
    hash_md5 = hashlib.md5(long_url.encode()).hexdigest()
    return hash_md5[:6]  # Take first 6 characters

# Pros: Deterministic (same URL = same short code)
# Cons: Possible collisions, not as short as base62
```

#### KGS (Key Generation Service)
```python
class KeyGenerationService:
    """Separate service for generating unique keys"""

    def __init__(self):
        self.unused_keys = set()
        self.used_keys = set()
        self._generate_keys_batch()

    def _generate_keys_batch(self):
        """Pre-generate batch of unused keys"""
        for _ in range(10000):
            key = self._generate_random_key()
            if key not in self.used_keys:
                self.unused_keys.add(key)

    def get_key(self):
        """Get next available key"""
        if len(self.unused_keys) < 1000:
            self._generate_keys_batch()

        key = self.unused_keys.pop()
        self.used_keys.add(key)
        return key
```

## ✅ Follow-up Questions & Answers

### Q: How would you handle a trending URL that gets millions of hits?
**A**: Implement multi-level caching (L1: application cache, L2: Redis, L3: database) and CDN for geographic distribution. Cache popular URLs with longer TTL.

### Q: What if someone creates millions of short URLs to attack the system?
**A**: Implement rate limiting per IP/user, require user registration for bulk usage, and monitor for unusual patterns.

### Q: How do you ensure the short code generation is not a bottleneck?
**A**: Use a Key Generation Service (KGS) that pre-generates batches of unique keys, or use distributed counter with multiple ranges per server.

### Q: How would you implement analytics without slowing down redirects?
**A**: Make analytics asynchronous - immediately redirect user and queue click data for background processing.

### Q: What about URL expiration and cleanup?
**A**: Run background jobs to mark expired URLs and archive old data. Consider soft deletion to maintain analytics history.

## 📚 Key Takeaways

1. **Start Simple**: Begin with basic functionality, then add complexity
2. **Consider Trade-offs**: Discuss pros/cons of different approaches
3. **Think at Scale**: Always consider how the system behaves under load
4. **Handle Edge Cases**: Expired URLs, custom aliases, malicious URLs
5. **Monitoring Matters**: Plan for observability from the beginning
6. **Security First**: Rate limiting, validation, and abuse prevention

This URL shortener design demonstrates core system design principles and can be completed within a 45-60 minute interview timeframe.