# URL Shortener Service (AWS Implementation) 🔗

Build a production-grade URL shortener like bit.ly using serverless AWS architecture.

## 🎯 Project Overview

Create a highly scalable, cost-effective URL shortener service that can handle millions of URLs and redirects using AWS serverless technologies.

**Live Example**: Similar to bit.ly, tinyurl.com, or goo.gl
**Architecture**: Serverless-first with global content delivery
**Expected Scale**: 1M+ URLs, 100K+ daily active users, 10M+ redirects/day

## 📚 Learning Objectives

After completing this project, you'll understand:
- Serverless architecture patterns and benefits
- NoSQL database design for high-scale applications
- Global content delivery with CloudFront
- API design and rate limiting strategies
- Cost-effective scaling with AWS Lambda

## 🏗️ System Architecture

### High-Level Architecture
```
Client → CloudFront → API Gateway → Lambda Functions → DynamoDB
   ↓                                      ↓
Custom Domain                         Analytics
   ↓                                      ↓
Route 53                             CloudWatch
```

### Detailed Architecture
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Web Client    │────│  CloudFront  │────│  Route 53 DNS   │
│  (React SPA)    │    │     CDN      │    │   Management    │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ POST /urls  │  │ GET /{id}   │  │  Analytics APIs     │  │
│  │ (Shorten)   │  │ (Redirect)  │  │  User Management    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Lambda Functions                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Shorten   │  │  Redirect   │  │     Analytics       │  │
│  │  Function   │  │  Function   │  │     Functions       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DynamoDB                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    URLs     │  │   Analytics │  │   User Sessions     │  │
│  │   Table     │  │    Table    │  │      Table          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technical Components

### Frontend (React SPA)
- **Hosting**: S3 + CloudFront
- **Features**: URL input, QR code generation, analytics dashboard
- **Tech Stack**: React, TypeScript, Tailwind CSS
- **Build**: Automated with CodeBuild/CodePipeline

### Backend (Serverless)
- **API Gateway**: RESTful API with custom domain
- **Lambda Functions**: Node.js/Python for business logic
- **DynamoDB**: NoSQL database for URL storage
- **CloudWatch**: Monitoring and logging

### Infrastructure
- **Route 53**: DNS management and health checks
- **ACM**: SSL certificate management
- **CloudFormation**: Infrastructure as Code
- **WAF**: Web application firewall protection

## 📋 Project Requirements

### Functional Requirements
- [x] **URL Shortening**: Convert long URLs to short codes
- [x] **URL Redirection**: Redirect short URLs to original URLs
- [x] **Custom Aliases**: Allow users to choose custom short codes
- [x] **Expiration**: Set expiration dates for URLs
- [x] **Analytics**: Track clicks, referrers, geographic data
- [x] **User Accounts**: Optional user registration for URL management
- [x] **API Access**: RESTful API for programmatic access

### Non-Functional Requirements
- [x] **Performance**: < 100ms response time for redirects
- [x] **Scalability**: Handle 10M+ redirects per day
- [x] **Availability**: 99.9% uptime
- [x] **Security**: Input validation, rate limiting, spam protection
- [x] **Cost**: < $50/month for expected load
- [x] **Global**: Low latency worldwide through CDN

## 🗂️ Project Structure

```
url-shortener-aws/
├── README.md
├── architecture/
│   ├── system-design.md
│   ├── database-schema.md
│   └── api-specification.md
├── infrastructure/
│   ├── cloudformation/
│   │   ├── main.yaml
│   │   ├── api-gateway.yaml
│   │   ├── lambda-functions.yaml
│   │   └── dynamodb.yaml
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── scripts/
│       ├── deploy.sh
│       └── cleanup.sh
├── backend/
│   ├── functions/
│   │   ├── shorten/
│   │   ├── redirect/
│   │   └── analytics/
│   ├── shared/
│   │   ├── database.js
│   │   ├── validation.js
│   │   └── utils.js
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── public/
│   └── package.json
├── monitoring/
│   ├── dashboards/
│   ├── alarms/
│   └── logs/
└── docs/
    ├── deployment.md
    ├── api-documentation.md
    └── user-guide.md
```

## 🔢 Database Design

### URLs Table (DynamoDB)
```json
{
  "TableName": "URLs",
  "KeySchema": [
    {"AttributeName": "shortCode", "KeyType": "HASH"}
  ],
  "AttributeDefinitions": [
    {"AttributeName": "shortCode", "AttributeType": "S"},
    {"AttributeName": "createdBy", "AttributeType": "S"},
    {"AttributeName": "createdAt", "AttributeType": "N"}
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "UserIndex",
      "KeySchema": [
        {"AttributeName": "createdBy", "KeyType": "HASH"},
        {"AttributeName": "createdAt", "KeyType": "RANGE"}
      ]
    }
  ]
}
```

