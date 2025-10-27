# Step-by-Step System Design Interview Approach 🟢

## 🎯 The 8-Step Framework

This structured approach will help you tackle any system design interview question systematically and impress your interviewer with organized thinking.

## ⏱️ Time Allocation (45-60 minute interview)

| Step | Time | Percentage |
|------|------|-----------|
| 1. Clarify Requirements | 5-7 min | 12% |
| 2. Estimate Scale | 3-5 min | 8% |
| 3. Define System Interface | 5 min | 10% |
| 4. High-Level Design | 10-15 min | 25% |
| 5. Database Design | 8-10 min | 18% |
| 6. Detailed Component Design | 10-15 min | 25% |
| 7. Scale the Design | 5-10 min | 15% |
| 8. Monitor & Wrap-up | 2-5 min | 7% |

## 📋 Step 1: Clarify Requirements (5-7 minutes)

### Essential Questions to Ask

#### Functional Requirements
- **Core Features**: "What are the main features users should be able to do?"
- **User Actions**: "What specific actions can users perform?"
- **Business Logic**: "Are there any special business rules I should know?"
- **Data Types**: "What types of data will the system handle?"

#### Non-Functional Requirements
- **Scale**: "How many users are we expecting?"
- **Performance**: "What are the latency requirements?"
- **Availability**: "What's the expected uptime?"
- **Consistency**: "How consistent should the data be?"

### Example: Chat Application
```
Interviewer: "Design a chat application like WhatsApp"

Your Questions:
✅ "Is this 1-on-1 messaging or group chats too?"
✅ "Do we need features like file sharing, voice messages?"
✅ "Should messages be persistent or temporary?"
✅ "Do we need online status indicators?"
✅ "How many users are we targeting?"
✅ "What's the expected message volume per day?"
✅ "Any specific latency requirements for message delivery?"
✅ "What about offline message delivery?"

Avoid asking:
❌ "Should we use React or Angular?" (too detailed)
❌ "What database should we use?" (that's for you to decide)
❌ "Can I use AWS?" (focus on concepts first)
```

### Requirements Template

```
FUNCTIONAL REQUIREMENTS:
- User registration and authentication
- Send/receive real-time messages
- Message history storage
- Online status indicators

NON-FUNCTIONAL REQUIREMENTS:
- 500M users, 10M daily active
- Real-time delivery (<100ms)
- 99.9% availability
- Messages stored permanently
- Global user base
```

## 🧮 Step 2: Estimate Scale (3-5 minutes)

### Back-of-Envelope Calculations

#### Key Numbers to Remember
```
1 million = 10^6
1 billion = 10^9
1 day = 86,400 seconds ≈ 10^5 seconds
1 month = 30 days = 2.6 million seconds ≈ 2.5 × 10^6 seconds
```

#### Example Calculation: Chat App
```
GIVEN:
- 500M total users
- 10% daily active = 50M DAU
- Each user sends 20 messages/day

CALCULATIONS:
Daily Messages:
50M users × 20 messages = 1B messages/day

Messages Per Second:
1B messages ÷ 86,400 seconds ≈ 12K messages/second

Peak Traffic (2x average):
12K × 2 = 24K messages/second

Storage per Day:
1B messages × 100 bytes/message = 100GB/day

5-Year Storage:
100GB × 365 × 5 = 182TB

Bandwidth:
Incoming: 12K × 100 bytes = 1.2MB/second
Outgoing: 12K × 100 bytes × 2 (fanout) = 2.4MB/second
```

### Quick Estimation Templates

#### Daily Active Users (DAU)
```
Total Users → DAU (rule of thumb: 10-30% of total)
500M total → 50M DAU (10%)
100M total → 30M DAU (30% for engaged apps)
```

#### Storage Calculation
```
Records per day × Record size × Retention period
Example: 1M tweets × 280 bytes × 365 days × 5 years = 500GB
```

#### QPS (Queries Per Second)
```
Daily requests ÷ 86,400 seconds
Peak QPS = Average QPS × 2 (or 3 for very spiky traffic)
```

## 🔌 Step 3: Define System Interface (5 minutes)

