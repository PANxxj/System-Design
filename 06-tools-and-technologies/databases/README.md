# Database Technologies 🟡

## 🎯 Learning Objectives
- Compare different database technologies and their use cases
- Understand when to choose SQL vs NoSQL solutions
- Learn about cloud database services and their trade-offs
- Master database selection criteria for different scenarios

## 🗄️ SQL Databases

### PostgreSQL
**Open-source, advanced relational database**

#### Strengths
- ✅ **ACID Compliance**: Full transaction support
- ✅ **Advanced Features**: JSON support, window functions, CTEs
- ✅ **Extensibility**: Custom data types, functions, operators
- ✅ **Performance**: Query optimization, indexing options
- ✅ **Reliability**: Battle-tested in production environments

#### Best Use Cases
```python
# Complex queries with relationships
"""
SELECT
    u.username,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE u.created_at >= '2024-01-01'
GROUP BY u.user_id, u.username
HAVING COUNT(o.order_id) > 5
ORDER BY total_spent DESC;
"""

# JSON support for semi-structured data
"""
SELECT
    product_name,
    attributes->>'color' as color,
    attributes->>'size' as size
FROM products
WHERE attributes @> '{"category": "clothing"}';
"""
```

#### When to Choose PostgreSQL
- Complex relational data with many joins
- Need for advanced SQL features
- Strong consistency requirements
- Mixed structured and semi-structured data (JSON)

### MySQL
**Popular open-source relational database**

#### Strengths
- ✅ **Popularity**: Large community, extensive documentation
- ✅ **Performance**: Optimized for read-heavy workloads
- ✅ **Replication**: Master-slave replication built-in
- ✅ **Storage Engines**: InnoDB, MyISAM for different needs

#### Best Use Cases
```python
# Web application backends
class MySQLUserService:
    def __init__(self, connection):
        self.db = connection

    def get_user_with_posts(self, user_id):
        query = """
        SELECT u.*, p.title, p.content, p.created_at as post_date
        FROM users u
        LEFT JOIN posts p ON u.user_id = p.user_id
        WHERE u.user_id = %s
        ORDER BY p.created_at DESC
        """
        return self.db.execute(query, (user_id,))

    def get_popular_posts(self, limit=10):
        query = """
        SELECT p.*, u.username, COUNT(l.like_id) as like_count
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        LEFT JOIN likes l ON p.post_id = l.post_id
        GROUP BY p.post_id
        ORDER BY like_count DESC
        LIMIT %s
        """
        return self.db.execute(query, (limit,))
```

#### When to Choose MySQL
- Web applications with read-heavy workloads
- Need for proven replication solutions
- WordPress, Drupal, or other CMS platforms
- Budget-conscious projects requiring reliability

### Oracle Database
**Enterprise-grade commercial database**

#### Strengths
- ✅ **Enterprise Features**: Advanced security, partitioning, compression
- ✅ **Performance**: Optimizer, materialized views, parallel processing
- ✅ **Scalability**: RAC (Real Application Clusters)
- ✅ **Support**: Commercial support and consulting

#### When to Choose Oracle
- Large enterprise applications
- Need for advanced enterprise features
- Regulatory compliance requirements
- Existing Oracle infrastructure

## 🗃️ NoSQL Databases

### MongoDB (Document Database)
**Flexible document storage with JSON-like documents**

#### Strengths
- ✅ **Schema Flexibility**: Dynamic schema evolution
- ✅ **Developer Friendly**: JSON-like documents, rich query language
- ✅ **Scaling**: Built-in sharding and replication
- ✅ **Indexing**: Flexible indexing on any field

