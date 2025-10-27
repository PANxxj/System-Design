# Database Concepts 🟢

## 🎯 Learning Objectives
- Understand SQL vs NoSQL database selection criteria
- Learn database scaling strategies and trade-offs
- Master data modeling principles for different database types
- Design effective database architectures for various use cases

## 📖 Database Fundamentals

### What is a Database?
A **database** is an organized collection of structured information stored electronically in a computer system. It's managed by a Database Management System (DBMS) that provides:
- Data storage and retrieval
- Data integrity and consistency
- Concurrent access control
- Security and access control
- Backup and recovery

### Why Use Databases?
- **Data Persistence**: Data survives application restarts
- **Concurrent Access**: Multiple users can access data safely
- **Data Integrity**: Enforce business rules and constraints
- **Query Capability**: Efficient data retrieval and manipulation
- **Scalability**: Handle growing amounts of data and users

## 🗄️ SQL Databases (RDBMS)

### Characteristics
- **Structured Data**: Fixed schema with tables, rows, and columns
- **ACID Properties**: Atomicity, Consistency, Isolation, Durability
- **Relationships**: Foreign keys and joins between tables
- **SQL Language**: Standardized query language
- **Strong Consistency**: All reads receive the most recent write

### Popular SQL Databases
- **PostgreSQL**: Advanced open-source database with JSON support
- **MySQL**: Widely used open-source database
- **Oracle**: Enterprise-grade commercial database
- **SQL Server**: Microsoft's enterprise database solution

### When to Use SQL Databases
✅ **Choose SQL when you need:**
- Complex relationships between data entities
- ACID transactions for financial or critical data
- Complex queries with joins and aggregations
- Strong consistency requirements
- Mature ecosystem and tooling
- Well-defined, stable schema

### Example: E-commerce Database Schema

```sql
-- Users table
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    product_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id BIGINT,
    inventory_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    INDEX idx_category (category_id),
    INDEX idx_price (price)
);

-- Orders table
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- Order items table (many-to-many relationship)
CREATE TABLE order_items (
    order_item_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    UNIQUE KEY unique_order_product (order_id, product_id)
);
```

### ACID Properties Deep Dive

#### Atomicity
All operations in a transaction succeed or fail together.

```sql
-- Example: Transfer money between accounts (all or nothing)
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;

-- If any operation fails, entire transaction is rolled back
COMMIT;
```

#### Consistency
Database moves from one valid state to another valid state.

```sql
-- Example: Enforce business rules with constraints
ALTER TABLE accounts ADD CONSTRAINT check_positive_balance
CHECK (balance >= 0);

-- This prevents accounts from going negative
UPDATE accounts SET balance = balance - 1000 WHERE account_id = 1;
-- ERROR: Check constraint 'check_positive_balance' is violated
```

#### Isolation
Concurrent transactions don't interfere with each other.

```sql
-- Transaction 1
START TRANSACTION;
SELECT balance FROM accounts WHERE account_id = 1; -- Returns 1000
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
-- Transaction sees balance as 900, but not committed yet

-- Transaction 2 (running concurrently)
SELECT balance FROM accounts WHERE account_id = 1; -- Still returns 1000
-- Won't see the update until Transaction 1 commits

COMMIT; -- Now Transaction 2 will see the updated balance
```

#### Durability
Committed transactions persist even after system failures.

```sql
-- Once this transaction commits, the changes are permanent
START TRANSACTION;
INSERT INTO orders (user_id, total_amount) VALUES (123, 99.99);
COMMIT;

-- Even if server crashes after COMMIT, the order will be saved
```

## 🗄️ NoSQL Databases

### Types of NoSQL Databases

#### 1. Document Databases
Store data as documents (usually JSON-like).

**Examples**: MongoDB, CouchDB, Amazon DocumentDB

```javascript
// MongoDB document example
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "user_id": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "zipcode": "94105"
  },
  "orders": [
    {
      "order_id": "order456",
      "total": 99.99,
      "items": ["product1", "product2"]
    }
  ],
  "created_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Best for**: Content management, user profiles, catalogs

#### 2. Key-Value Stores
Simple key-value pairs for fast lookups.

**Examples**: Redis, DynamoDB, Riak

```python
# Redis key-value examples
redis.set("user:123:profile", json.dumps({
    "name": "John Doe",
    "email": "john@example.com"
}))

redis.set("session:abc123", "user:123", ex=3600)  # Expires in 1 hour