### API Design Principles
- **RESTful**: Use standard HTTP methods
- **Clear naming**: Intuitive endpoint names
- **Consistent**: Follow patterns across all endpoints
- **Minimal**: Only expose what's needed

### Example: Chat Application APIs

```python
# User Management
POST /api/users/register
POST /api/users/login
GET  /api/users/profile/{user_id}

# Messaging
POST /api/messages
GET  /api/messages/{conversation_id}?limit=20&offset=0
PUT  /api/messages/{message_id}/read

# Conversations
GET  /api/conversations/{user_id}
POST /api/conversations
DELETE /api/conversations/{conversation_id}

# Real-time
WebSocket: /ws/chat/{user_id}
```

### Detailed API Specification

```python
# Send Message API
POST /api/messages
Request:
{
    "sender_id": "user123",
    "receiver_id": "user456",
    "content": "Hello, how are you?",
    "message_type": "text",  # text, image, file
    "timestamp": "2024-10-18T10:30:00Z"
}

Response:
{
    "message_id": "msg_789",
    "status": "sent",
    "timestamp": "2024-10-18T10:30:01Z"
}

# Get Messages API
GET /api/messages/{conversation_id}?limit=20&before=msg_123
Response:
{
    "messages": [
        {
            "message_id": "msg_789",
            "sender_id": "user123",
            "content": "Hello!",
            "timestamp": "2024-10-18T10:30:00Z",
            "read_status": "delivered"
        }
    ],
    "has_more": true,
    "next_cursor": "msg_456"
}
```

## 🏗️ Step 4: High-Level Design (10-15 minutes)

### Start Simple, Then Add Complexity

#### Basic Architecture
```
[Mobile App] → [Load Balancer] → [API Gateway] → [Chat Service] → [Database]
[Web App]                                                        → [Message Queue]
```

#### Components to Include
1. **Client Applications** (Mobile, Web)
2. **Load Balancer** (distribute traffic)
3. **API Gateway** (routing, authentication)
4. **Core Services** (business logic)
5. **Databases** (data storage)
6. **Message Queues** (async processing)
7. **Cache Layer** (performance)

#### Progressive Complexity
```
Version 1: Basic request-response
[Client] → [Server] → [Database]

Version 2: Add caching
[Client] → [Server] → [Cache] → [Database]

Version 3: Add load balancing
[Client] → [Load Balancer] → [Server Pool] → [Cache] → [Database]

Version 4: Add microservices
[Client] → [API Gateway] → [User Service]     → [User DB]
                        → [Message Service]  → [Message DB]
                        → [Notification Service] → [Queue]
```

### Drawing Tips
- **Use boxes and arrows**: Clear, simple diagrams
- **Label everything**: Don't assume interviewer knows what boxes mean
- **Show data flow**: Indicate direction of requests/responses
- **Start simple**: Add complexity gradually

## 🗄️ Step 5: Database Design (8-10 minutes)

### Schema Design Process

#### 1. Identify Entities
```
Chat Application Entities:
- Users
- Messages
- Conversations
- User_Conversations (many-to-many)
```

#### 2. Define Relationships
```
Users (1) ←→ (M) Messages
Users (M) ←→ (M) Conversations
Messages (M) ←→ (1) Conversations
```

#### 3. Design Tables

```sql
-- Users table
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP,
    is_online BOOLEAN DEFAULT FALSE
);

-- Conversations table
CREATE TABLE conversations (
    conversation_id BIGINT PRIMARY KEY,
    conversation_type ENUM('direct', 'group') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Messages table (consider partitioning for scale)
CREATE TABLE messages (
    message_id BIGINT PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    sender_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    message_type ENUM('text', 'image', 'file') DEFAULT 'text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    INDEX idx_conversation_time (conversation_id, created_at)
);

-- User-Conversation mapping
CREATE TABLE user_conversations (
    user_id BIGINT NOT NULL,
    conversation_id BIGINT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_read_message_id BIGINT,
    PRIMARY KEY (user_id, conversation_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);
```

### SQL vs NoSQL Decision Framework