#### Example Use Cases
```python
# E-commerce product catalog
{
  "_id": ObjectId("..."),
  "name": "Wireless Headphones",
  "brand": "TechBrand",
  "price": 199.99,
  "categories": ["electronics", "audio", "headphones"],
  "specifications": {
    "wireless": true,
    "batteryLife": "20 hours",
    "frequency": "20Hz-20kHz",
    "weight": "250g"
  },
  "reviews": [
    {
      "userId": "user123",
      "rating": 5,
      "comment": "Great sound quality!",
      "date": ISODate("2024-01-15")
    }
  ],
  "inventory": {
    "inStock": true,
    "quantity": 150,
    "warehouses": ["NYC", "LA", "CHI"]
  }
}

# User profiles with varying structures
{
  "_id": ObjectId("..."),
  "username": "john_doe",
  "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "preferences": {
      "theme": "dark",
      "notifications": {
        "email": true,
        "push": false,
        "sms": true
      }
    },
    "socialLinks": {
      "twitter": "@johndoe",
      "linkedin": "linkedin.com/in/johndoe"
    }
  },
  "subscription": {
    "plan": "premium",
    "startDate": ISODate("2024-01-01"),
    "features": ["unlimited_storage", "priority_support"]
  }
}
```

#### When to Choose MongoDB
- Rapid application development
- Evolving data models
- Content management systems
- Real-time analytics
- Catalog and inventory systems

### Redis (Key-Value Store)
**In-memory data structure store**

#### Strengths
- ✅ **Performance**: Sub-millisecond latency
- ✅ **Data Structures**: Strings, hashes, lists, sets, sorted sets
- ✅ **Persistence**: RDB snapshots and AOF logging
- ✅ **Pub/Sub**: Built-in messaging capabilities

#### Example Use Cases
```python
import redis
import json
from datetime import timedelta

class RedisService:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # Caching
    def cache_user_profile(self, user_id, profile_data, ttl_hours=24):
        key = f"user:profile:{user_id}"
        self.redis_client.setex(
            key,
            timedelta(hours=ttl_hours),
            json.dumps(profile_data)
        )

    def get_cached_profile(self, user_id):
        key = f"user:profile:{user_id}"
        data = self.redis_client.get(key)
        return json.loads(data) if data else None

    # Session management
    def create_session(self, session_id, user_data, ttl_hours=8):
        key = f"session:{session_id}"
        self.redis_client.hset(key, mapping=user_data)
        self.redis_client.expire(key, timedelta(hours=ttl_hours))

    def get_session(self, session_id):
        key = f"session:{session_id}"
        return self.redis_client.hgetall(key)

    # Real-time features
    def add_to_leaderboard(self, user_id, score):
        self.redis_client.zadd("game:leaderboard", {user_id: score})

    def get_top_players(self, limit=10):
        return self.redis_client.zrevrange(
            "game:leaderboard", 0, limit-1, withscores=True
        )

    # Rate limiting
    def is_rate_limited(self, user_id, limit=100, window_seconds=3600):
        key = f"rate_limit:{user_id}"
        current = self.redis_client.incr(key)

        if current == 1:
            self.redis_client.expire(key, window_seconds)

        return current > limit

    # Pub/Sub messaging
    def publish_notification(self, channel, message):
        self.redis_client.publish(channel, json.dumps(message))

    def subscribe_to_notifications(self, channel):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(channel)
        return pubsub
```

#### When to Choose Redis
- Caching layer
- Session storage
- Real-time leaderboards
- Rate limiting
- Pub/sub messaging
- Temporary data storage

### Cassandra (Column-Family)
**Distributed wide-column store**

#### Strengths
- ✅ **Scalability**: Linear scaling, no single point of failure
- ✅ **Availability**: Always-on architecture
- ✅ **Performance**: Optimized for write-heavy workloads
- ✅ **Geographic Distribution**: Multi-datacenter replication

#### Example Use Cases
```python
# Time-series data
"""
CREATE TABLE sensor_readings (
    sensor_id UUID,
    reading_time TIMESTAMP,
    temperature DECIMAL,
    humidity DECIMAL,
    location TEXT,
    PRIMARY KEY (sensor_id, reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC);

-- Query recent readings
SELECT * FROM sensor_readings
WHERE sensor_id = 123e4567-e89b-12d3-a456-426614174000
AND reading_time >= '2024-01-01 00:00:00'
ORDER BY reading_time DESC
LIMIT 100;
"""

# User activity tracking
"""
CREATE TABLE user_activity (
    user_id UUID,
    activity_date DATE,
    activity_time TIMESTAMP,
    action TEXT,
    details MAP<TEXT, TEXT>,
    PRIMARY KEY (user_id, activity_date, activity_time)
);

-- Query user activity for a specific day
SELECT * FROM user_activity
WHERE user_id = 456e7890-e89b-12d3-a456-426614174000
AND activity_date = '2024-01-15';
"""
```