# Hash for related fields
redis.hset("user:123:stats", mapping={
    "login_count": 42,
    "last_login": "2024-01-01T12:00:00Z"
})
```

**Best for**: Caching, session storage, real-time recommendations

#### 3. Column-Family
Store data in column families, optimized for queries over large datasets.

**Examples**: Cassandra, HBase, Amazon SimpleDB

```sql
-- Cassandra CQL example
CREATE TABLE user_activity (
    user_id UUID,
    activity_date DATE,
    activity_time TIMESTAMP,
    activity_type TEXT,
    activity_data MAP<TEXT, TEXT>,
    PRIMARY KEY (user_id, activity_date, activity_time)
) WITH CLUSTERING ORDER BY (activity_date DESC, activity_time DESC);

-- Insert activity data
INSERT INTO user_activity (user_id, activity_date, activity_time, activity_type, activity_data)
VALUES (123e4567-e89b-12d3-a456-426614174000, '2024-01-01', '2024-01-01 12:00:00', 'page_view', {'page': '/products', 'referrer': 'google'});
```

**Best for**: Time-series data, IoT sensors, analytics

#### 4. Graph Databases
Store data as nodes and relationships.

**Examples**: Neo4j, Amazon Neptune, ArangoDB

```cypher
// Neo4j Cypher query examples
// Create nodes and relationships
CREATE (john:Person {name: 'John Doe', age: 30})
CREATE (jane:Person {name: 'Jane Smith', age: 28})
CREATE (company:Company {name: 'Tech Corp'})
CREATE (john)-[:WORKS_FOR]->(company)
CREATE (jane)-[:WORKS_FOR]->(company)
CREATE (john)-[:FRIENDS_WITH]->(jane)

// Find mutual friends
MATCH (person:Person {name: 'John Doe'})-[:FRIENDS_WITH]->(friend)-[:FRIENDS_WITH]->(mutualFriend)
WHERE NOT (person)-[:FRIENDS_WITH]->(mutualFriend)
RETURN mutualFriend.name
```

**Best for**: Social networks, recommendation engines, fraud detection

### When to Use NoSQL Databases

✅ **Choose NoSQL when you need:**
- Flexible or evolving schema
- Massive scale (horizontal scaling)
- High write throughput
- Simple access patterns (key lookups)
- Eventual consistency is acceptable
- Rapid development and iteration

## ⚖️ SQL vs NoSQL Decision Framework

### Decision Matrix

| Factor | SQL | NoSQL |
|--------|-----|-------|
| **Data Structure** | Structured, related | Flexible, varied |
| **Schema** | Fixed, predefined | Dynamic, evolving |
| **Scalability** | Vertical (scale up) | Horizontal (scale out) |
| **Consistency** | Strong (ACID) | Eventual (BASE) |
| **Queries** | Complex (SQL) | Simple (key-based) |
| **Transactions** | Multi-table ACID | Limited or eventual |
| **Maturity** | Very mature | Newer, evolving |

### Real-World Use Cases

#### E-commerce Platform
```python
# Hybrid approach - use both SQL and NoSQL
class EcommercePlatform:
    def __init__(self):
        # SQL for transactional data
        self.postgres = PostgreSQLConnection()

        # NoSQL for various use cases
        self.redis = RedisConnection()      # Caching, sessions
        self.mongodb = MongoDBConnection()  # Product catalog
        self.elasticsearch = ElasticsearchConnection()  # Search

    def create_order(self, user_id, items):
        """Use SQL for ACID transactions"""
        with self.postgres.transaction():
            order = self.postgres.create_order(user_id, items)
            self.postgres.update_inventory(items)
            self.postgres.create_payment_record(order.id)
            return order

    def get_product_catalog(self, category, filters):
        """Use NoSQL for flexible product data"""
        return self.mongodb.find_products({
            'category': category,
            'filters': filters,
            'in_stock': True
        })

    def search_products(self, query):
        """Use search engine for full-text search"""
        return self.elasticsearch.search({
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['name', 'description', 'tags']
                }
            }
        })

    def get_user_session(self, session_id):
        """Use key-value store for fast session lookup"""
        return self.redis.get(f"session:{session_id}")
```

## 📊 Database Scaling Strategies

### Vertical Scaling (Scale Up)
Add more power to existing database server.

```python
# Example: Upgrading database server
class DatabaseUpgrade:
    def scale_vertically(self):
        """Increase server resources"""
        return {
            'before': {'cpu': '4 cores', 'memory': '16GB', 'storage': '1TB SSD'},
            'after': {'cpu': '16 cores', 'memory': '64GB', 'storage': '4TB SSD'},
            'pros': ['Simple', 'No application changes', 'Maintains consistency'],
            'cons': ['Hardware limits', 'Expensive', 'Single point of failure']
        }
