# Mock Interview Practice Sessions 🟡

## 🎯 Learning Objectives
- Practice system design interviews in realistic settings
- Develop communication and problem-solving skills
- Learn to handle follow-up questions and deep dives
- Build confidence for actual interviews

## 🎭 Mock Interview Format

### Standard 45-Minute Interview Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Interview Timeline                        │
├─────────────────────────────────────────────────────────────┤
│ 0-5 min    │ Introduction & Problem Statement              │
│ 5-10 min   │ Requirements Gathering & Clarification       │
│ 10-15 min  │ High-Level Architecture Design               │
│ 15-30 min  │ Detailed Component Design                    │
│ 30-40 min  │ Deep Dive & Follow-up Questions              │
│ 40-45 min  │ Wrap-up & Questions                          │
└─────────────────────────────────────────────────────────────┘
```

## 📝 Mock Interview Sessions

### Session 1: Design a Chat Application (Beginner)

**Problem Statement:**
"Design a real-time chat application like WhatsApp that supports one-on-one messaging."

#### Expected Interview Flow:

**Phase 1: Requirements Gathering (5 minutes)**

**Interviewer Questions to Ask:**
- "What's the scale we're designing for?"
- "What features are most important?"
- "Are there any specific technical constraints?"

**Candidate Should Ask:**
- How many users are we expecting? (Daily/Monthly active users)
- What types of messages? (Text only, or media too?)
- Do we need message history?
- Real-time delivery requirements?
- Mobile, web, or both?
- Any specific regions/countries?

**Sample Clarifications:**
- 100 million daily active users
- Text messages only for now
- Message history for 30 days
- Real-time delivery (< 1 second)
- Mobile app primary, web secondary
- Global but English language only

**Phase 2: Estimation (5 minutes)**

**Candidate Should Calculate:**

```python
# Traffic Estimation
daily_active_users = 100_000_000
messages_per_user_per_day = 50
total_messages_per_day = daily_active_users * messages_per_user_per_day
# = 5 billion messages/day

messages_per_second = total_messages_per_day / (24 * 60 * 60)
# = ~58,000 messages/second

# Storage Estimation
average_message_size = 100  # bytes
daily_storage = total_messages_per_day * average_message_size
# = 500 GB/day

retention_period = 30  # days
total_storage = daily_storage * retention_period
# = 15 TB

# Bandwidth Estimation
read_write_ratio = 2  # 2 reads per write
read_qps = messages_per_second * read_write_ratio
write_qps = messages_per_second

peak_multiplier = 3
peak_read_qps = read_qps * peak_multiplier
peak_write_qps = write_qps * peak_multiplier
```

**Phase 3: High-Level Design (10 minutes)**

**Expected Architecture:**

```
[Mobile Apps] ← → [Load Balancer] ← → [API Gateway]
                                           ↓
                                    [Chat Service]
                                           ↓
                                 [Message Queue] ← → [WebSocket Service]
                                           ↓
                                   [Message Store]