#### When to Choose Cassandra
- High write throughput requirements
- Time-series data
- IoT data collection
- Activity logs and analytics
- Global distribution needs

### DynamoDB (AWS Managed NoSQL)
**Fully managed key-value and document database**

#### Strengths
- ✅ **Serverless**: No infrastructure management
- ✅ **Performance**: Single-digit millisecond latency
- ✅ **Scaling**: Auto-scaling based on demand
- ✅ **Integration**: Deep AWS ecosystem integration

#### Example Use Cases
```python
import boto3
from boto3.dynamodb.conditions import Key, Attr

class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.users_table = self.dynamodb.Table('Users')
        self.orders_table = self.dynamodb.Table('Orders')

    # User management
    def create_user(self, user_data):
        return self.users_table.put_item(Item=user_data)

    def get_user(self, user_id):
        response = self.users_table.get_item(Key={'user_id': user_id})
        return response.get('Item')

    def update_user(self, user_id, update_data):
        update_expression = "SET "
        expression_values = {}

        for key, value in update_data.items():
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value

        update_expression = update_expression.rstrip(', ')

        return self.users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )

    # Order management with GSI
    def create_order(self, order_data):
        return self.orders_table.put_item(Item=order_data)

    def get_user_orders(self, user_id):
        response = self.orders_table.query(
            IndexName='user_id-index',
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        return response['Items']

    def get_orders_by_status(self, status):
        response = self.orders_table.scan(
            FilterExpression=Attr('status').eq(status)
        )
        return response['Items']
```

#### When to Choose DynamoDB
- AWS-native applications
- Need for managed infrastructure
- Unpredictable scaling requirements
- Gaming applications
- Mobile backends

## 🔍 Database Selection Framework

### Decision Matrix

| Factor | PostgreSQL | MySQL | MongoDB | Redis | Cassandra | DynamoDB |
|--------|------------|-------|---------|-------|-----------|----------|
| **ACID Transactions** | ✅ Full | ✅ Full | ⚠️ Limited | ❌ No | ❌ No | ⚠️ Limited |
| **Schema Flexibility** | ⚠️ JSON Support | ❌ Fixed | ✅ Dynamic | ✅ Key-Value | ⚠️ Column | ✅ Document |
| **Horizontal Scaling** | ⚠️ Read Replicas | ⚠️ Read Replicas | ✅ Sharding | ✅ Clustering | ✅ Native | ✅ Auto |
| **Query Complexity** | ✅ Complex SQL | ✅ Complex SQL | ✅ Rich Queries | ❌ Simple | ⚠️ Limited | ⚠️ Limited |
| **Consistency** | ✅ Strong | ✅ Strong | ⚠️ Eventual | ✅ Strong | ⚠️ Tunable | ⚠️ Eventual |
| **Ops Complexity** | ⚠️ Moderate | ⚠️ Moderate | ⚠️ Moderate | ✅ Simple | ❌ Complex | ✅ Managed |

### Use Case Mapping