```

### Horizontal Scaling (Scale Out)

#### Read Replicas
```python
class ReadReplicaSetup:
    def __init__(self):
        self.master = DatabaseConnection('master-db')
        self.read_replicas = [
            DatabaseConnection('replica-1'),
            DatabaseConnection('replica-2'),
            DatabaseConnection('replica-3')
        ]
        self.replica_index = 0

    def write(self, query, params):
        """All writes go to master"""
        return self.master.execute(query, params)

    def read(self, query, params):
        """Distribute reads across replicas"""
        replica = self.read_replicas[self.replica_index]
        self.replica_index = (self.replica_index + 1) % len(self.read_replicas)
        return replica.execute(query, params)

# Usage
db = ReadReplicaSetup()

# Writes to master
db.write("INSERT INTO users (name, email) VALUES (?, ?)", ("John", "john@example.com"))

# Reads from replicas
users = db.read("SELECT * FROM users WHERE active = ?", (True,))
```

#### Database Sharding
```python
class DatabaseSharding:
    def __init__(self, shards):
        self.shards = shards  # List of database connections

    def get_shard(self, user_id):
        """Determine which shard contains user data"""
        shard_index = hash(user_id) % len(self.shards)
        return self.shards[shard_index]

    def get_user(self, user_id):
        """Get user from appropriate shard"""
        shard = self.get_shard(user_id)
        return shard.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))

    def create_user(self, user_data):
        """Create user in appropriate shard"""
        shard = self.get_shard(user_data['user_id'])
        return shard.execute(
            "INSERT INTO users (user_id, name, email) VALUES (?, ?, ?)",
            (user_data['user_id'], user_data['name'], user_data['email'])
        )

    def get_user_friends(self, user_id):
        """Cross-shard query - more complex"""
        # This requires querying multiple shards
        all_friends = []
        for shard in self.shards:
            friends = shard.execute(
                "SELECT * FROM friendships WHERE user_id = ?",
                (user_id,)
            )
            all_friends.extend(friends)
        return all_friends
```

### Sharding Strategies

#### 1. Range-Based Sharding
```python
class RangeBasedSharding:
    def __init__(self, shards):
        self.shards = shards
        # Define ranges for each shard
        self.ranges = [
            {'min': 0, 'max': 999999, 'shard': shards[0]},
            {'min': 1000000, 'max': 1999999, 'shard': shards[1]},
            {'min': 2000000, 'max': 2999999, 'shard': shards[2]}
        ]

    def get_shard(self, user_id):
        for range_config in self.ranges:
            if range_config['min'] <= user_id <= range_config['max']:
                return range_config['shard']
        raise ValueError(f"No shard found for user_id: {user_id}")
```

#### 2. Hash-Based Sharding
```python
class HashBasedSharding:
    def __init__(self, shards):
        self.shards = shards

    def get_shard(self, key):
        """Use hash function to determine shard"""
        import hashlib
        hash_value = int(hashlib.md5(str(key).encode()).hexdigest(), 16)
        shard_index = hash_value % len(self.shards)
        return self.shards[shard_index]
```

#### 3. Directory-Based Sharding
```python
class DirectoryBasedSharding:
    def __init__(self, shards):
        self.shards = shards
        self.directory = {}  # key -> shard mapping

    def assign_to_shard(self, key, shard_id):
        """Manually assign key to specific shard"""
        self.directory[key] = shard_id

    def get_shard(self, key):
        """Look up shard in directory"""
        shard_id = self.directory.get(key)
        if shard_id is None:
            raise ValueError(f"No shard assigned for key: {key}")
        return self.shards[shard_id]
```

## 🔍 Database Performance Optimization

### Indexing Strategies

#### 1. Single Column Index
```sql
-- Create index on frequently queried column
CREATE INDEX idx_user_email ON users(email);

-- Query that benefits from index
SELECT * FROM users WHERE email = 'john@example.com';
```

#### 2. Composite Index
```sql
-- Create composite index for multi-column queries
CREATE INDEX idx_order_user_date ON orders(user_id, created_at);

-- Query that benefits from composite index
SELECT * FROM orders
WHERE user_id = 123
AND created_at >= '2024-01-01'
ORDER BY created_at DESC;
```

#### 3. Partial Index
```sql
-- Index only active users to save space
CREATE INDEX idx_active_users ON users(user_id) WHERE active = true;

-- Query that benefits from partial index
SELECT * FROM users WHERE user_id = 123 AND active = true;
```

### Query Optimization

#### 1. Avoid N+1 Queries
```python
# BAD: N+1 query problem
def get_users_with_orders_bad():
    users = db.execute("SELECT * FROM users")
    for user in users:
        # This creates N additional queries!
        orders = db.execute("SELECT * FROM orders WHERE user_id = ?", (user['id'],))
        user['orders'] = orders
    return users