```

**Candidate Should Mention:**
- WebSocket connections for real-time messaging
- Message queues for reliability
- Database for message persistence
- Load balancing for scalability

**Phase 4: Detailed Design (15 minutes)**

**Key Components to Design:**

1. **WebSocket Service**
   ```python
   class WebSocketService:
       def __init__(self):
           self.user_connections = {}  # user_id -> websocket

       async def handle_message(self, sender_id, recipient_id, message):
           # Store message
           await self.store_message(sender_id, recipient_id, message)

           # Send to recipient if online
           if recipient_id in self.user_connections:
               await self.send_to_user(recipient_id, message)

           # Send delivery confirmation to sender
           await self.send_delivery_confirmation(sender_id, message_id)
   ```

2. **Message Store Schema**
   ```sql
   CREATE TABLE messages (
       message_id VARCHAR(36) PRIMARY KEY,
       chat_id VARCHAR(36),
       sender_id VARCHAR(36),
       recipient_id VARCHAR(36),
       content TEXT,
       timestamp TIMESTAMP,
       message_status ENUM('sent', 'delivered', 'read')
   );

   -- Index for chat history queries
   CREATE INDEX idx_chat_timestamp ON messages(chat_id, timestamp);
   ```

3. **API Endpoints**
   ```python
   # Send message
   POST /api/v1/messages
   {
       "recipient_id": "user_123",
       "content": "Hello world",
       "message_type": "text"
   }

   # Get chat history
   GET /api/v1/chats/{chat_id}/messages?limit=50&before={timestamp}
   ```

**Phase 5: Deep Dive Questions (10 minutes)**

**Typical Follow-up Questions:**

1. **"How would you handle message delivery when users are offline?"**

   **Expected Answer:**
   - Store messages in queue/database
   - When user comes online, fetch undelivered messages
   - Push notifications for offline users
   - Implement exponential backoff for retries

2. **"How would you scale this to support group chats?"**

   **Expected Answer:**
   - Modify schema to support group conversations
   - Fan-out messages to all group members
   - Consider message queues for large groups
   - Implement member management APIs

3. **"What about message ordering and consistency?"**

   **Expected Answer:**
   - Use message timestamps with vector clocks
   - Implement sequence numbers per chat
   - Handle out-of-order delivery
   - Consider event sourcing for consistency

#### Evaluation Criteria:

**Excellent (L5-L6):**
- ✅ Clear requirements gathering
- ✅ Accurate capacity estimation
- ✅ Well-structured architecture
- ✅ Detailed component design
- ✅ Handles follow-up questions well
- ✅ Considers edge cases and trade-offs
- ✅ Good communication throughout

**Good (L4):**
- ✅ Basic requirements covered
- ✅ Reasonable architecture
- ✅ Some component details
- ✅ Handles most follow-ups
- ❌ Misses some edge cases

**Needs Improvement (L3):**
- ✅ Understands problem
- ✅ Basic architecture
- ❌ Lacks detail in design
- ❌ Struggles with follow-ups
- ❌ Poor estimation

### Session 2: Design a URL Shortener (Intermediate)

**Problem Statement:**
"Design a URL shortening service like bit.ly that can handle millions of URL shortenings per day."

#### Expected Interview Flow:

**Phase 1: Requirements (5 minutes)**

**Candidate Should Ask:**
- How many URL shortenings per day?
- How many redirections per day?
- What's the ratio of reads to writes?
- How long should URLs be stored?
- Do we need analytics?
- Custom aliases allowed?
- Any specific URL length requirements?

**Sample Requirements:**
- 500M URL shortenings per day
- 50B redirections per day (100:1 read/write ratio)
- URLs stored for 5 years
- Basic analytics (click count)
- Custom aliases optional
- Short URL length: 6-7 characters

**Phase 2: Estimation (5 minutes)**

```python
# Traffic Estimation
url_shortenings_per_day = 500_000_000
redirections_per_day = 50_000_000_000

write_qps = url_shortenings_per_day / (24 * 60 * 60)  # ~5,800 QPS
read_qps = redirections_per_day / (24 * 60 * 60)     # ~580,000 QPS

# Storage Estimation
average_url_length = 100  # bytes
storage_per_url = average_url_length + 50  # metadata
daily_storage = url_shortenings_per_day * storage_per_url  # ~75 GB/day
five_year_storage = daily_storage * 365 * 5  # ~137 TB

# Short URL space
charset_size = 62  # [a-zA-Z0-9]
url_length = 7
possible_urls = charset_size ** url_length  # ~3.5 trillion URLs
```

**Phase 3: High-Level Design (10 minutes)**

```
[Client] → [Load Balancer] → [Web Servers] → [Application Servers]
                                                      ↓
                                              [Cache Layer (Redis)]
                                                      ↓
                                              [Database (MySQL/Cassandra)]
