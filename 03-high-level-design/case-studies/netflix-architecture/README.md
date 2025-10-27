# Netflix System Architecture 🔴

## 🎯 Learning Objectives
- Understand large-scale video streaming architecture
- Learn microservices design at massive scale
- Master CDN and content delivery strategies
- Implement recommendation and personalization systems

## 📋 Requirements Analysis

### Functional Requirements
- **Video Streaming**: Stream millions of videos to global users
- **Content Management**: Upload, encode, and manage video content
- **User Management**: Registration, profiles, subscriptions
- **Recommendation Engine**: Personalized content suggestions
- **Search & Discovery**: Content search and browsing
- **Offline Viewing**: Download content for offline consumption
- **Multi-device Support**: TV, mobile, web, gaming consoles

### Non-Functional Requirements
- **Scale**: 200+ million users, billions of hours watched monthly
- **Availability**: 99.99% uptime (4 minutes downtime/month)
- **Performance**: <2 seconds video start time globally
- **Bandwidth**: Handle 15% of global internet traffic
- **Storage**: Petabytes of video content
- **Global**: Serve users in 190+ countries

## 🏗️ High-Level Architecture

```python
# Netflix High-Level Architecture Components

class NetflixArchitecture:
    """
    Netflix's microservices architecture overview
    """

    def __init__(self):
        self.components = {
            'client_layer': [
                'Web Application',
                'Mobile Apps (iOS/Android)',
                'Smart TV Apps',
                'Gaming Console Apps',
                'API Gateway'
            ],

            'microservices_layer': [
                'User Service',
                'Content Service',
                'Recommendation Service',
                'Search Service',
                'Billing Service',
                'Notification Service',
                'Analytics Service'
            ],

            'data_layer': [
                'Cassandra (User data)',
                'MySQL (Billing data)',
                'Elasticsearch (Search)',
                'S3 (Video storage)',
                'Redis (Caching)'
            ],

            'infrastructure': [
                'AWS Cloud',
                'CDN (Content Delivery Network)',
                'Load Balancers',
                'Auto-scaling Groups',
                'Monitoring & Logging'
            ]
        }

# System Architecture Diagram (Conceptual)
"""
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   Mobile App    │    │    Smart TV     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      API Gateway        │
                    │   (Load Balancing)      │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
   ┌────▼────┐            ┌─────▼─────┐           ┌─────▼─────┐
   │ User    │            │ Content   │           │Recommend  │
   │Service  │            │ Service   │           │ Service   │
   └────┬────┘            └─────┬─────┘           └─────┬─────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │     Data Layer         │
                    │ Cassandra/MySQL/Redis  │
                    └────────────────────────┘
"""
```

## 🔧 Core System Components

### 1. Content Delivery Network (CDN)