# GOOD: Use JOIN to fetch data in one query
def get_users_with_orders_good():
    return db.execute("""
        SELECT u.*, o.order_id, o.total_amount, o.created_at as order_date
        FROM users u
        LEFT JOIN orders o ON u.user_id = o.user_id
        ORDER BY u.user_id, o.created_at DESC
    """)
```

#### 2. Use LIMIT and Pagination
```sql
-- Instead of fetching all results
SELECT * FROM products ORDER BY created_at DESC;

-- Use pagination
SELECT * FROM products
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;  -- First page

SELECT * FROM products
ORDER BY created_at DESC
LIMIT 20 OFFSET 20; -- Second page
```

#### 3. Query Analysis
```sql
-- PostgreSQL: Analyze query execution plan
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'john@example.com';

-- MySQL: Check query execution
EXPLAIN SELECT * FROM users WHERE email = 'john@example.com';
```

### Connection Pooling

```python
import psycopg2.pool

class DatabaseConnectionPool:
    def __init__(self, min_connections=5, max_connections=20):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            min_connections,
            max_connections,
            host='localhost',
            database='myapp',
            user='username',
            password='password'
        )

    def execute_query(self, query, params=None):
        """Execute query using connection from pool"""
        connection = None
        try:
            # Get connection from pool
            connection = self.pool.getconn()
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
                # Return connection to pool
                self.pool.putconn(connection)
```

## 🛡️ Data Consistency and CAP Theorem

### CAP Theorem
In a distributed database system, you can only guarantee 2 out of 3:

- **Consistency**: All nodes see the same data at the same time
- **Availability**: System remains operational
- **Partition Tolerance**: System continues despite network failures

#### Examples:

**CP Systems (Consistency + Partition Tolerance)**
- Traditional RDBMS with master-slave replication
- Sacrifice availability during network partitions
- Examples: PostgreSQL with synchronous replication

**AP Systems (Availability + Partition Tolerance)**
- Eventual consistency, always available
- May return stale data during partitions
- Examples: Cassandra, DynamoDB

**CA Systems (Consistency + Availability)**
- Only possible without network partitions
- Not practical for distributed systems
- Examples: Single-node databases

### Consistency Models

#### 1. Strong Consistency
```python
class StrongConsistencyDB:
    def __init__(self, nodes):
        self.nodes = nodes
        self.master = nodes[0]

    def write(self, key, value):
        """Write to master, synchronously replicate to all nodes"""
        # Write to master
        self.master.write(key, value)

        # Synchronously replicate to all replicas
        for replica in self.nodes[1:]:
            replica.write(key, value)

        # Only return success if all nodes updated
        return True

    def read(self, key):
        """Read from master to ensure consistency"""
        return self.master.read(key)
```

#### 2. Eventual Consistency
```python
class EventualConsistencyDB:
    def __init__(self, nodes):
        self.nodes = nodes

    def write(self, key, value):
        """Write to any node, asynchronously propagate"""
        # Write to local node immediately
        primary_node = self.nodes[0]
        primary_node.write(key, value)

        # Asynchronously propagate to other nodes
        for node in self.nodes[1:]:
            self._async_replicate(node, key, value)

        return True  # Return immediately

    def read(self, key):
        """Read from any available node"""
        for node in self.nodes:
            try:
                return node.read(key)
            except NodeUnavailable:
                continue
        raise AllNodesUnavailable()

    def _async_replicate(self, node, key, value):
        """Asynchronously replicate data to node"""
        # This would typically use a message queue
        threading.Thread(target=node.write, args=(key, value)).start()
```

## ✅ Knowledge Check

After studying this section, you should be able to:

- [ ] Choose between SQL and NoSQL databases for different use cases
- [ ] Design appropriate database schemas for relational and document databases
- [ ] Understand ACID properties and when they're important
- [ ] Implement database scaling strategies (replication, sharding)
- [ ] Optimize database performance through indexing and query optimization
- [ ] Apply CAP theorem to understand consistency trade-offs

## 🔄 Quick Review Questions

1. **When would you choose MongoDB over PostgreSQL for a new project?**
2. **What's the difference between read replicas and database sharding?**
3. **How does the CAP theorem influence database design decisions?**
4. **What are the pros and cons of hash-based vs range-based sharding?**
5. **When might you sacrifice ACID properties for performance?**

## 🚀 Next Steps

- Study [Consistency Patterns](consistency-patterns.md) to understand distributed data consistency
- Learn [Caching Strategies](caching-strategies.md) to reduce database load
- Practice database design in [Real-World Examples](../04-real-world-examples/)

---

**Remember**: Database choice is one of the most important architectural decisions. Consider your data model, consistency requirements, scale needs, and team expertise when making this choice!