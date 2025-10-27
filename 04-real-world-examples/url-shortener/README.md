# URL Shortener System Design - Complete Implementation

## Overview
A comprehensive URL shortening service similar to bit.ly, TinyURL, or goo.gl, designed to handle billions of URLs with high availability, fast redirects, and detailed analytics. This implementation covers the complete system architecture with working code examples.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [URL Encoding Service](#url-encoding-service)
3. [URL Shortening Service](#url-shortening-service)
4. [Caching Layer](#caching-layer)
5. [Analytics Service](#analytics-service)
6. [Rate Limiting](#rate-limiting)
7. [Database Design](#database-design)
8. [Scalability Considerations](#scalability-considerations)

## System Architecture

### High-Level Design

```python
import asyncio
import hashlib
import base64
import string
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import redis
import logging
from urllib.parse import urlparse
import re

@dataclass
class ShortenedURL:
    short_id: str
    original_url: str
    user_id: Optional[str] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    click_count: int = 0
    is_active: bool = True
    custom_alias: Optional[str] = None
    password: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ClickEvent:
    short_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    referrer: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None

@dataclass
class URLMetrics:
    short_id: str
    total_clicks: int
    unique_clicks: int
    clicks_by_day: Dict[str, int]
    clicks_by_country: Dict[str, int]
    clicks_by_device: Dict[str, int]
    clicks_by_browser: Dict[str, int]
    top_referrers: List[Tuple[str, int]]
```

## URL Encoding Service

### Base62 Encoding Implementation

```python
class URLEncoder:
    def __init__(self):
        self.base62_chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
        self.base = len(self.base62_chars)

    def encode_id(self, id_number: int) -> str:
        """Convert integer ID to base62 string"""
        if id_number == 0:
            return self.base62_chars[0]

        encoded = ""
        while id_number > 0:
            encoded = self.base62_chars[id_number % self.base] + encoded
            id_number //= self.base

        return encoded

    def decode_id(self, encoded_string: str) -> int:
        """Convert base62 string back to integer ID"""
        id_number = 0
        for char in encoded_string:
            id_number = id_number * self.base + self.base62_chars.index(char)
        return id_number

    def generate_random_string(self, length: int = 7) -> str:
        """Generate random base62 string of specified length"""
        return ''.join(random.choices(self.base62_chars, k=length))

    def hash_based_encoding(self, url: str, length: int = 7) -> str:
        """Generate short ID using hash of the URL"""
        # Use MD5 hash of URL + timestamp for uniqueness
        hash_input = f"{url}{datetime.utcnow().timestamp()}"
        hash_digest = hashlib.md5(hash_input.encode()).hexdigest()

        # Convert hex to integer then to base62
        hash_int = int(hash_digest[:10], 16)  # Use first 10 hex chars
        encoded = self.encode_id(hash_int)

        # Truncate or pad to desired length
        if len(encoded) > length:
            return encoded[:length]
        elif len(encoded) < length:
            return encoded + self.generate_random_string(length - len(encoded))

        return encoded
```

### Counter-Based ID Generation

```python
class CounterBasedGenerator:
    def __init__(self, redis_client, key_prefix="url_counter"):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.encoder = URLEncoder()

    async def get_next_id(self) -> str:
        """Get next sequential ID and encode it"""
        counter_key = f"{self.key_prefix}:global"

        # Atomic increment
        next_id = await self.redis.incr(counter_key)

        # Encode to base62
        return self.encoder.encode_id(next_id)

    async def get_next_range_id(self, server_id: str, range_size: int = 1000) -> str:
        """Get next ID from a pre-allocated range for this server"""
        range_key = f"{self.key_prefix}:range:{server_id}"

        # Check if we have IDs left in current range
        current_id = await self.redis.get(f"{range_key}:current")
        range_end = await self.redis.get(f"{range_key}:end")

        if current_id and range_end and int(current_id) < int(range_end):
            # Use next ID from current range
            next_id = await self.redis.incr(f"{range_key}:current")
            return self.encoder.encode_id(next_id)

        # Allocate new range
        global_counter = await self.redis.incrby(f"{self.key_prefix}:global", range_size)
        range_start = global_counter - range_size + 1
        range_end = global_counter

        # Set range for this server
        await self.redis.set(f"{range_key}:current", range_start - 1)
        await self.redis.set(f"{range_key}:end", range_end)

        # Return first ID from new range
        next_id = await self.redis.incr(f"{range_key}:current")
        return self.encoder.encode_id(next_id)
```

## URL Shortening Service

### Core URL Shortening Service

```python
class URLShortenerService:
    def __init__(self, database, cache, id_generator, rate_limiter):
        self.db = database
        self.cache = cache
        self.id_generator = id_generator
        self.rate_limiter = rate_limiter
        self.base_url = "https://short.ly/"
        self.url_validator = URLValidator()

    async def shorten_url(self, request: Dict) -> Dict:
        """Shorten a URL with optional customization"""
        original_url = request['url']
        user_id = request.get('user_id')
        custom_alias = request.get('custom_alias')
        expiration_days = request.get('expiration_days')
        password = request.get('password')

        # Rate limiting check
        if user_id:
            can_proceed = await self.rate_limiter.check_rate_limit(
                f"user:{user_id}",
                limit=100,  # 100 URLs per hour per user
                window=3600
            )
            if not can_proceed:
                return {"error": "Rate limit exceeded", "code": 429}

        # Validate URL
        if not self.url_validator.is_valid_url(original_url):
            return {"error": "Invalid URL format", "code": 400}

        # Check if URL is already shortened by this user
        existing = await self.find_existing_url(original_url, user_id)
        if existing and not custom_alias:
            return {
                "short_url": f"{self.base_url}{existing.short_id}",
                "short_id": existing.short_id,
                "created_at": existing.created_at.isoformat(),
                "is_existing": True
            }

        # Generate short ID
        if custom_alias:
            if await self.is_alias_taken(custom_alias):
                return {"error": "Custom alias already taken", "code": 409}
            short_id = custom_alias
        else:
            short_id = await self.generate_unique_id()

        # Calculate expiration
        expires_at = None
        if expiration_days:
            expires_at = datetime.utcnow() + timedelta(days=expiration_days)

        # Create shortened URL record
        shortened_url = ShortenedURL(
            short_id=short_id,
            original_url=original_url,
            user_id=user_id,
            expires_at=expires_at,
            custom_alias=custom_alias,
            password=password
        )

        # Store in database
        await self.store_url(shortened_url)

        # Cache for fast access
        await self.cache_url(shortened_url)

        return {
            "short_url": f"{self.base_url}{short_id}",
            "short_id": short_id,
            "original_url": original_url,
            "created_at": shortened_url.created_at.isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None
        }

    async def resolve_url(self, short_id: str, client_info: Dict) -> Dict:
        """Resolve short URL to original URL and track analytics"""

        # Try cache first
        cached_url = await self.get_cached_url(short_id)

        if not cached_url:
            # Fallback to database
            url_record = await self.get_url_from_db(short_id)
            if not url_record:
                return {"error": "URL not found", "code": 404}

            # Cache for future requests
            await self.cache_url(url_record)
            cached_url = url_record
        else:
            url_record = cached_url

        # Check if URL is active and not expired
        if not url_record.is_active:
            return {"error": "URL has been deactivated", "code": 410}

        if url_record.expires_at and datetime.utcnow() > url_record.expires_at:
            return {"error": "URL has expired", "code": 410}

        # Check password protection
        if url_record.password:
            provided_password = client_info.get('password')
            if not provided_password or provided_password != url_record.password:
                return {"error": "Password required", "code": 401}

        # Track click analytics (async to not slow down redirect)
        asyncio.create_task(self.track_click(short_id, client_info))

        return {
            "original_url": url_record.original_url,
            "redirect": True
        }

    async def generate_unique_id(self, max_attempts: int = 5) -> str:
        """Generate unique short ID with collision handling"""
        for attempt in range(max_attempts):
            short_id = await self.id_generator.get_next_id()

            # Check if ID is already taken
            existing = await self.get_url_from_db(short_id)
            if not existing:
                return short_id

            # Collision detected - try again
            logging.warning(f"ID collision detected: {short_id}, attempt {attempt + 1}")

        # Fallback to random generation if counter-based fails
        while True:
            short_id = self.id_generator.encoder.generate_random_string(8)  # Longer for uniqueness
            existing = await self.get_url_from_db(short_id)
            if not existing:
                return short_id

    async def store_url(self, url: ShortenedURL):
        """Store URL in database"""
        await self.db.execute(
            """
            INSERT INTO shortened_urls (short_id, original_url, user_id, created_at, expires_at,
                                      custom_alias, password, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (url.short_id, url.original_url, url.user_id, url.created_at,
             url.expires_at, url.custom_alias, url.password, url.is_active)
        )

    async def cache_url(self, url: ShortenedURL):
        """Cache URL for fast access"""
        cache_key = f"url:{url.short_id}"
        cache_data = {
            "original_url": url.original_url,
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
            "is_active": url.is_active,
            "password": url.password
        }

        # Cache with TTL (1 hour for most URLs, shorter for expiring ones)
        ttl = 3600
        if url.expires_at:
            remaining_time = (url.expires_at - datetime.utcnow()).total_seconds()
            ttl = min(ttl, max(300, int(remaining_time)))  # Min 5 minutes

        await self.cache.setex(cache_key, ttl, json.dumps(cache_data))

    async def get_cached_url(self, short_id: str) -> Optional[ShortenedURL]:
        """Get URL from cache"""
        cache_key = f"url:{short_id}"
        cached_data = await self.cache.get(cache_key)

        if cached_data:
            data = json.loads(cached_data)
            return ShortenedURL(
                short_id=short_id,
                original_url=data['original_url'],
                expires_at=datetime.fromisoformat(data['expires_at']) if data['expires_at'] else None,
                is_active=data['is_active'],
                password=data['password']
            )

        return None

    async def track_click(self, short_id: str, client_info: Dict):
        """Track click event for analytics"""
        click_event = ClickEvent(
            short_id=short_id,
            timestamp=datetime.utcnow(),
            ip_address=client_info.get('ip_address', ''),
            user_agent=client_info.get('user_agent', ''),
            referrer=client_info.get('referrer'),
            country=await self.get_country_from_ip(client_info.get('ip_address')),
            device_type=self.parse_device_type(client_info.get('user_agent', '')),
            browser=self.parse_browser(client_info.get('user_agent', ''))
        )

        # Store click event
        await self.store_click_event(click_event)

        # Update click count (cached)
        await self.increment_click_count(short_id)

    async def find_existing_url(self, original_url: str, user_id: Optional[str]) -> Optional[ShortenedURL]:
        """Find existing shortened URL for the same original URL"""
        if user_id:
            result = await self.db.fetch_one(
                "SELECT * FROM shortened_urls WHERE original_url = ? AND user_id = ? AND is_active = 1",
                (original_url, user_id)
            )
        else:
            result = await self.db.fetch_one(
                "SELECT * FROM shortened_urls WHERE original_url = ? AND user_id IS NULL AND is_active = 1",
                (original_url,)
            )

        return ShortenedURL(**result) if result else None
```

### URL Validation Service

```python
class URLValidator:
    def __init__(self):
        self.blocked_domains = {
            'malware.com', 'phishing-site.net', 'spam.org'
        }
        self.allowed_schemes = {'http', 'https', 'ftp'}

    def is_valid_url(self, url: str) -> bool:
        """Validate URL format and security"""
        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in self.allowed_schemes:
                return False

            # Check domain
            if not parsed.netloc:
                return False

            # Check for blocked domains
            domain = parsed.netloc.lower()
            if domain in self.blocked_domains:
                return False

            # Check for suspicious patterns
            if self.contains_suspicious_patterns(url):
                return False

            # Check URL length
            if len(url) > 2048:  # Standard URL length limit
                return False

            return True

        except Exception:
            return False

    def contains_suspicious_patterns(self, url: str) -> bool:
        """Check for suspicious URL patterns"""
        suspicious_patterns = [
            r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # Raw IP addresses
            r'[a-z0-9]{32,}',  # Very long random strings
            r'(bit\.ly|tinyurl\.com|short\.ly)/',  # Nested URL shorteners
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, url.lower()):
                return True

        return False

    async def check_url_safety(self, url: str) -> Dict:
        """Check URL against security databases"""
        # Simulate security check (integrate with Google Safe Browsing API)
        safety_result = {
            'is_safe': True,
            'threats': [],
            'reputation_score': 95
        }

        # Check domain reputation
        parsed = urlparse(url)
        domain_age = await self.get_domain_age(parsed.netloc)

        if domain_age < 30:  # Domain less than 30 days old
            safety_result['reputation_score'] -= 20

        return safety_result
```

## Caching Layer

### Multi-Level Caching

```python
class URLCacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.local_cache = {}  # In-memory L1 cache
        self.local_cache_ttl = 300  # 5 minutes
        self.local_cache_max_size = 10000

    async def get_url(self, short_id: str) -> Optional[Dict]:
        """Get URL with multi-level caching"""
        # Try L1 (local) cache first
        local_result = self.get_from_local_cache(short_id)
        if local_result:
            return local_result

        # Try L2 (Redis) cache
        redis_result = await self.get_from_redis_cache(short_id)
        if redis_result:
            # Backfill local cache
            self.set_to_local_cache(short_id, redis_result)
            return redis_result

        return None

    async def set_url(self, short_id: str, url_data: Dict, ttl: int = 3600):
        """Set URL in all cache levels"""
        # Set in Redis (L2)
        await self.redis.setex(
            f"url:{short_id}",
            ttl,
            json.dumps(url_data)
        )

        # Set in local cache (L1)
        self.set_to_local_cache(short_id, url_data)

    def get_from_local_cache(self, short_id: str) -> Optional[Dict]:
        """Get from local in-memory cache"""
        cache_key = f"url:{short_id}"
        if cache_key in self.local_cache:
            entry = self.local_cache[cache_key]
            if datetime.utcnow().timestamp() - entry['timestamp'] < self.local_cache_ttl:
                return entry['data']
            else:
                del self.local_cache[cache_key]

        return None

    def set_to_local_cache(self, short_id: str, data: Dict):
        """Set to local in-memory cache with LRU eviction"""
        cache_key = f"url:{short_id}"

        # LRU eviction if cache is full
        if len(self.local_cache) >= self.local_cache_max_size:
            oldest_key = min(
                self.local_cache.keys(),
                key=lambda k: self.local_cache[k]['timestamp']
            )
            del self.local_cache[oldest_key]

        self.local_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.utcnow().timestamp()
        }

    async def get_from_redis_cache(self, short_id: str) -> Optional[Dict]:
        """Get from Redis cache"""
        cached_data = await self.redis.get(f"url:{short_id}")
        return json.loads(cached_data) if cached_data else None

    async def invalidate_url(self, short_id: str):
        """Invalidate URL from all cache levels"""
        # Remove from Redis
        await self.redis.delete(f"url:{short_id}")

        # Remove from local cache
        cache_key = f"url:{short_id}"
        if cache_key in self.local_cache:
            del self.local_cache[cache_key]

    async def warm_cache(self, popular_urls: List[str]):
        """Pre-warm cache with popular URLs"""
        for short_id in popular_urls:
            # Fetch from database and cache
            url_data = await self.get_url_from_database(short_id)
            if url_data:
                await self.set_url(short_id, url_data)
```

## Analytics Service

### Click Analytics and Metrics

```python
class AnalyticsService:
    def __init__(self, database, time_series_db, cache):
        self.db = database
        self.time_series_db = time_series_db  # InfluxDB or similar
        self.cache = cache

    async def store_click_event(self, click_event: ClickEvent):
        """Store click event for detailed analytics"""
        # Store in relational database for complex queries
        await self.db.execute(
            """
            INSERT INTO click_events (short_id, timestamp, ip_address, user_agent,
                                    referrer, country, city, device_type, browser)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (click_event.short_id, click_event.timestamp, click_event.ip_address,
             click_event.user_agent, click_event.referrer, click_event.country,
             click_event.city, click_event.device_type, click_event.browser)
        )

        # Store in time-series database for real-time analytics
        await self.store_time_series_event(click_event)

        # Update real-time counters
        await self.update_real_time_metrics(click_event)

    async def store_time_series_event(self, click_event: ClickEvent):
        """Store click event in time-series database"""
        point = {
            "measurement": "url_clicks",
            "tags": {
                "short_id": click_event.short_id,
                "country": click_event.country or "unknown",
                "device_type": click_event.device_type or "unknown",
                "browser": click_event.browser or "unknown"
            },
            "fields": {
                "clicks": 1
            },
            "time": click_event.timestamp
        }

        await self.time_series_db.write_point(point)

    async def update_real_time_metrics(self, click_event: ClickEvent):
        """Update real-time metrics in Redis"""
        now = datetime.utcnow()
        hour_key = now.strftime("%Y-%m-%d-%H")
        day_key = now.strftime("%Y-%m-%d")

        pipeline = self.cache.pipeline()

        # Total clicks
        pipeline.incr(f"clicks:{click_event.short_id}:total")
        pipeline.incr(f"clicks:{click_event.short_id}:hour:{hour_key}")
        pipeline.incr(f"clicks:{click_event.short_id}:day:{day_key}")

        # Country clicks
        if click_event.country:
            pipeline.incr(f"clicks:{click_event.short_id}:country:{click_event.country}")

        # Device clicks
        if click_event.device_type:
            pipeline.incr(f"clicks:{click_event.short_id}:device:{click_event.device_type}")

        # Browser clicks
        if click_event.browser:
            pipeline.incr(f"clicks:{click_event.short_id}:browser:{click_event.browser}")

        # Unique clicks (using HyperLogLog for memory efficiency)
        pipeline.pfadd(f"unique_clicks:{click_event.short_id}", click_event.ip_address)

        await pipeline.execute()

    async def get_url_analytics(self, short_id: str, days: int = 30) -> URLMetrics:
        """Get comprehensive analytics for a URL"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get total and unique clicks
        total_clicks = await self.cache.get(f"clicks:{short_id}:total") or 0
        unique_clicks = await self.cache.pfcount(f"unique_clicks:{short_id}") or 0

        # Get clicks by day
        clicks_by_day = await self.get_daily_clicks(short_id, start_date, end_date)

        # Get geographic distribution
        clicks_by_country = await self.get_clicks_by_dimension(short_id, "country")

        # Get device distribution
        clicks_by_device = await self.get_clicks_by_dimension(short_id, "device")

        # Get browser distribution
        clicks_by_browser = await self.get_clicks_by_dimension(short_id, "browser")

        # Get top referrers
        top_referrers = await self.get_top_referrers(short_id, limit=10)

        return URLMetrics(
            short_id=short_id,
            total_clicks=int(total_clicks),
            unique_clicks=int(unique_clicks),
            clicks_by_day=clicks_by_day,
            clicks_by_country=clicks_by_country,
            clicks_by_device=clicks_by_device,
            clicks_by_browser=clicks_by_browser,
            top_referrers=top_referrers
        )

    async def get_daily_clicks(self, short_id: str, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Get clicks grouped by day"""
        clicks_by_day = {}
        current_date = start_date

        while current_date <= end_date:
            day_key = current_date.strftime("%Y-%m-%d")
            clicks = await self.cache.get(f"clicks:{short_id}:day:{day_key}") or 0
            clicks_by_day[day_key] = int(clicks)
            current_date += timedelta(days=1)

        return clicks_by_day

    async def get_clicks_by_dimension(self, short_id: str, dimension: str, limit: int = 10) -> Dict[str, int]:
        """Get clicks grouped by dimension (country, device, browser)"""
        pattern = f"clicks:{short_id}:{dimension}:*"
        keys = await self.cache.keys(pattern)

        results = {}
        for key in keys:
            dimension_value = key.split(":")[-1]
            clicks = await self.cache.get(key) or 0
            results[dimension_value] = int(clicks)

        # Sort by clicks and return top N
        sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True)[:limit])
        return sorted_results

    async def get_top_referrers(self, short_id: str, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top referrers for a URL"""
        query = """
        SELECT referrer, COUNT(*) as clicks
        FROM click_events
        WHERE short_id = ? AND referrer IS NOT NULL AND referrer != ''
        GROUP BY referrer
        ORDER BY clicks DESC
        LIMIT ?
        """

        results = await self.db.fetch_all(query, (short_id, limit))
        return [(row['referrer'], row['clicks']) for row in results]

    async def generate_analytics_report(self, short_id: str) -> Dict:
        """Generate comprehensive analytics report"""
        metrics = await self.get_url_analytics(short_id)

        # Calculate growth rates
        yesterday_clicks = await self.get_clicks_for_date(short_id, datetime.utcnow() - timedelta(days=1))
        week_ago_clicks = await self.get_clicks_for_date(short_id, datetime.utcnow() - timedelta(days=7))

        daily_growth = ((yesterday_clicks - week_ago_clicks) / max(week_ago_clicks, 1)) * 100

        # Peak performance analysis
        peak_day = max(metrics.clicks_by_day.items(), key=lambda x: x[1], default=("", 0))

        return {
            "summary": {
                "total_clicks": metrics.total_clicks,
                "unique_clicks": metrics.unique_clicks,
                "click_through_rate": (metrics.unique_clicks / max(metrics.total_clicks, 1)) * 100,
                "daily_growth_rate": round(daily_growth, 2)
            },
            "peak_performance": {
                "best_day": peak_day[0],
                "best_day_clicks": peak_day[1]
            },
            "geographic_distribution": metrics.clicks_by_country,
            "device_breakdown": metrics.clicks_by_device,
            "browser_breakdown": metrics.clicks_by_browser,
            "top_referrers": metrics.top_referrers,
            "daily_trend": metrics.clicks_by_day
        }
```

## Rate Limiting

### Advanced Rate Limiting

```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit using sliding window"""
        now = datetime.utcnow().timestamp()
        pipeline = self.redis.pipeline()

        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, now - window)

        # Add current request
        pipeline.zadd(key, {str(now): now})

        # Count requests in window
        pipeline.zcard(key)

        # Set expiration
        pipeline.expire(key, window)

        results = await pipeline.execute()
        request_count = results[2]

        return request_count <= limit

    async def check_token_bucket_rate_limit(self, key: str, capacity: int, refill_rate: float) -> bool:
        """Token bucket rate limiting for burst traffic"""
        now = datetime.utcnow().timestamp()

        # Get current bucket state
        bucket_data = await self.redis.hmget(key, "tokens", "last_refill")
        current_tokens = float(bucket_data[0] or capacity)
        last_refill = float(bucket_data[1] or now)

        # Calculate tokens to add based on time elapsed
        time_elapsed = now - last_refill
        tokens_to_add = time_elapsed * refill_rate
        current_tokens = min(capacity, current_tokens + tokens_to_add)

        if current_tokens >= 1:
            # Allow request and consume token
            current_tokens -= 1
            await self.redis.hmset(key, {
                "tokens": current_tokens,
                "last_refill": now
            })
            await self.redis.expire(key, 3600)  # 1 hour TTL
            return True
        else:
            # Update refill time even if request is denied
            await self.redis.hmset(key, {
                "tokens": current_tokens,
                "last_refill": now
            })
            await self.redis.expire(key, 3600)
            return False

    async def apply_tiered_rate_limiting(self, user_id: str) -> Dict:
        """Apply different rate limits based on user tier"""
        user_tier = await self.get_user_tier(user_id)

        rate_limits = {
            "free": {"urls_per_hour": 10, "clicks_per_hour": 1000},
            "premium": {"urls_per_hour": 100, "clicks_per_hour": 10000},
            "enterprise": {"urls_per_hour": 1000, "clicks_per_hour": 100000}
        }

        limits = rate_limits.get(user_tier, rate_limits["free"])

        # Check URL creation limit
        url_limit_ok = await self.check_rate_limit(
            f"urls:{user_id}:hour",
            limits["urls_per_hour"],
            3600
        )

        # Check click limit (for analytics requests)
        click_limit_ok = await self.check_rate_limit(
            f"clicks:{user_id}:hour",
            limits["clicks_per_hour"],
            3600
        )

        return {
            "url_creation_allowed": url_limit_ok,
            "analytics_allowed": click_limit_ok,
            "limits": limits
        }
```

## Database Design

### Database Schema and Operations

```python
class DatabaseManager:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    async def create_tables(self):
        """Create database tables for URL shortener"""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS shortened_urls (
                short_id VARCHAR(20) PRIMARY KEY,
                original_url TEXT NOT NULL,
                user_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL,
                click_count BIGINT DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                custom_alias VARCHAR(100) UNIQUE,
                password VARCHAR(255) NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at),
                INDEX idx_expires_at (expires_at)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS click_events (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                short_id VARCHAR(20) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT,
                referrer TEXT,
                country VARCHAR(100),
                city VARCHAR(100),
                device_type VARCHAR(50),
                browser VARCHAR(50),
                INDEX idx_short_id (short_id),
                INDEX idx_timestamp (timestamp),
                INDEX idx_country (country),
                FOREIGN KEY (short_id) REFERENCES shortened_urls(short_id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(50) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                tier VARCHAR(20) DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
            """
        ]

        for table_sql in tables:
            await self.execute(table_sql)

    async def create_indexes(self):
        """Create optimized indexes for performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_url_user_created ON shortened_urls(user_id, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_clicks_short_timestamp ON click_events(short_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_clicks_country_timestamp ON click_events(country, timestamp DESC)",
        ]

        for index_sql in indexes:
            await self.execute(index_sql)

    async def setup_partitioning(self):
        """Set up table partitioning for large datasets"""
        # Partition click_events table by month for better performance
        partition_sql = """
        ALTER TABLE click_events
        PARTITION BY RANGE (YEAR(timestamp) * 100 + MONTH(timestamp)) (
            PARTITION p202401 VALUES LESS THAN (202402),
            PARTITION p202402 VALUES LESS THAN (202403),
            PARTITION p202403 VALUES LESS THAN (202404),
            -- Add more partitions as needed
            PARTITION pmax VALUES LESS THAN MAXVALUE
        )
        """
        # Note: This is MySQL-specific syntax
        try:
            await self.execute(partition_sql)
        except Exception as e:
            # Partitioning might already exist or not supported
            logging.warning(f"Partitioning setup failed: {e}")

class ShardedDatabaseManager:
    def __init__(self, shard_configs: List[Dict]):
        self.shards = shard_configs
        self.shard_map = {}

    def get_shard_for_url(self, short_id: str) -> Dict:
        """Determine which shard to use for a given URL"""
        shard_index = hash(short_id) % len(self.shards)
        return self.shards[shard_index]

    async def store_url_sharded(self, url: ShortenedURL):
        """Store URL in appropriate shard"""
        shard = self.get_shard_for_url(url.short_id)
        await shard['connection'].execute(
            "INSERT INTO shortened_urls (...) VALUES (...)",
            # URL data
        )

    async def get_url_sharded(self, short_id: str) -> Optional[ShortenedURL]:
        """Retrieve URL from appropriate shard"""
        shard = self.get_shard_for_url(short_id)
        result = await shard['connection'].fetch_one(
            "SELECT * FROM shortened_urls WHERE short_id = ?",
            (short_id,)
        )
        return ShortenedURL(**result) if result else None
```

This comprehensive URL shortener implementation provides all the essential features needed for a production-ready service: efficient URL encoding, caching, analytics, rate limiting, and database management. The system is designed to handle billions of URLs with high availability and fast response times.