```python
from typing import Dict, List, Optional
import hashlib
import time
from dataclasses import dataclass
from enum import Enum

class CDNStrategy(Enum):
    PUSH = "push"  # Pre-populate edge servers
    PULL = "pull"  # Populate on-demand

@dataclass
class VideoAsset:
    content_id: str
    title: str
    duration_seconds: int
    file_size_mb: int
    bitrates: List[int]  # Multiple quality options
    regions: List[str]
    popularity_score: float

@dataclass
class EdgeServer:
    server_id: str
    region: str
    capacity_gb: int
    current_usage_gb: int
    bandwidth_mbps: int
    latency_ms: int

class ContentDeliveryNetwork:
    """
    Netflix's CDN implementation for global content delivery
    """

    def __init__(self):
        self.edge_servers: Dict[str, EdgeServer] = {}
        self.content_cache: Dict[str, Dict[str, VideoAsset]] = {}  # region -> content
        self.popularity_tracker: Dict[str, float] = {}
        self.strategy = CDNStrategy.PULL

    def add_edge_server(self, server: EdgeServer):
        """Add edge server to CDN"""
        self.edge_servers[server.server_id] = server
        self.content_cache[server.region] = {}

    def get_optimal_server(self, user_region: str, content_id: str) -> Optional[EdgeServer]:
        """
        Select optimal edge server for content delivery
        """
        # Find servers in user's region first
        region_servers = [
            server for server in self.edge_servers.values()
            if server.region == user_region
        ]

        if not region_servers:
            # Find nearest region servers
            region_servers = list(self.edge_servers.values())

        # Filter servers that have the content or capacity
        available_servers = []
        for server in region_servers:
            if (content_id in self.content_cache.get(server.region, {}) or
                server.current_usage_gb < server.capacity_gb * 0.8):
                available_servers.append(server)

        if not available_servers:
            return None

        # Select server with lowest latency and sufficient bandwidth
        return min(available_servers,
                  key=lambda s: s.latency_ms + (100 - s.bandwidth_mbps))

    def cache_content(self, content: VideoAsset, region: str) -> bool:
        """
        Cache content on edge servers in specified region
        """
        region_servers = [
            server for server in self.edge_servers.values()
            if server.region == region
        ]

        for server in region_servers:
            if server.current_usage_gb + content.file_size_mb/1024 <= server.capacity_gb:
                # Cache content
                self.content_cache[region][content.content_id] = content
                server.current_usage_gb += content.file_size_mb / 1024

                print(f"Cached {content.title} on server {server.server_id} in {region}")
                return True

        return False

    def prefetch_popular_content(self):
        """
        Pre-fetch popular content to edge servers
        """
        # Sort content by popularity
        popular_content = sorted(
            self.popularity_tracker.items(),
            key=lambda x: x[1], reverse=True
        )[:100]  # Top 100 popular content

        for content_id, popularity in popular_content:
            # Cache in all major regions
            for region in ['us-east', 'europe', 'asia-pacific']:
                # Find content and cache it
                # Implementation depends on content storage
                pass

class AdaptiveBitrateStreaming:
    """
    Netflix's adaptive bitrate streaming implementation
    """

    def __init__(self):
        self.bitrate_ladder = [
            {'resolution': '240p', 'bitrate': 300},
            {'resolution': '360p', 'bitrate': 500},
            {'resolution': '480p', 'bitrate': 1000},
            {'resolution': '720p', 'bitrate': 2500},
            {'resolution': '1080p', 'bitrate': 5000},
            {'resolution': '4K', 'bitrate': 15000}
        ]

    def select_bitrate(self, available_bandwidth: int, buffer_health: float,
                      device_capability: str) -> Dict:
        """
        Select optimal bitrate based on network conditions
        """
        # Factor in buffer health (0.0 to 1.0)
        bandwidth_utilization = 0.8 if buffer_health > 0.3 else 0.6
        usable_bandwidth = available_bandwidth * bandwidth_utilization

        # Filter by device capability
        max_resolution = self._get_max_resolution(device_capability)
        suitable_options = [
            option for option in self.bitrate_ladder
            if (option['bitrate'] <= usable_bandwidth and
                self._resolution_rank(option['resolution']) <=
                self._resolution_rank(max_resolution))
        ]

        if not suitable_options:
            return self.bitrate_ladder[0]  # Fallback to lowest quality

        # Select highest quality within bandwidth
        return max(suitable_options, key=lambda x: x['bitrate'])

    def _get_max_resolution(self, device_type: str) -> str:
        device_caps = {
            'mobile': '1080p',
            'tablet': '1080p',
            'laptop': '1080p',
            'desktop': '4K',
            'smart_tv': '4K',
            'gaming_console': '4K'
        }
        return device_caps.get(device_type, '1080p')

    def _resolution_rank(self, resolution: str) -> int:
        ranks = {'240p': 1, '360p': 2, '480p': 3, '720p': 4, '1080p': 5, '4K': 6}
        return ranks.get(resolution, 1)
```

### 2. Recommendation Engine