### Analytics Table (DynamoDB)
```json
{
  "TableName": "Analytics",
  "KeySchema": [
    {"AttributeName": "shortCode", "KeyType": "HASH"},
    {"AttributeName": "timestamp", "KeyType": "RANGE"}
  ],
  "AttributeDefinitions": [
    {"AttributeName": "shortCode", "AttributeType": "S"},
    {"AttributeName": "timestamp", "AttributeType": "N"}
  ],
  "TimeToLiveSpecification": {
    "AttributeName": "ttl",
    "Enabled": true
  }
}
```

## 🔌 API Specification

### POST /urls (Shorten URL)
```http
POST /urls
Content-Type: application/json
Authorization: Bearer <token> (optional)

{
  "url": "https://example.com/very/long/url",
  "customCode": "my-short-link", // optional
  "expiresAt": "2024-12-31T23:59:59Z" // optional
}

Response:
{
  "shortCode": "abc123",
  "shortUrl": "https://short.ly/abc123",
  "originalUrl": "https://example.com/very/long/url",
  "createdAt": "2024-01-15T10:30:00Z",
  "expiresAt": "2024-12-31T23:59:59Z"
}
```

### GET /{shortCode} (Redirect)
```http
GET /abc123

Response:
HTTP/1.1 301 Moved Permanently
Location: https://example.com/very/long/url
Cache-Control: public, max-age=3600
```

### GET /analytics/{shortCode}
```http
GET /analytics/abc123
Authorization: Bearer <token>

Response:
{
  "shortCode": "abc123",
  "totalClicks": 1542,
  "dailyStats": [
    {"date": "2024-01-15", "clicks": 45},
    {"date": "2024-01-14", "clicks": 38}
  ],
  "topReferrers": [
    {"referrer": "twitter.com", "clicks": 234},
    {"referrer": "facebook.com", "clicks": 187}
  ],
  "topCountries": [
    {"country": "US", "clicks": 456},
    {"country": "UK", "clicks": 234}
  ]
}
```

## 🚀 Implementation Phases

### Phase 1: MVP (Week 1)
**Goal**: Basic URL shortening and redirection

**Tasks**:
- [ ] Set up AWS account and basic infrastructure
- [ ] Create DynamoDB table for URLs
- [ ] Implement shorten Lambda function
- [ ] Implement redirect Lambda function
- [ ] Set up API Gateway with basic endpoints
- [ ] Deploy simple frontend for testing

**Deliverables**:
- Working URL shortener with basic functionality
- Infrastructure code (CloudFormation/Terraform)
- Basic tests and documentation

### Phase 2: Production Features (Week 2)
**Goal**: Add production-ready features

**Tasks**:
- [ ] Add user authentication with Cognito
- [ ] Implement custom short codes
- [ ] Add URL expiration functionality
- [ ] Set up CloudFront for global distribution
- [ ] Implement rate limiting and input validation
- [ ] Add comprehensive error handling

**Deliverables**:
- Production-ready API with security features
- Global CDN distribution
- User management system

### Phase 3: Analytics & Monitoring (Week 3)
**Goal**: Analytics dashboard and monitoring

**Tasks**:
- [ ] Implement click tracking with analytics table
- [ ] Create analytics Lambda functions
- [ ] Build analytics dashboard frontend
- [ ] Set up CloudWatch monitoring and alarms
- [ ] Implement performance optimization
- [ ] Add comprehensive logging

**Deliverables**:
- Analytics dashboard with real-time data
- Production monitoring setup
- Performance optimization report

### Phase 4: Advanced Features (Week 4)
**Goal**: Advanced features and optimization

**Tasks**:
- [ ] Implement QR code generation
- [ ] Add bulk URL operations
- [ ] Set up API rate limiting with API Gateway
- [ ] Implement caching strategies
- [ ] Add advanced security features (WAF)
- [ ] Create comprehensive documentation

**Deliverables**:
- Feature-complete URL shortener
- Security hardening implementation
- Complete project documentation

## 💰 Cost Analysis

### Expected Monthly Costs (10M redirects/month)

#### Serverless Components
- **Lambda**: ~$15/month (10M invocations)
- **API Gateway**: ~$35/month (10M requests)
- **DynamoDB**: ~$25/month (5GB storage + reads/writes)
- **CloudFront**: ~$10/month (data transfer)

#### Additional Services
- **Route 53**: ~$1/month (hosted zone + queries)
- **S3**: ~$5/month (frontend hosting + logs)
- **CloudWatch**: ~$5/month (logs + metrics)

**Total Estimated Cost**: ~$96/month for 10M redirects

### Cost Optimization Strategies
- Use DynamoDB On-Demand for variable traffic
- Implement caching to reduce Lambda invocations
- Optimize Lambda function memory allocation
- Use CloudFront caching to reduce API calls
- Set up automated resource cleanup

## 🔒 Security Implementation

### Input Validation
- URL format validation and sanitization
- Custom code validation (alphanumeric, length limits)
- Rate limiting per IP and user
- Malicious URL detection