```

**Phase 4: Detailed Design (15 minutes)**

**Key Components:**

1. **URL Encoding Algorithm**
   ```python
   import hashlib
   import base62

   class URLEncoder:
       def __init__(self):
           self.counter = 0
           self.base = 62

       def encode_with_counter(self):
           """Simple counter-based encoding"""
           self.counter += 1
           return base62.encode(self.counter)

       def encode_with_hash(self, long_url):
           """Hash-based encoding with collision handling"""
           hash_value = hashlib.md5(long_url.encode()).hexdigest()
           # Take first 7 characters and convert to base62
           return self.hash_to_base62(hash_value[:7])
   ```

2. **Database Schema**
   ```sql
   CREATE TABLE urls (
       short_url VARCHAR(7) PRIMARY KEY,
       long_url VARCHAR(2048) NOT NULL,
       user_id VARCHAR(36),
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       expires_at TIMESTAMP,
       click_count BIGINT DEFAULT 0,
       INDEX idx_user_id (user_id),
       INDEX idx_created_at (created_at)
   );
   ```

3. **API Design**
   ```python
   # Shorten URL
   POST /api/v1/shorten
   {
       "long_url": "https://example.com/very/long/url",
       "custom_alias": "my-link",  # optional
       "expires_at": "2024-12-31"  # optional
   }

   Response:
   {
       "short_url": "https://bit.ly/abc123",
       "long_url": "https://example.com/very/long/url"
   }

   # Redirect
   GET /{short_code}
   Response: 302 Redirect to long_url
   ```

**Phase 5: Deep Dive (10 minutes)**

**Follow-up Questions:**

1. **"How would you handle hot URLs that get millions of clicks?"**
   - Multi-level caching (browser, CDN, application)
   - Cache popular URLs in memory
   - Use Redis cluster for distributed caching
   - Async analytics updates

2. **"How do you ensure uniqueness of short URLs?"**
   - Database constraints
   - Distributed ID generation
   - Counter-based approach with multiple servers
   - Handle collisions gracefully

3. **"How would you implement analytics?"**
   - Real-time: Update counters in cache
   - Batch processing: Periodic updates to database
   - Detailed analytics: Log clicks to data pipeline
   - Separate analytics database

### Session 3: Design Netflix (Advanced)

**Problem Statement:**
"Design a video streaming service like Netflix that can serve content to millions of users globally."

#### Expected Interview Flow:

**Phase 1: Requirements (5 minutes)**

**Candidate Should Ask:**
- How many users? (registered vs active)
- How many videos in catalog?
- What video qualities/formats?
- Global or specific regions?
- Live streaming or VOD only?
- Mobile, TV, web support?
- Recommendation system needed?

**Sample Requirements:**
- 200M registered users, 100M daily active
- 10K videos in catalog
- Multiple qualities (480p to 4K)
- Global service
- Video-on-demand only
- All platforms (mobile, web, smart TV)
- Basic recommendation system

**Phase 2: Estimation (5 minutes)**

```python
# User Metrics
registered_users = 200_000_000
daily_active_users = 100_000_000
concurrent_users_peak = daily_active_users * 0.1  # 10M concurrent

# Content Metrics
total_videos = 10_000
average_video_length = 90  # minutes
video_qualities = 4  # 480p, 720p, 1080p, 4K

# Storage Estimation (per video)
storage_per_minute = {
    '480p': 5,    # MB
    '720p': 10,   # MB
    '1080p': 20,  # MB
    '4K': 50      # MB
}

total_storage_per_video = sum(storage_per_minute.values()) * average_video_length
total_catalog_storage = total_videos * total_storage_per_video  # ~77 TB

# Bandwidth Estimation
average_viewing_session = 60  # minutes
sessions_per_day = daily_active_users * 1.5
total_viewing_minutes = sessions_per_day * average_viewing_session

peak_bandwidth = (total_viewing_minutes / (24 * 60)) * 10  # MB/min for 1080p
# Peak bandwidth: ~625 GB/s
```

**Phase 3: High-Level Architecture (10 minutes)**

```
[CDN (Geographically Distributed)]
         ↑