#### E-commerce Platform
```python
class EcommerceDataArchitecture:
    """Multi-database architecture for e-commerce"""

    def __init__(self):
        # PostgreSQL for core transactional data
        self.postgres = PostgreSQLConnection()

        # MongoDB for product catalog
        self.mongodb = MongoDBConnection()

        # Redis for caching and sessions
        self.redis = RedisConnection()

        # Elasticsearch for search
        self.elasticsearch = ElasticsearchConnection()

    def create_order(self, order_data):
        """Use PostgreSQL for ACID transactions"""
        with self.postgres.transaction():
            order = self.postgres.create_order(order_data)
            self.postgres.update_inventory(order.items)
            self.postgres.create_payment_record(order.id)

            # Invalidate cache
            self.redis.delete(f"user:cart:{order.user_id}")

            return order

    def get_product_details(self, product_id):
        """Use MongoDB for flexible product data"""
        # Try cache first
        cached = self.redis.get(f"product:{product_id}")
        if cached:
            return json.loads(cached)

        product = self.mongodb.products.find_one({"_id": product_id})

        # Cache for 1 hour
        self.redis.setex(f"product:{product_id}", 3600, json.dumps(product))

        return product

    def search_products(self, query, filters):
        """Use Elasticsearch for full-text search"""
        return self.elasticsearch.search({
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["name^2", "description", "tags"]
                        }
                    },
                    "filter": filters
                }
            }
        })
```

#### Social Media Platform
```python
class SocialMediaDataArchitecture:
    def __init__(self):
        # PostgreSQL for user relationships
        self.postgres = PostgreSQLConnection()

        # Cassandra for posts and timeline
        self.cassandra = CassandraConnection()

        # Redis for real-time features
        self.redis = RedisConnection()

    def create_post(self, user_id, content):
        """Use Cassandra for high write throughput"""
        post_id = uuid.uuid4()
        timestamp = datetime.now()

        # Store post
        self.cassandra.execute("""
            INSERT INTO posts (post_id, user_id, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (post_id, user_id, content, timestamp))

        # Fan out to followers' timelines
        followers = self.postgres.get_followers(user_id)
        for follower_id in followers:
            self.cassandra.execute("""
                INSERT INTO user_timeline (user_id, post_id, created_at)
                VALUES (?, ?, ?)
            """, (follower_id, post_id, timestamp))

    def get_user_timeline(self, user_id, limit=20):
        """Get timeline from Cassandra"""
        return self.cassandra.execute("""
            SELECT * FROM user_timeline
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
```

## 🚀 Cloud Database Services

### AWS RDS (Relational Database Service)
**Managed SQL databases in the cloud**

#### Benefits
- ✅ **Automated Management**: Backups, patching, monitoring
- ✅ **High Availability**: Multi-AZ deployments
- ✅ **Scaling**: Read replicas, vertical scaling
- ✅ **Security**: Encryption, VPC isolation

#### When to Use
- Need managed SQL database
- Want to reduce operational overhead
- Require high availability
- Need automated backups and patching

### Google Cloud Spanner
**Globally distributed, strongly consistent database**

#### Benefits
- ✅ **Global Consistency**: Strong consistency across regions
- ✅ **Horizontal Scaling**: Automatic sharding
- ✅ **SQL Interface**: Standard SQL with joins
- ✅ **High Availability**: 99.999% availability SLA

#### When to Use
- Global applications requiring strong consistency
- Financial applications
- Need SQL with global scale
- High availability requirements

### Azure Cosmos DB
**Multi-model, globally distributed database**

#### Benefits
- ✅ **Multi-Model**: Document, key-value, graph, column-family
- ✅ **Global Distribution**: Turnkey global distribution
- ✅ **Tunable Consistency**: 5 consistency levels
- ✅ **Serverless**: Pay-per-request pricing model

#### When to Use
- Multi-model data requirements
- Global distribution needs
- Tunable consistency requirements
- Azure-native applications

## 🔧 Database Performance Optimization

### Indexing Strategies

```python
# PostgreSQL index examples
"""
-- B-tree index (default)
CREATE INDEX idx_user_email ON users(email);

-- Partial index for active users only
CREATE INDEX idx_active_users ON users(user_id) WHERE active = true;

-- Composite index for complex queries
CREATE INDEX idx_order_user_date ON orders(user_id, created_at);

-- GIN index for JSON data
CREATE INDEX idx_product_attributes ON products USING GIN(attributes);

-- Expression index
CREATE INDEX idx_user_lower_email ON users(LOWER(email));
"""

# MongoDB index examples
"""
# Single field index
db.users.createIndex({ "email": 1 })

# Compound index
db.orders.createIndex({ "user_id": 1, "created_at": -1 })

# Text index for search
db.products.createIndex({ "name": "text", "description": "text" })

# Partial index
db.users.createIndex(
    { "email": 1 },
    { partialFilterExpression: { "active": true } }
)

# TTL index for expiring documents
db.sessions.createIndex(
    { "created_at": 1 },
    { expireAfterSeconds: 3600 }
)
"""
```