#### Choose SQL When:
- ✅ Complex relationships between entities
- ✅ ACID transactions required
- ✅ Complex queries needed
- ✅ Data consistency is critical
- ✅ Structured data with known schema

#### Choose NoSQL When:
- ✅ Simple data access patterns
- ✅ Massive scale requirements
- ✅ Flexible schema needed
- ✅ High write volume
- ✅ Geographic distribution

### Example NoSQL Design (MongoDB)

```javascript
// Users collection
{
  "_id": "user123",
  "username": "john_doe",
  "email": "john@example.com",
  "password_hash": "...",
  "created_at": "2024-01-01T00:00:00Z",
  "last_seen": "2024-10-18T10:30:00Z",
  "is_online": true
}

// Messages collection (partitioned by conversation_id)
{
  "_id": "msg_789",
  "conversation_id": "conv_456",
  "sender_id": "user123",
  "content": "Hello, how are you?",
  "message_type": "text",
  "created_at": "2024-10-18T10:30:00Z",
  "read_by": [
    {"user_id": "user456", "read_at": "2024-10-18T10:31:00Z"}
  ]
}
```

## 🔧 Step 6: Detailed Component Design (10-15 minutes)

### Deep Dive into Key Components

#### Message Service Design
```python
class MessageService:
    def __init__(self, db, cache, message_queue):
        self.db = db
        self.cache = cache
        self.message_queue = message_queue

    def send_message(self, sender_id, receiver_id, content):
        # 1. Validate inputs
        if not self.validate_message(content):
            raise ValueError("Invalid message content")

        # 2. Check if users exist and can communicate
        if not self.can_send_message(sender_id, receiver_id):
            raise PermissionError("Cannot send message")

        # 3. Create message object
        message = {
            "message_id": self.generate_id(),
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content,
            "timestamp": datetime.utcnow(),
            "status": "sent"
        }

        # 4. Store in database
        self.db.save_message(message)

        # 5. Cache recent messages
        conversation_key = f"messages:{min(sender_id, receiver_id)}:{max(sender_id, receiver_id)}"
        self.cache.add_to_list(conversation_key, message, max_size=100)

        # 6. Queue for real-time delivery
        self.message_queue.publish("message_delivery", {
            "receiver_id": receiver_id,
            "message": message
        })

        return message["message_id"]
```

#### WebSocket Connection Manager
```python
class WebSocketManager:
    def __init__(self):
        self.connections = {}  # user_id -> websocket connection
        self.user_status = {}  # user_id -> last_seen

    def connect_user(self, user_id, websocket):
        """Handle new WebSocket connection"""
        # Store connection
        self.connections[user_id] = websocket
        self.user_status[user_id] = datetime.utcnow()

        # Notify friends user is online
        self.broadcast_status_change(user_id, "online")

    def disconnect_user(self, user_id):
        """Handle WebSocket disconnection"""
        if user_id in self.connections:
            del self.connections[user_id]

        self.user_status[user_id] = datetime.utcnow()
        self.broadcast_status_change(user_id, "offline")

    def send_message_to_user(self, user_id, message):
        """Send message to specific user"""
        if user_id in self.connections:
            try:
                self.connections[user_id].send(json.dumps(message))
                return True
            except:
                # Connection broken, clean up
                self.disconnect_user(user_id)

        return False  # User offline or connection failed
```

### Algorithms and Data Structures

#### Message Ordering
```python
def ensure_message_ordering(messages):
    """Ensure messages are delivered in order"""
    # Sort by timestamp
    return sorted(messages, key=lambda m: m['timestamp'])

def handle_out_of_order_delivery(message, expected_sequence):
    """Handle messages that arrive out of order"""
    if message['sequence_number'] == expected_sequence:
        # Deliver immediately
        deliver_message(message)
        return expected_sequence + 1
    else:
        # Buffer for later delivery
        buffer_message(message)
        return expected_sequence
```

#### Message Deduplication
```python
class MessageDeduplicator:
    def __init__(self, cache):
        self.cache = cache

    def is_duplicate(self, message_id, sender_id):
        """Check if message was already processed"""
        key = f"processed:{sender_id}:{message_id}"
        return self.cache.exists(key)

    def mark_processed(self, message_id, sender_id):
        """Mark message as processed"""
        key = f"processed:{sender_id}:{message_id}"
        self.cache.set(key, True, ttl=3600)  # 1 hour
```