```python
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict
import math

@dataclass
class User:
    user_id: str
    age: int
    country: str
    subscription_type: str
    viewing_history: List[str]
    ratings: Dict[str, float]
    genres_preference: Dict[str, float]

@dataclass
class Content:
    content_id: str
    title: str
    genres: List[str]
    duration: int
    release_year: int
    rating: float
    popularity_score: float
    cast: List[str]
    director: str

class CollaborativeFiltering:
    """
    Netflix's collaborative filtering recommendation engine
    """

    def __init__(self):
        self.user_item_matrix = defaultdict(dict)
        self.item_similarity_matrix = {}
        self.user_similarity_matrix = {}

    def add_rating(self, user_id: str, content_id: str, rating: float):
        """Add user rating for content"""
        self.user_item_matrix[user_id][content_id] = rating

    def calculate_cosine_similarity(self, vec1: Dict, vec2: Dict) -> float:
        """Calculate cosine similarity between two vectors"""
        common_items = set(vec1.keys()) & set(vec2.keys())
        if not common_items:
            return 0.0

        numerator = sum(vec1[item] * vec2[item] for item in common_items)

        sum1 = sum(vec1[item] ** 2 for item in common_items)
        sum2 = sum(vec2[item] ** 2 for item in common_items)

        denominator = math.sqrt(sum1 * sum2)
        return numerator / denominator if denominator != 0 else 0.0

    def compute_user_similarities(self):
        """Compute similarity matrix between users"""
        users = list(self.user_item_matrix.keys())

        for i, user1 in enumerate(users):
            for user2 in users[i+1:]:
                similarity = self.calculate_cosine_similarity(
                    self.user_item_matrix[user1],
                    self.user_item_matrix[user2]
                )
                self.user_similarity_matrix[(user1, user2)] = similarity
                self.user_similarity_matrix[(user2, user1)] = similarity

    def get_recommendations(self, user_id: str, num_recommendations: int = 10) -> List[Tuple[str, float]]:
        """
        Get content recommendations for user using collaborative filtering
        """
        if user_id not in self.user_item_matrix:
            return []

        user_ratings = self.user_item_matrix[user_id]
        recommendations = defaultdict(float)
        similarity_sums = defaultdict(float)

        # Find similar users
        for other_user in self.user_item_matrix:
            if other_user == user_id:
                continue

            similarity = self.user_similarity_matrix.get((user_id, other_user), 0)
            if similarity <= 0:
                continue

            # Get items rated by similar user but not by current user
            for content_id, rating in self.user_item_matrix[other_user].items():
                if content_id not in user_ratings:
                    recommendations[content_id] += similarity * rating
                    similarity_sums[content_id] += similarity

        # Normalize recommendations
        final_recommendations = []
        for content_id, weighted_sum in recommendations.items():
            if similarity_sums[content_id] > 0:
                predicted_rating = weighted_sum / similarity_sums[content_id]
                final_recommendations.append((content_id, predicted_rating))

        # Sort by predicted rating and return top N
        final_recommendations.sort(key=lambda x: x[1], reverse=True)
        return final_recommendations[:num_recommendations]

class ContentBasedFiltering:
    """
    Content-based recommendation using content features
    """

    def __init__(self):
        self.content_features = {}
        self.user_profiles = {}

    def extract_content_features(self, content: Content) -> Dict[str, float]:
        """Extract features from content"""
        features = {}

        # Genre features
        for genre in content.genres:
            features[f"genre_{genre}"] = 1.0

        # Temporal features
        current_year = 2024
        features["recency"] = max(0, 1 - (current_year - content.release_year) / 20)

        # Popularity features
        features["popularity"] = content.popularity_score

        # Rating features
        features["rating"] = content.rating / 10.0

        return features

    def build_user_profile(self, user: User) -> Dict[str, float]:
        """Build user profile from viewing history and ratings"""
        profile = defaultdict(float)
        total_weight = 0

        for content_id in user.viewing_history:
            if content_id in self.content_features:
                # Weight by user rating if available
                weight = user.ratings.get(content_id, 3.0)  # Default neutral rating

                for feature, value in self.content_features[content_id].items():
                    profile[feature] += weight * value

                total_weight += weight

        # Normalize profile
        if total_weight > 0:
            for feature in profile:
                profile[feature] /= total_weight

        return dict(profile)

    def predict_rating(self, user_profile: Dict[str, float],
                      content_features: Dict[str, float]) -> float:
        """Predict user rating for content"""
        score = 0.0

        for feature, user_preference in user_profile.items():
            content_value = content_features.get(feature, 0.0)
            score += user_preference * content_value

        return max(0, min(5, score))  # Clamp to 0-5 rating scale

class HybridRecommendationEngine:
    """
    Netflix's hybrid recommendation system combining multiple approaches
    """

    def __init__(self):
        self.collaborative_filter = CollaborativeFiltering()
        self.content_filter = ContentBasedFiltering()
        self.popularity_bias = 0.1  # Weight for popular content

    def get_recommendations(self, user: User, available_content: List[Content],
                          num_recommendations: int = 20) -> List[Tuple[str, float]]:
        """
        Get hybrid recommendations combining multiple approaches
        """
        # Get collaborative filtering recommendations
        cf_recommendations = dict(self.collaborative_filter.get_recommendations(
            user.user_id, num_recommendations * 2
        ))

        # Get content-based recommendations
        user_profile = self.content_filter.build_user_profile(user)
        cb_recommendations = {}

        for content in available_content:
            if content.content_id not in user.viewing_history:
                content_features = self.content_filter.extract_content_features(content)
                rating = self.content_filter.predict_rating(user_profile, content_features)
                cb_recommendations[content.content_id] = rating

        # Combine recommendations
        hybrid_scores = {}
        all_content_ids = set(cf_recommendations.keys()) | set(cb_recommendations.keys())

        for content_id in all_content_ids:
            cf_score = cf_recommendations.get(content_id, 0) * 0.6  # 60% weight
            cb_score = cb_recommendations.get(content_id, 0) * 0.4  # 40% weight

            # Add popularity bias
            content = next((c for c in available_content if c.content_id == content_id), None)
            popularity_score = content.popularity_score if content else 0

            hybrid_scores[content_id] = cf_score + cb_score + (popularity_score * self.popularity_bias)

        # Sort and return top recommendations
        recommendations = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
        return recommendations[:num_recommendations]

# Matrix factorization for advanced collaborative filtering
class MatrixFactorization:
    """
    Advanced matrix factorization for Netflix recommendations
    """

    def __init__(self, num_factors: int = 50, learning_rate: float = 0.01,
                 regularization: float = 0.1, num_iterations: int = 100):
        self.num_factors = num_factors
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.num_iterations = num_iterations

    def fit(self, ratings_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit matrix factorization model using gradient descent
        """
        num_users, num_items = ratings_matrix.shape

        # Initialize factor matrices with small random values
        user_factors = np.random.normal(0, 0.1, (num_users, self.num_factors))
        item_factors = np.random.normal(0, 0.1, (num_items, self.num_factors))

        # Get indices of non-zero ratings
        user_indices, item_indices = np.where(ratings_matrix > 0)

        for iteration in range(self.num_iterations):
            for i in range(len(user_indices)):
                user_idx = user_indices[i]
                item_idx = item_indices[i]
                actual_rating = ratings_matrix[user_idx, item_idx]

                # Predict rating
                predicted_rating = np.dot(user_factors[user_idx], item_factors[item_idx])
                error = actual_rating - predicted_rating

                # Update factors using gradient descent
                user_factor_temp = user_factors[user_idx].copy()
                user_factors[user_idx] += self.learning_rate * (
                    error * item_factors[item_idx] -
                    self.regularization * user_factors[user_idx]
                )
                item_factors[item_idx] += self.learning_rate * (
                    error * user_factor_temp -
                    self.regularization * item_factors[item_idx]
                )

        return user_factors, item_factors

    def predict(self, user_factors: np.ndarray, item_factors: np.ndarray) -> np.ndarray:
        """Predict ratings matrix from user and item factors"""
        return np.dot(user_factors, item_factors.T)
```