### Query Optimization

```python
class QueryOptimizer:
    def __init__(self, db_connection):
        self.db = db_connection

    def optimize_user_orders_query(self):
        # BAD: N+1 query problem
        def get_users_with_orders_bad():
            users = self.db.execute("SELECT * FROM users")
            for user in users:
                orders = self.db.execute(
                    "SELECT * FROM orders WHERE user_id = ?",
                    (user['id'],)
                )
                user['orders'] = orders
            return users

        # GOOD: Single query with JOIN
        def get_users_with_orders_good():
            return self.db.execute("""
                SELECT
                    u.user_id,
                    u.username,
                    u.email,
                    o.order_id,
                    o.total_amount,
                    o.created_at as order_date
                FROM users u
                LEFT JOIN orders o ON u.user_id = o.user_id
                ORDER BY u.user_id, o.created_at DESC
            """)

    def optimize_pagination(self, page, page_size):
        # BAD: OFFSET with large numbers is slow
        def paginate_bad():
            offset = (page - 1) * page_size
            return self.db.execute("""
                SELECT * FROM products
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (page_size, offset))

        # GOOD: Cursor-based pagination
        def paginate_good(last_created_at=None):
            if last_created_at:
                return self.db.execute("""
                    SELECT * FROM products
                    WHERE created_at < ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (last_created_at, page_size))
            else:
                return self.db.execute("""
                    SELECT * FROM products
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (page_size,))
```

### Connection Pooling

```python
import psycopg2.pool
import pymongo
import redis.connection

class DatabaseConnections:
    def __init__(self):
        # PostgreSQL connection pool
        self.postgres_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=5,
            maxconn=20,
            host='localhost',
            database='myapp',
            user='username',
            password='password'
        )

        # MongoDB connection with pool
        self.mongodb_client = pymongo.MongoClient(
            'mongodb://localhost:27017/',
            maxPoolSize=20,
            minPoolSize=5,
            serverSelectionTimeoutMS=5000
        )

        # Redis connection pool
        self.redis_pool = redis.ConnectionPool(
            host='localhost',
            port=6379,
            max_connections=20
        )
        self.redis_client = redis.Redis(connection_pool=self.redis_pool)

    def execute_postgres_query(self, query, params=None):
        connection = None
        try:
            connection = self.postgres_pool.getconn()
            cursor = connection.cursor()
            cursor.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount

            return result
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                self.postgres_pool.putconn(connection)
```

## ✅ Knowledge Check

After studying this section, you should be able to:

- [ ] Choose appropriate database technology for different use cases
- [ ] Understand trade-offs between SQL and NoSQL databases
- [ ] Design multi-database architectures
- [ ] Implement database performance optimizations
- [ ] Evaluate cloud database services for different scenarios

## 🔄 Quick Review Questions

1. **When would you choose MongoDB over PostgreSQL for a new project?**
2. **What are the trade-offs between DynamoDB and self-managed Cassandra?**
3. **How do you decide between using Redis as a cache vs primary database?**
4. **What factors influence the choice between cloud and on-premise databases?**
5. **When is it appropriate to use multiple databases in one application?**

## 🚀 Next Steps

- Study [Message Queues](../message-queues/) for async data processing
- Learn [Caching](../caching/) strategies to complement database performance
- Practice database selection in [Real-World Examples](../../04-real-world-examples/)

---

**Remember**: Database choice significantly impacts your application's scalability, consistency, and operational complexity. Consider your specific requirements, team expertise, and long-term growth plans when making this critical decision!