## ⚡ Step 7: Scale the Design (5-10 minutes)

### Identify Bottlenecks

#### Database Bottlenecks
- **Symptoms**: Slow queries, high CPU usage
- **Solutions**:
  - Read replicas for read scaling
  - Sharding for write scaling
  - Database indexing optimization

#### Application Server Bottlenecks
- **Symptoms**: High response times, CPU maxed out
- **Solutions**:
  - Horizontal scaling (more servers)
  - Auto-scaling based on metrics
  - Code optimization

#### Network Bottlenecks
- **Symptoms**: High latency, bandwidth limits
- **Solutions**:
  - CDN for static content
  - Geographic distribution
  - Data compression

### Scaling Solutions

#### Database Scaling
```
Read Scaling:
[App Servers] → [Master DB] (writes)
              → [Read Replica 1] (reads)
              → [Read Replica 2] (reads)

Write Scaling (Sharding):
Users A-H → [Shard 1]
Users I-P → [Shard 2]
Users Q-Z → [Shard 3]
```

#### Microservices Architecture
```
[API Gateway] → [User Service] → [User DB]
              → [Message Service] → [Message DB]
              → [Notification Service] → [Queue]
              → [File Service] → [Object Storage]
```

#### Caching Strategy
```
Multi-Level Caching:
[Client] → [CDN] → [Load Balancer] → [App Server] → [Redis] → [Database]
          Cache    Cache              L1 Cache      L2 Cache
```

### Geographic Distribution
```
Global Architecture:
[US Users] → [US Region] → [US Database]
[EU Users] → [EU Region] → [EU Database]
[Asia Users] → [Asia Region] → [Asia Database]

Cross-region replication for global features
```

## 📊 Step 8: Monitor & Wrap-up (2-5 minutes)

### Monitoring Strategy

#### Key Metrics
```python
# Application Metrics
- Request rate (QPS)
- Response time (latency percentiles)
- Error rate
- Active connections

# Infrastructure Metrics
- CPU, Memory, Disk usage
- Network I/O
- Database connections
- Cache hit ratio

# Business Metrics
- Daily/Monthly active users
- Message delivery success rate
- User engagement metrics
```

#### Alerting
```python
# Critical Alerts
- Service downtime (availability < 99.5%)
- High error rate (> 1%)
- Database connection failures

# Warning Alerts
- High response time (p95 > 500ms)
- Low cache hit ratio (< 80%)
- Approaching rate limits
```

### Final Considerations

#### Security
- Authentication/Authorization
- Input validation
- Rate limiting
- Data encryption

#### Deployment
- Blue-green deployments
- Feature flags
- Database migrations
- Rollback strategies

## ✅ Interview Success Checklist

### Before You Start
- [ ] Listen carefully to the problem statement
- [ ] Ask clarifying questions (don't make assumptions)
- [ ] Agree on scope with interviewer

### During the Design
- [ ] Think out loud (communicate your reasoning)
- [ ] Start simple, add complexity gradually
- [ ] Draw clear diagrams with labels
- [ ] Consider trade-offs and alternatives
- [ ] Estimate numbers and validate with interviewer

### Wrapping Up
- [ ] Summarize your design
- [ ] Discuss potential improvements
- [ ] Address any concerns raised
- [ ] Show enthusiasm and curiosity

## 🚫 Common Mistakes to Avoid

1. **Jumping to solution without understanding requirements**
2. **Over-engineering the initial design**
3. **Not asking enough clarifying questions**
4. **Ignoring non-functional requirements**
5. **Poor time management**
6. **Not explaining trade-offs**
7. **Focusing only on happy path scenarios**
8. **Not considering failure cases**
9. **Using buzzwords without understanding**
10. **Not validating design with interviewer**

---

**Remember**: The goal is to demonstrate your thinking process, not to arrive at a perfect solution. Show how you approach complex problems systematically!