### 3. Microservices Architecture

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import json
import time
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import requests

class ServiceHealth(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class ServiceMetrics:
    service_name: str
    requests_per_second: float
    average_response_time: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    health_status: ServiceHealth

class CircuitBreaker:
    """
    Circuit breaker pattern for microservice resilience
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"

            raise e

class BaseService(ABC):
    """
    Base class for all Netflix microservices
    """

    def __init__(self, service_name: str, port: int):
        self.service_name = service_name
        self.port = port
        self.health_status = ServiceHealth.HEALTHY
        self.metrics = ServiceMetrics(
            service_name=service_name,
            requests_per_second=0.0,
            average_response_time=0.0,
            error_rate=0.0,
            cpu_usage=0.0,
            memory_usage=0.0,
            health_status=ServiceHealth.HEALTHY
        )
        self.circuit_breakers = {}

    @abstractmethod
    def process_request(self, request: Dict) -> Dict:
        """Process incoming request"""
        pass

    def health_check(self) -> Dict:
        """Health check endpoint"""
        return {
            "service": self.service_name,
            "status": self.health_status.value,
            "timestamp": time.time(),
            "metrics": asdict(self.metrics)
        }

class UserService(BaseService):
    """
    Netflix User Management Service
    """

    def __init__(self):
        super().__init__("user-service", 8001)
        self.users_db = {}  # Simulated database
        self.user_sessions = {}

    def process_request(self, request: Dict) -> Dict:
        """Process user service requests"""
        action = request.get("action")

        if action == "get_user":
            return self.get_user(request.get("user_id"))
        elif action == "create_user":
            return self.create_user(request.get("user_data"))
        elif action == "authenticate":
            return self.authenticate_user(request.get("credentials"))
        elif action == "get_profile":
            return self.get_user_profile(request.get("user_id"))
        else:
            return {"error": "Unknown action"}

    def get_user(self, user_id: str) -> Dict:
        """Get user information"""
        if user_id in self.users_db:
            user = self.users_db[user_id]
            return {"success": True, "user": user}
        return {"success": False, "error": "User not found"}

    def create_user(self, user_data: Dict) -> Dict:
        """Create new user"""
        user_id = f"user_{len(self.users_db) + 1}"
        user_data["user_id"] = user_id
        user_data["created_at"] = time.time()

        self.users_db[user_id] = user_data
        return {"success": True, "user_id": user_id}

    def authenticate_user(self, credentials: Dict) -> Dict:
        """Authenticate user login"""
        email = credentials.get("email")
        password = credentials.get("password")

        # Simplified authentication
        for user_id, user in self.users_db.items():
            if user.get("email") == email and user.get("password") == password:
                session_token = f"session_{user_id}_{int(time.time())}"
                self.user_sessions[session_token] = user_id
                return {
                    "success": True,
                    "session_token": session_token,
                    "user_id": user_id
                }

        return {"success": False, "error": "Invalid credentials"}

    def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile with viewing preferences"""
        if user_id in self.users_db:
            user = self.users_db[user_id]
            # Add viewing statistics
            profile = {
                **user,
                "viewing_time_today": 120,  # minutes
                "favorite_genres": ["Action", "Drama", "Comedy"],
                "watch_list_count": 25,
                "recently_watched": ["content_1", "content_2", "content_3"]
            }
            return {"success": True, "profile": profile}
        return {"success": False, "error": "User not found"}

class ContentService(BaseService):
    """
    Netflix Content Management Service
    """

    def __init__(self):
        super().__init__("content-service", 8002)
        self.content_db = {}
        self.content_metadata = {}

    def process_request(self, request: Dict) -> Dict:
        """Process content service requests"""
        action = request.get("action")

        if action == "get_content":
            return self.get_content(request.get("content_id"))
        elif action == "search_content":
            return self.search_content(request.get("query"))
        elif action == "get_trending":
            return self.get_trending_content()
        elif action == "get_categories":
            return self.get_content_by_category(request.get("category"))
        else:
            return {"error": "Unknown action"}

    def get_content(self, content_id: str) -> Dict:
        """Get specific content details"""
        if content_id in self.content_db:
            content = self.content_db[content_id]
            metadata = self.content_metadata.get(content_id, {})

            return {
                "success": True,
                "content": {**content, **metadata}
            }
        return {"success": False, "error": "Content not found"}

    def search_content(self, query: str) -> Dict:
        """Search content by title, genre, cast, etc."""
        query_lower = query.lower()
        results = []

        for content_id, content in self.content_db.items():
            # Simple search implementation
            if (query_lower in content.get("title", "").lower() or
                any(query_lower in genre.lower() for genre in content.get("genres", [])) or
                any(query_lower in actor.lower() for actor in content.get("cast", []))):
                results.append({**content, "content_id": content_id})

        return {"success": True, "results": results}

    def get_trending_content(self) -> Dict:
        """Get trending content based on view counts"""
        # Sort by popularity/view count
        trending = sorted(
            [(cid, content) for cid, content in self.content_db.items()],
            key=lambda x: x[1].get("view_count", 0),
            reverse=True
        )[:20]

        trending_list = [
            {**content, "content_id": content_id}
            for content_id, content in trending
        ]

        return {"success": True, "trending": trending_list}

    def get_content_by_category(self, category: str) -> Dict:
        """Get content filtered by category/genre"""
        category_content = []

        for content_id, content in self.content_db.items():
            if category.lower() in [g.lower() for g in content.get("genres", [])]:
                category_content.append({**content, "content_id": content_id})

        return {"success": True, "category": category, "content": category_content}

class RecommendationService(BaseService):
    """
    Netflix Recommendation Service
    """

    def __init__(self):
        super().__init__("recommendation-service", 8003)
        self.recommendation_engine = HybridRecommendationEngine()

    def process_request(self, request: Dict) -> Dict:
        """Process recommendation requests"""
        action = request.get("action")

        if action == "get_recommendations":
            return self.get_user_recommendations(
                request.get("user_id"),
                request.get("num_recommendations", 20)
            )
        elif action == "get_similar_content":
            return self.get_similar_content(request.get("content_id"))
        elif action == "get_personalized_rows":
            return self.get_personalized_rows(request.get("user_id"))
        else:
            return {"error": "Unknown action"}

    def get_user_recommendations(self, user_id: str, num_recommendations: int) -> Dict:
        """Get personalized recommendations for user"""
        # In real implementation, fetch user data and content from other services
        try:
            # Simulated recommendations
            recommendations = [
                {"content_id": f"rec_{i}", "score": 0.9 - i*0.1, "reason": "Because you watched..."}
                for i in range(num_recommendations)
            ]

            return {"success": True, "recommendations": recommendations}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_similar_content(self, content_id: str) -> Dict:
        """Get content similar to given content"""
        # Content-based similarity
        similar_content = [
            {"content_id": f"similar_{i}", "similarity_score": 0.8 - i*0.1}
            for i in range(10)
        ]

        return {"success": True, "similar_content": similar_content}

    def get_personalized_rows(self, user_id: str) -> Dict:
        """Get personalized homepage rows for user"""
        rows = [
            {
                "row_id": "trending_now",
                "title": "Trending Now",
                "content_ids": [f"trending_{i}" for i in range(20)]
            },
            {
                "row_id": "because_you_watched",
                "title": "Because you watched Action Movies",
                "content_ids": [f"action_{i}" for i in range(15)]
            },
            {
                "row_id": "new_releases",
                "title": "New Releases",
                "content_ids": [f"new_{i}" for i in range(20)]
            }
        ]

        return {"success": True, "rows": rows}

class APIGateway:
    """
    Netflix API Gateway for routing and load balancing
    """

    def __init__(self):
        self.services = {}
        self.load_balancer = LoadBalancer()
        self.rate_limiter = RateLimiter()

    def register_service(self, service_name: str, instances: List[str]):
        """Register service instances"""
        self.services[service_name] = instances

    def route_request(self, service_name: str, request: Dict, user_id: str = None) -> Dict:
        """Route request to appropriate service with load balancing"""
        # Rate limiting
        if not self.rate_limiter.allow_request(user_id or "anonymous"):
            return {"error": "Rate limit exceeded", "status": 429}

        # Get service instance
        if service_name not in self.services:
            return {"error": "Service not found", "status": 404}

        instance = self.load_balancer.get_instance(service_name, self.services[service_name])

        # In real implementation, make HTTP request to service
        # For simulation, directly call service method
        try:
            if service_name == "user-service":
                service = UserService()
                return service.process_request(request)
            elif service_name == "content-service":
                service = ContentService()
                return service.process_request(request)
            elif service_name == "recommendation-service":
                service = RecommendationService()
                return service.process_request(request)
            else:
                return {"error": "Unknown service"}

        except Exception as e:
            return {"error": f"Service error: {str(e)}", "status": 500}

class LoadBalancer:
    """
    Load balancer for distributing requests across service instances
    """

    def __init__(self):
        self.round_robin_counters = {}

    def get_instance(self, service_name: str, instances: List[str]) -> str:
        """Get next instance using round-robin"""
        if service_name not in self.round_robin_counters:
            self.round_robin_counters[service_name] = 0

        index = self.round_robin_counters[service_name]
        instance = instances[index % len(instances)]

        self.round_robin_counters[service_name] = (index + 1) % len(instances)
        return instance

class RateLimiter:
    """
    Rate limiter for API protection
    """

    def __init__(self, max_requests_per_minute: int = 100):
        self.max_requests = max_requests_per_minute
        self.request_counts = defaultdict(list)

    def allow_request(self, client_id: str) -> bool:
        """Check if request is allowed under rate limit"""
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.request_counts[client_id] = [
            timestamp for timestamp in self.request_counts[client_id]
            if timestamp > minute_ago
        ]

        # Check rate limit
        if len(self.request_counts[client_id]) >= self.max_requests:
            return False

        # Add current request
        self.request_counts[client_id].append(now)
        return True
```

## 📊 System Metrics and Monitoring

### Performance Monitoring

```python
class NetflixMetrics:
    """
    Netflix system metrics and monitoring
    """

    def __init__(self):
        self.metrics = {
            'video_streaming': {
                'avg_start_time_ms': 1800,  # Target: <2000ms
                'buffering_ratio': 0.02,    # Target: <5%
                'quality_switches_per_session': 1.5,  # Target: <3
                'cdn_hit_ratio': 0.95,      # Target: >90%
            },
            'user_engagement': {
                'daily_active_users': 200_000_000,
                'avg_session_duration_minutes': 45,
                'content_completion_rate': 0.78,
                'user_retention_rate': 0.93,
            },
            'system_performance': {
                'api_response_time_ms': 150,  # Target: <200ms
                'service_availability': 0.9999,  # 99.99%
                'error_rate': 0.001,          # 0.1%
                'throughput_rps': 50_000,     # Requests per second
            },
            'infrastructure': {
                'servers_count': 100_000,
                'edge_locations': 1_000,
                'bandwidth_tbps': 100,  # Terabits per second
                'storage_petabytes': 100,
            }
        }

    def get_real_time_metrics(self) -> Dict:
        """Get current system metrics"""
        return {
            'timestamp': time.time(),
            'global_concurrent_streams': 15_000_000,
            'peak_bandwidth_usage': 95_000_000,  # Mbps
            'active_edge_servers': 950,
            'cache_hit_ratio': 0.96,
            'average_bitrate': 4_500,  # kbps
            'quality_distribution': {
                '4K': 0.15,
                '1080p': 0.45,
                '720p': 0.30,
                '480p': 0.10
            }
        }

    def track_user_experience(self, user_id: str, session_data: Dict):
        """Track individual user experience metrics"""
        metrics = {
            'user_id': user_id,
            'session_start': session_data.get('start_time'),
            'video_start_time': session_data.get('video_start_time'),
            'buffering_events': session_data.get('buffer_events', []),
            'quality_changes': session_data.get('quality_changes', []),
            'total_watch_time': session_data.get('watch_time_seconds'),
            'completion_percentage': session_data.get('completion_rate'),
            'device_type': session_data.get('device'),
            'location': session_data.get('region')
        }

        # Calculate QoE (Quality of Experience) score
        qoe_score = self.calculate_qoe_score(metrics)
        metrics['qoe_score'] = qoe_score

        return metrics

    def calculate_qoe_score(self, session_metrics: Dict) -> float:
        """
        Calculate Quality of Experience score (0-10)
        Based on startup time, buffering, and quality
        """
        score = 10.0

        # Penalize long startup times
        startup_time = session_metrics.get('video_start_time', 0)
        if startup_time > 2000:  # >2 seconds
            score -= min(3.0, (startup_time - 2000) / 1000)

        # Penalize buffering events
        buffer_events = len(session_metrics.get('buffering_events', []))
        score -= min(2.0, buffer_events * 0.5)

        # Penalize excessive quality changes
        quality_changes = len(session_metrics.get('quality_changes', []))
        if quality_changes > 5:
            score -= min(1.5, (quality_changes - 5) * 0.3)

        return max(0.0, score)
```

## 🔐 Security and Authentication

```python
import jwt
import bcrypt
from datetime import datetime, timedelta

class NetflixSecurity:
    """
    Netflix security and authentication system
    """

    def __init__(self):
        self.jwt_secret = "netflix_secret_key"
        self.token_expiry_hours = 24
        self.failed_login_attempts = defaultdict(int)
        self.blocked_ips = set()

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def generate_jwt_token(self, user_id: str, device_id: str) -> str:
        """Generate JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'device_id': device_id,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return token

    def validate_jwt_token(self, token: str) -> Optional[Dict]:
        """Validate and decode JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def check_rate_limiting(self, ip_address: str) -> bool:
        """Check if IP is rate limited"""
        if ip_address in self.blocked_ips:
            return False

        if self.failed_login_attempts[ip_address] > 10:
            self.blocked_ips.add(ip_address)
            return False

        return True

    def record_failed_login(self, ip_address: str):
        """Record failed login attempt"""
        self.failed_login_attempts[ip_address] += 1
```

## 🌍 Global Scale Considerations

### Data Replication Strategy
```python
class GlobalDataStrategy:
    """
    Netflix's global data replication and consistency strategy
    """

    def __init__(self):
        self.regions = [
            'us-east-1', 'us-west-2', 'eu-west-1',
            'ap-southeast-1', 'ap-northeast-1'
        ]

        self.data_placement = {
            'user_profiles': 'multi_region_sync',      # Strong consistency
            'viewing_history': 'multi_region_async',   # Eventual consistency
            'recommendations': 'regional_cache',       # Regional processing
            'content_metadata': 'global_cdn',          # Global distribution
            'billing_data': 'single_region_sync'       # Strong consistency
        }

    def get_data_strategy(self, data_type: str, user_region: str) -> Dict:
        """Get data access strategy for specific data type and region"""
        strategy = self.data_placement.get(data_type, 'regional_cache')

        return {
            'strategy': strategy,
            'primary_region': self.get_primary_region(user_region),
            'replica_regions': self.get_replica_regions(user_region),
            'consistency_level': self.get_consistency_level(strategy)
        }

    def get_primary_region(self, user_region: str) -> str:
        """Determine primary region for user data"""
        region_mapping = {
            'north_america': 'us-east-1',
            'europe': 'eu-west-1',
            'asia_pacific': 'ap-southeast-1'
        }
        return region_mapping.get(user_region, 'us-east-1')

    def get_replica_regions(self, user_region: str) -> List[str]:
        """Get replica regions for data redundancy"""
        primary = self.get_primary_region(user_region)
        return [region for region in self.regions if region != primary][:2]

    def get_consistency_level(self, strategy: str) -> str:
        """Determine consistency level based on strategy"""
        consistency_mapping = {
            'multi_region_sync': 'strong',
            'multi_region_async': 'eventual',
            'regional_cache': 'eventual',
            'global_cdn': 'eventual',
            'single_region_sync': 'strong'
        }
        return consistency_mapping.get(strategy, 'eventual')
```

## ✅ Key Takeaways

### Architecture Principles
- **Microservices**: Loosely coupled, independently deployable services
- **Circuit Breakers**: Fault tolerance and resilience patterns
- **CDN Strategy**: Global content delivery with edge caching
- **Hybrid Recommendations**: Multiple ML approaches combined
- **Adaptive Streaming**: Dynamic quality adjustment

### Scalability Patterns
- **Horizontal Scaling**: Auto-scaling service instances
- **Data Partitioning**: Sharding by user/region
- **Caching Layers**: Multi-level caching strategy
- **Asynchronous Processing**: Event-driven architecture
- **Global Distribution**: Multi-region deployment

### Performance Optimization
- **Video Start Time**: <2 seconds globally
- **CDN Hit Ratio**: >95% cache efficiency
- **Buffering Rate**: <5% of viewing time
- **API Response**: <200ms average
- **System Availability**: 99.99% uptime

## 🚀 Next Steps

- Study [YouTube Architecture](../youtube-video-streaming/) for comparison
- Explore [WhatsApp Messaging](../whatsapp-messaging/) for real-time systems
- Practice [System Design Interviews](../../../05-interview-preparation/)
- Learn [Advanced Topics](../../../07-advanced-topics/) for deeper understanding