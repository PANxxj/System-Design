# 05. System Design Interview Preparation

## 🎯 Learning Objectives

Master the system design interview process:
- Follow a structured approach to tackle any system design question
- Communicate technical decisions clearly and confidently
- Handle follow-up questions and deep dives effectively
- Demonstrate trade-off analysis and scaling strategies

## 📋 Prerequisites
- Completed fundamentals and either LLD or HLD sections
- Understanding of distributed systems concepts
- Basic knowledge of common technologies
- **Estimated Time**: 3-4 weeks

## 🗂️ Section Contents

### Interview Framework & Strategy
- **[Step-by-Step Approach](interview-frameworks/step-by-step-approach.md)** 🟢
  - Structured methodology for any system design question
  - Time management during interviews
  - Common pitfalls to avoid

- **[Clarifying Questions](interview-frameworks/clarifying-questions.md)** 🟢
  - Essential questions to ask before designing
  - Understanding functional vs non-functional requirements
  - Constraint identification techniques

- **[Trade-offs Discussion](interview-frameworks/trade-offs-discussion.md)** 🟡
  - How to analyze and present trade-offs
  - CAP theorem applications
  - Performance vs consistency decisions

### Estimation Techniques
- **[Capacity Planning](estimation-techniques/capacity-planning.md)** 🟢
  - Back-of-the-envelope calculations
  - Traffic and storage estimation
  - Bandwidth and memory requirements

- **[Back-of-Envelope Math](estimation-techniques/back-of-envelope.md)** 🟢
  - Essential numbers every engineer should know
  - Quick calculation techniques
  - Approximation strategies

### Common Interview Questions
- **[Design Twitter](common-questions/design-twitter.md)** 🟡
- **[Design Instagram](common-questions/design-instagram.md)** 🟡
- **[Design Uber](common-questions/design-uber.md)** 🔴
- **[Design WhatsApp](common-questions/design-whatsapp.md)** 🟡
- **[Design YouTube](common-questions/design-youtube.md)** 🔴
- **[Design URL Shortener](common-questions/design-url-shortener.md)** 🟢

### Practice Sessions
- **[Mock Interviews](practice-sessions/mock-interviews/)** 🟡
- **[Timed Exercises](practice-sessions/timed-exercises/)** 🟡

## 📖 Study Guide

### Week 1: Framework Mastery (🟢 Essential)
**Day 1-2**: Step-by-Step Approach
- Learn the structured methodology
- Practice on simple examples
- **Exercise**: Apply framework to design a basic cache

**Day 3-4**: Clarifying Questions
- Study question templates
- Practice requirement gathering
- **Exercise**: Create question lists for 5 different systems

**Day 5-7**: Estimation Techniques
- Master back-of-envelope calculations
- Practice capacity planning
- **Exercise**: Estimate requirements for popular apps

### Week 2: Common Questions (🟡 Intermediate)
**Day 1-2**: Simple Systems
- URL Shortener design
- Basic chat application
- **Exercise**: Complete designs within 45-minute time limit

**Day 3-4**: Medium Complexity
- Twitter-like social media
- Instagram photo sharing
- **Exercise**: Focus on scaling and trade-offs

**Day 5-7**: Advanced Systems
- Uber ride-sharing
- YouTube video streaming
- **Exercise**: Handle complex requirements and deep dives

### Week 3: Advanced Preparation (🔴 Advanced)
**Day 1-3**: Deep Technical Discussions
- Study advanced distributed systems concepts
- Practice explaining complex trade-offs
- **Exercise**: Design systems with multiple conflicting requirements

**Day 4-7**: Mock Interview Practice
- Conduct full-length mock interviews
- Practice with peers or mentors
- **Exercise**: Record and review your explanations

### Week 4: Final Preparation
**Day 1-3**: Review and Refinement
- Review all common questions
- Practice your weakest areas
- **Exercise**: Speed rounds - design systems in 30 minutes

**Day 4-7**: Company-Specific Preparation
- Research target companies' systems
- Study their engineering blogs
- **Exercise**: Design systems similar to target company's products

## 🚀 The 8-Step Interview Framework

### 1. Clarify Requirements (5-7 minutes)
**Functional Requirements:**
- What are the core features?
- What actions can users perform?
- What are the inputs and outputs?

**Non-Functional Requirements:**
- How many users? (scale)
- What's the expected read/write ratio?
- What are the latency requirements?
- What's the availability requirement?

### 2. Estimate Scale (3-5 minutes)
```
Example for Twitter:
- 300M monthly active users
- 50% daily active → 150M DAU
- Average 2 tweets per user per day
- Total: 300M tweets/day = 3,500 tweets/second
- Read/Write ratio: 100:1 → 350K reads/second
```

### 3. Define System Interface (5 minutes)
```python
# Example API design
def post_tweet(user_id, tweet_content, media_urls=None):
    """Create a new tweet"""
    pass

def get_timeline(user_id, count=20, max_tweet_id=None):
    """Get user's timeline"""
    pass

def follow_user(follower_id, followee_id):
    """Follow another user"""
    pass
```

### 4. High-Level Design (10-15 minutes)
- Draw main components
- Show data flow
- Identify major services

```
[Mobile App] → [Load Balancer] → [API Gateway] → [Tweet Service]
                                                ↓
[Web App] ────────────────────────────────────→ [User Service]
                                                ↓
                                              [Database]
```