[Users] → [Load Balancer] → [API Gateway] → [Microservices]
                                                  ↓
                                           [User Service]
                                           [Video Service]
                                           [Recommendation Service]
                                           [Analytics Service]
                                                  ↓
                                           [Databases (Master/Slave)]
                                                  ↓
                                           [Video Storage (Object Storage)]
```

**Phase 4: Detailed Design (15 minutes)**

**Key Components:**

1. **Video Processing Pipeline**
   ```python
   class VideoProcessingPipeline:
       async def process_video(self, video_file):
           # 1. Upload raw video
           raw_video_url = await self.upload_raw_video(video_file)

           # 2. Transcode to multiple formats
           transcoding_jobs = []
           for quality in ['480p', '720p', '1080p', '4K']:
               job = await self.start_transcoding(raw_video_url, quality)
               transcoding_jobs.append(job)

           # 3. Generate thumbnails
           thumbnails = await self.generate_thumbnails(raw_video_url)

           # 4. Upload to CDN
           for job in transcoding_jobs:
               encoded_video = await self.wait_for_completion(job)
               await self.upload_to_cdn(encoded_video)

           # 5. Update database
           await self.update_video_metadata(video_id, transcoding_jobs)
   ```

2. **CDN Strategy**
   ```python
   class CDNManager:
       def __init__(self):
           self.cdn_regions = {
               'us-east': 'https://us-east.cdn.netflix.com',
               'us-west': 'https://us-west.cdn.netflix.com',
               'eu-west': 'https://eu-west.cdn.netflix.com',
               'asia-pac': 'https://asia.cdn.netflix.com'
           }

       def get_video_url(self, video_id, user_location, quality):
           # Determine best CDN region
           cdn_region = self.get_nearest_region(user_location)

           # Generate signed URL with expiration
           base_url = self.cdn_regions[cdn_region]
           return f"{base_url}/videos/{video_id}/{quality}.m3u8?token={self.generate_token()}"
   ```

3. **Database Design**
   ```sql
   -- Users table
   CREATE TABLE users (
       user_id VARCHAR(36) PRIMARY KEY,
       email VARCHAR(255) UNIQUE,
       subscription_type ENUM('basic', 'standard', 'premium'),
       created_at TIMESTAMP
   );

   -- Videos table
   CREATE TABLE videos (
       video_id VARCHAR(36) PRIMARY KEY,
       title VARCHAR(255),
       description TEXT,
       duration_minutes INT,
       release_date DATE,
       genre VARCHAR(100),
       rating VARCHAR(10)
   );

   -- Video files table
   CREATE TABLE video_files (
       file_id VARCHAR(36) PRIMARY KEY,
       video_id VARCHAR(36),
       quality ENUM('480p', '720p', '1080p', '4K'),
       file_url VARCHAR(500),
       file_size_mb INT,
       FOREIGN KEY (video_id) REFERENCES videos(video_id)
   );

   -- Watch history
   CREATE TABLE watch_history (
       user_id VARCHAR(36),
       video_id VARCHAR(36),
       watched_at TIMESTAMP,
       watch_duration_minutes INT,
       PRIMARY KEY (user_id, video_id, watched_at)
   );
   ```

**Phase 5: Deep Dive (10 minutes)**

**Advanced Questions:**

1. **"How do you handle video streaming at scale?"**
   - Adaptive bitrate streaming (HLS/DASH)
   - Multiple CDN providers for redundancy
   - Edge servers close to users
   - Video chunk caching strategy
   - Preloading popular content

2. **"How would you implement the recommendation system?"**
   ```python
   class RecommendationEngine:
       def get_recommendations(self, user_id):
           # Collaborative filtering
           similar_users = self.find_similar_users(user_id)

           # Content-based filtering
           user_preferences = self.analyze_viewing_history(user_id)

           # Trending content
           trending_videos = self.get_trending_content()

           # Combine algorithms
           recommendations = self.hybrid_approach(
               similar_users, user_preferences, trending_videos
           )

           return recommendations[:20]  # Top 20
   ```

3. **"How do you ensure video quality and minimize buffering?"**
   - Adaptive bitrate streaming
   - Multiple encoding profiles
   - Edge server optimization
   - Bandwidth detection and quality adjustment
   - Preloading and predictive caching

## 🎯 Practice Schedule

### Week 1: Foundation
- **Day 1-2:** Chat Application (Basic)
- **Day 3-4:** URL Shortener
- **Day 5-6:** Design Twitter Feed
- **Day 7:** Review and self-assessment

### Week 2: Intermediate
- **Day 1-2:** Design Instagram
- **Day 3-4:** Design Uber
- **Day 5-6:** Design Dropbox
- **Day 7:** Mock interview with peer

### Week 3: Advanced
- **Day 1-2:** Design Netflix
- **Day 3-4:** Design YouTube
- **Day 5-6:** Design WhatsApp
- **Day 7:** Complete mock interview

## 📋 Interview Evaluation Rubric

### Communication (25%)
- **Excellent:** Clear, structured communication. Asks clarifying questions. Explains thought process well.
- **Good:** Generally clear. Some good questions. Mostly explains reasoning.
- **Needs Work:** Unclear communication. Few clarifying questions. Hard to follow.

### Problem Solving (25%)
- **Excellent:** Systematic approach. Handles requirements well. Good trade-off analysis.
- **Good:** Reasonable approach. Covers most requirements. Some trade-offs discussed.
- **Needs Work:** Disorganized approach. Misses requirements. No trade-off analysis.

### Technical Design (25%)
- **Excellent:** Well-architected system. Appropriate technology choices. Scalable design.
- **Good:** Decent architecture. Mostly appropriate choices. Some scalability considerations.
- **Needs Work:** Poor architecture. Wrong technology choices. No scalability planning.

### Depth of Knowledge (25%)
- **Excellent:** Deep understanding. Handles follow-ups well. Knows implementation details.
- **Good:** Good understanding. Handles most follow-ups. Some implementation knowledge.
- **Needs Work:** Surface-level knowledge. Struggles with follow-ups. Little implementation detail.

## 🔄 Common Mistakes to Avoid

### 1. Jumping to Solution Too Quickly
❌ **Wrong:** Start designing immediately
✅ **Right:** Ask clarifying questions first

### 2. Not Estimating Scale
❌ **Wrong:** Design without understanding requirements
✅ **Right:** Calculate users, storage, bandwidth needs

### 3. Over-Engineering
❌ **Wrong:** Complex distributed system for small scale
✅ **Right:** Start simple, then scale

### 4. Ignoring Trade-offs
❌ **Wrong:** Present only one solution
✅ **Right:** Discuss alternatives and trade-offs

### 5. Poor Communication
❌ **Wrong:** Silent design or unclear explanations
✅ **Right:** Think out loud and explain reasoning

## 🎓 Tips for Success

### Before the Interview
1. **Practice drawing**: Use whiteboard or online tools
2. **Time yourself**: Stick to the 45-minute format
3. **Record sessions**: Review your performance
4. **Study company products**: Understand their scale and challenges

### During the Interview
1. **Start with requirements**: Don't assume anything
2. **Think out loud**: Explain your reasoning
3. **Start simple**: Build complexity gradually
4. **Ask for feedback**: "Does this approach make sense?"
5. **Handle pushback gracefully**: Be open to suggestions

### After the Interview
1. **Self-evaluate**: Use the rubric above
2. **Identify weak areas**: Focus practice on these
3. **Get feedback**: Ask interviewer or peers
4. **Iterate and improve**: Each session should be better

## 🔗 Additional Resources

- [System Design Interview Questions Database](../../common-questions/)
- [Estimation Techniques Guide](../estimation-techniques/)
- [Interview Frameworks](../../interview-frameworks/)
- [Timed Exercises](../timed-exercises/)

Remember: The goal is not to get the "perfect" answer, but to demonstrate your thought process, technical knowledge, and ability to work through complex problems systematically.