### Access Control
- API key authentication for public API
- JWT tokens for user-specific operations
- IAM roles with least privilege principle
- CORS configuration for frontend

### Protection Measures
- AWS WAF for DDoS protection
- CloudTrail for audit logging
- VPC endpoints for internal traffic
- Encryption at rest and in transit

## 📊 Performance Optimization

### Lambda Optimization
```javascript
// Optimized Lambda function
const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();

// Connection reuse
const connectionParams = {
  region: process.env.AWS_REGION,
  maxRetries: 3,
  retryDelayOptions: {
    customBackoff: function(retryCount) {
      return Math.pow(2, retryCount) * 100;
    }
  }
};

exports.handler = async (event) => {
  try {
    // Warm-up optimization
    if (event.source === 'serverless-plugin-warmup') {
      return 'Lambda is warm!';
    }

    const shortCode = event.pathParameters.shortCode;

    // Get URL from DynamoDB
    const result = await dynamodb.get({
      TableName: process.env.URLS_TABLE,
      Key: { shortCode }
    }).promise();

    if (!result.Item) {
      return {
        statusCode: 404,
        body: JSON.stringify({ error: 'URL not found' })
      };
    }

    // Check expiration
    if (result.Item.expiresAt && Date.now() > result.Item.expiresAt) {
      return {
        statusCode: 410,
        body: JSON.stringify({ error: 'URL has expired' })
      };
    }

    // Track analytics asynchronously
    trackClick(shortCode, event);

    return {
      statusCode: 301,
      headers: {
        'Location': result.Item.originalUrl,
        'Cache-Control': 'public, max-age=3600'
      }
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
};
```

### DynamoDB Optimization
- Use single-table design patterns
- Implement efficient secondary indexes
- Optimize read/write capacity modes
- Use DynamoDB Accelerator (DAX) for caching

### CDN Configuration
```yaml
# CloudFront distribution for optimal caching
CachePolicy:
  DefaultCacheBehavior:
    CachePolicyId: !Ref CachingOptimized
    OriginRequestPolicyId: !Ref CORS-S3Origin
    ResponseHeadersPolicyId: !Ref SimpleCORS
    ViewerProtocolPolicy: redirect-to-https
    AllowedMethods:
      - GET
      - HEAD
      - OPTIONS
      - PUT
      - PATCH
      - POST
      - DELETE
    CachedMethods:
      - GET
      - HEAD
    Compress: true
```

## 📈 Monitoring and Alerting

### Key Metrics to Track
- **Response Time**: API Gateway and Lambda latency
- **Error Rate**: 4xx and 5xx error percentages
- **Throughput**: Requests per second
- **DynamoDB Performance**: Read/write capacity utilization
- **Cost**: Daily spending and trends

### CloudWatch Alarms
```yaml
HighErrorRateAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: URLShortener-HighErrorRate
    AlarmDescription: High error rate detected
    MetricName: 4XXError
    Namespace: AWS/ApiGateway
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 2
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    AlarmActions:
      - !Ref SNSAlert
```

### Custom Dashboards
- Real-time traffic monitoring
- Geographic usage patterns
- Popular URL categories
- Cost optimization opportunities

## 🎯 Success Criteria

### Technical Achievements
- [ ] **Performance**: < 100ms average response time
- [ ] **Scalability**: Handle 1000+ requests/second
- [ ] **Reliability**: 99.9% uptime over 30 days
- [ ] **Security**: No security vulnerabilities in audit
- [ ] **Cost**: Under $50/month for expected load

### Business Metrics
- [ ] **User Engagement**: 80%+ click-through rate
- [ ] **Analytics Accuracy**: Real-time data with < 1% variance
- [ ] **Global Performance**: < 200ms response time worldwide
- [ ] **API Adoption**: Support for 3rd party integrations

## 🚀 Getting Started

### Quick Start (15 minutes)
1. **Clone Repository**: Get the starter template
2. **Configure AWS**: Set up credentials and region
3. **Deploy Infrastructure**: Run CloudFormation template
4. **Test Basic Functionality**: Create and access short URLs
5. **Deploy Frontend**: Upload to S3 and configure CloudFront

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd url-shortener-aws

# Install dependencies
npm install

# Configure AWS CLI
aws configure

# Deploy infrastructure
./infrastructure/scripts/deploy.sh

# Deploy functions
cd backend && npm run deploy

# Build and deploy frontend
cd frontend && npm run build && npm run deploy
```

## 📞 Next Steps

After completing the URL shortener:
1. **Scale to [Chat Application](../chat-application-aws/)** - Add real-time features
2. **Explore [Microservices](../../04-microservices-implementation/)** - Break into smaller services
3. **Add [Advanced Monitoring](../../09-monitoring-observability/)** - Comprehensive observability

---

**Ready to build?** Start with the [MVP implementation](implementation/mvp/) to create your first serverless URL shortener!

*This project demonstrates serverless architecture patterns that scale automatically and cost-effectively with usage.*