### 5. Database Design (8-10 minutes)
```sql
-- Example schemas
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    email VARCHAR(100),
    created_at TIMESTAMP
);

CREATE TABLE tweets (
    tweet_id BIGINT PRIMARY KEY,
    user_id BIGINT,
    content TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 6. Detailed Component Design (10-15 minutes)
- Break down major components
- Discuss algorithms and data structures
- Address performance bottlenecks

### 7. Scale the Design (10-15 minutes)
- Identify bottlenecks
- Propose scaling solutions
- Discuss trade-offs

### 8. Monitor and Maintain (3-5 minutes)
- Logging and metrics
- Alerting strategies
- Deployment considerations

## 📊 Evaluation Criteria

### What Interviewers Look For

**Problem-Solving Approach (30%)**
- Structured thinking
- Appropriate questions asked
- Requirements clarification

**Technical Knowledge (25%)**
- Understanding of distributed systems
- Knowledge of technologies and trade-offs
- Scalability concepts

**Communication (25%)**
- Clear explanations
- Diagram quality
- Ability to discuss trade-offs

**Depth and Breadth (20%)**
- Deep dive capability
- Handling follow-up questions
- End-to-end thinking

### Common Mistakes to Avoid

❌ **Jumping to solutions without understanding requirements**
❌ **Not asking clarifying questions**
❌ **Over-engineering the initial design**
❌ **Ignoring non-functional requirements**
❌ **Poor time management**
❌ **Not explaining trade-offs**
❌ **Focusing only on happy path scenarios**
❌ **Not considering failure scenarios**

## 🎯 Sample Interview Question Walkthrough

### Question: "Design a Chat Application like WhatsApp"

**1. Requirements Clarification (5 min)**
```
Interviewer: Design a chat application
You: Let me clarify the requirements:

Functional:
- Is this 1-on-1 messaging or group chats too?
- Do we need features like file sharing, voice messages?
- Should messages be persistent?
- Do we need online status indicators?

Non-Functional:
- How many users are we targeting?
- What's the expected message volume?
- Any specific latency requirements?
- What about availability requirements?

Interviewer: Let's focus on 1-on-1 messaging with 500M users,
real-time delivery, and 99.9% availability.
```

**2. Scale Estimation (4 min)**
```
Users: 500M total, assume 10% daily active = 50M DAU
Messages: Assume 20 messages per user per day
Total daily messages: 50M × 20 = 1B messages/day
Messages per second: 1B / (24 × 3600) = ~12K/sec
Peak traffic: 2x average = 24K/sec

Storage: 1B messages/day × 100 bytes/message = 100GB/day
5 years: 100GB × 365 × 5 = ~180TB
```

**3. API Design (3 min)**
```python
send_message(sender_id, receiver_id, message_content, message_type)
get_messages(user_id, conversation_id, limit, offset)
get_conversations(user_id)
mark_as_read(user_id, message_id)
```

**4. High-Level Design (12 min)**
```
[Mobile Client] → [Load Balancer] → [Chat Service] → [Message Queue] → [Database]
                                          ↓
[Web Client] ──────────────────────→ [WebSocket Manager] → [Redis Cache]
```

Continue with database design, detailed components, scaling, etc.

## 🛠️ Practice Exercises

### Exercise 1: Time Management
Practice the 45-minute format:
- Set a timer for each phase
- Record yourself explaining
- Review and improve pacing

### Exercise 2: Question Bank
Create your own clarifying questions for:
- Social media platforms
- E-commerce systems
- Streaming services
- Transportation apps
- Communication tools

### Exercise 3: Technology Justification
For each technology choice, prepare a 2-minute explanation:
- Why SQL vs NoSQL?
- When to use Redis vs Memcached?
- REST vs GraphQL vs gRPC?
- Microservices vs Monolith?

## 📚 Company-Specific Preparation

### FAANG Companies
- **Google**: Focus on scale and efficiency
- **Amazon**: Emphasize reliability and cost optimization
- **Facebook/Meta**: Social features and real-time systems
- **Apple**: User experience and privacy
- **Netflix**: Content delivery and personalization

### Startup vs Big Tech
- **Startups**: Rapid development, MVP approach
- **Big Tech**: Scale, reliability, performance optimization

## ✅ Pre-Interview Checklist

**One Week Before:**
- [ ] Review all fundamental concepts
- [ ] Practice 2-3 mock interviews
- [ ] Prepare questions about the company's systems
- [ ] Study the company's engineering blog

**One Day Before:**
- [ ] Review your notes on common patterns
- [ ] Practice drawing clean diagrams
- [ ] Prepare examples from your experience
- [ ] Get good rest - clarity of thought is crucial

**Day of Interview:**
- [ ] Test your setup (whiteboard, markers, or digital tools)
- [ ] Review back-of-envelope calculation shortcuts
- [ ] Prepare thoughtful questions about the role
- [ ] Stay calm and think out loud

## 🚀 Next Steps

After interview preparation:
1. **Schedule mock interviews** with peers or mentors
2. **Practice regularly** - at least 2 sessions per week
3. **Stay updated** with latest technology trends
4. **Join communities** for ongoing practice and feedback

---

**Remember**: System design interviews test your ability to think through complex problems systematically. Focus on clear communication and structured thinking over memorizing perfect solutions!