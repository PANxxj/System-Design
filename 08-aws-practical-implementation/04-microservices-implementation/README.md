# Microservices Implementation on AWS 🔄

Master the art of building, deploying, and managing microservices architectures using AWS container and orchestration services.

## 🎯 Learning Objectives

After completing this section, you'll be able to:
- Design and implement microservices architectures
- Use container orchestration with ECS and EKS
- Implement service discovery and communication patterns
- Build resilient, fault-tolerant distributed systems
- Apply microservices best practices and patterns

## 📚 Prerequisites

**Required Completion**:
- [x] [Scalable Architectures](../03-scalable-architectures/) - Advanced scaling patterns
- [x] [Basic Web Application](../02-basic-web-application/) - Containerization basics
- [x] [System Design HLD](../../03-high-level-design/) - Distributed systems concepts

**Technical Skills**:
- Docker containerization experience
- API design and development
- Understanding of distributed systems
- Basic Kubernetes knowledge (helpful)

## ⏱️ Time Commitment

**Total Duration**: 5-6 weeks (30-35 hours)
- **Week 1**: Containerization and ECS basics (6-7 hours)
- **Week 2**: EKS and Kubernetes fundamentals (7-8 hours)
- **Week 3**: Service mesh and communication (6-7 hours)
- **Week 4**: API Gateway and service discovery (5-6 hours)
- **Week 5**: Monitoring and observability (3-4 hours)
- **Week 6**: Advanced patterns and optimization (3-4 hours)

## 🏗️ Microservices Architecture Evolution

### Monolithic to Microservices Journey
```
Phase 1: Monolith
┌─────────────────────────────────┐
│        Single Application       │
│  ┌─────┬─────┬─────┬─────────┐  │
│  │ Web │ API │ BL  │ Database│  │
│  └─────┴─────┴─────┴─────────┘  │
└─────────────────────────────────┘

Phase 2: Modular Monolith
┌─────────────────────────────────┐
│    ┌─────────┬─────────────┐    │
│    │   Web   │    API      │    │
│    └─────────┴─────────────┘    │
│    ┌─────────┬─────────────┐    │
│    │  Users  │   Orders    │    │
│    └─────────┴─────────────┘    │
│    ┌─────────────────────────┐  │
│    │      Database           │  │
│    └─────────────────────────┘  │
└─────────────────────────────────┘

Phase 3: Microservices
┌─────────┐  ┌─────────┐  ┌─────────┐
│  User   │  │ Order   │  │Product  │
│Service  │  │Service  │  │Service  │
│   DB    │  │   DB    │  │   DB    │
└─────────┘  └─────────┘  └─────────┘
      ↕            ↕            ↕
┌─────────────────────────────────────┐
│           API Gateway               │
└─────────────────────────────────────┘
```

### Target Architecture
```
Internet → CloudFront → ALB → API Gateway
                               ↓
              ┌─────────────────┼─────────────────┐
              ↓                 ↓                 ↓
        ┌──────────┐     ┌──────────┐     ┌──────────┐
        │   EKS    │     │   EKS    │     │   EKS    │
        │ Cluster  │     │ Cluster  │     │ Cluster  │
        │  (User)  │     │ (Order)  │     │(Product) │
        └──────────┘     └──────────┘     └──────────┘
              ↓                 ↓                 ↓
        ┌──────────┐     ┌──────────┐     ┌──────────┐
        │   RDS    │     │DynamoDB  │     │   RDS    │
        │ (Users)  │     │ (Orders) │     │(Products)│
        └──────────┘     └──────────┘     └──────────┘
```

## 🗂️ Section Contents

### Week 1: Containerization & ECS
- [Docker Best Practices](containerization/docker-best-practices.md)
- [ECS Task Definitions](containerization/ecs-tasks.md)
- [ECS Services and Load Balancing](containerization/ecs-services.md)
- [Container Registry with ECR](containerization/ecr-registry.md)

### Week 2: Kubernetes & EKS
- [EKS Cluster Setup](service-mesh/eks-setup.md)
- [Kubernetes Fundamentals](service-mesh/k8s-fundamentals.md)
- [Pod and Service Management](service-mesh/pods-services.md)
- [Ingress Controllers](service-mesh/ingress-controllers.md)

### Week 3: Service Mesh & Communication
- [Service Mesh with Istio](service-mesh/istio-implementation.md)
- [Inter-service Communication](service-mesh/service-communication.md)
- [Circuit Breakers and Retries](service-mesh/resilience-patterns.md)
- [Distributed Tracing](service-mesh/distributed-tracing.md)

### Week 4: API Gateway & Service Discovery
- [API Gateway Patterns](api-gateway/gateway-patterns.md)
- [Service Discovery](service-discovery/discovery-patterns.md)
- [Load Balancing Strategies](service-discovery/load-balancing.md)
- [Health Checks and Monitoring](service-discovery/health-monitoring.md)

### Week 5: Observability
- [Centralized Logging](../09-monitoring-observability/centralized-logging.md)
- [Metrics and Monitoring](../09-monitoring-observability/metrics-monitoring.md)
- [Distributed Tracing](../09-monitoring-observability/distributed-tracing.md)
- [Alerting Strategies](../09-monitoring-observability/alerting.md)

### Week 6: Advanced Patterns
- [Event-Driven Microservices](advanced-patterns/event-driven.md)
- [CQRS and Event Sourcing](advanced-patterns/cqrs-event-sourcing.md)
- [Saga Pattern](advanced-patterns/saga-pattern.md)
- [Deployment Strategies](advanced-patterns/deployment-strategies.md)

## 🛠️ Hands-on Projects

### Project 1: E-commerce Microservices (Week 1-2)
**Objective**: Build a complete e-commerce platform using microservices

**Services to Implement**:
- User Service (authentication, profiles)
- Product Service (catalog, inventory)
- Order Service (cart, checkout, orders)
- Payment Service (payment processing)
- Notification Service (emails, SMS)

**Technology Stack**:
- **Containers**: Docker + ECR
- **Orchestration**: ECS Fargate initially, then EKS
- **Databases**: RDS (Users/Products), DynamoDB (Orders), ElastiCache (Sessions)
- **API Gateway**: AWS API Gateway
- **Message Queue**: SQS for async processing

### Project 2: Microservices with Service Mesh (Week 3-4)
**Objective**: Enhance the e-commerce platform with service mesh

**Enhancements**:
- Deploy on EKS with Istio service mesh
- Implement mTLS between services
- Add traffic management and load balancing
- Implement circuit breakers and retries
- Add distributed tracing with Jaeger

**Service Mesh Features**:
```yaml
Traffic Management:
  - Blue/Green deployments
  - Canary releases
  - Traffic splitting for A/B testing
  - Circuit breaker patterns

Security:
  - mTLS encryption
  - Service-to-service authentication
  - Rate limiting per service
  - Network policies

Observability:
  - Distributed tracing
  - Service metrics
  - Access logs
  - Performance monitoring
```

### Project 3: Event-Driven Architecture (Week 5-6)
**Objective**: Transform to event-driven microservices

**Event-Driven Components**:
- EventBridge for service communication
- SQS for reliable message delivery
- SNS for pub/sub notifications
- Step Functions for complex workflows
- Lambda for lightweight processing

**Event Flows**:
```
Order Placed Event:
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │Order Service│───▶│ EventBridge │───▶│   SNS       │
  └─────────────┘    └─────────────┘    └─────────────┘
                                               │
          ┌────────────────────────────────────┼────────────────┐
          ▼                    ▼                    ▼            ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐  ┌──────────┐
    │Inventory │        │ Payment  │        │Shipping  │  │   Email  │
    │ Service  │        │ Service  │        │ Service  │  │ Service  │
    └──────────┘        └──────────┘        └──────────┘  └──────────┘
```

## 📋 Service Design Patterns

### 1. Database per Service Pattern
```python
# User Service - PostgreSQL
class UserService:
    def __init__(self):
        self.db = PostgreSQLConnection()

    def create_user(self, user_data):
        return self.db.insert('users', user_data)

    def get_user(self, user_id):
        return self.db.select('users', {'id': user_id})

# Order Service - DynamoDB
class OrderService:
    def __init__(self):
        self.db = DynamoDBResource()

    def create_order(self, order_data):
        table = self.db.Table('orders')
        return table.put_item(Item=order_data)

    def get_orders(self, user_id):
        table = self.db.Table('orders')
        return table.query(
            IndexName='UserIndex',
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
```

### 2. API Gateway Pattern
```yaml
# API Gateway Configuration
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: ecommerce-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - api.ecommerce.com
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: api-cert
    hosts:
    - api.ecommerce.com

---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ecommerce-routes
spec:
  hosts:
  - api.ecommerce.com
  gateways:
  - ecommerce-gateway
  http:
  - match:
    - uri:
        prefix: /users
    route:
    - destination:
        host: user-service
        port:
          number: 80
  - match:
    - uri:
        prefix: /products
    route:
    - destination:
        host: product-service
        port:
          number: 80
  - match:
    - uri:
        prefix: /orders
    route:
    - destination:
        host: order-service
        port:
          number: 80
```

### 3. Circuit Breaker Pattern
```python
import circuitbreaker

class PaymentServiceClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    @circuitbreaker.circuit(
        failure_threshold=5,
        recovery_timeout=10,
        expected_exception=requests.RequestException
    )
    def process_payment(self, payment_data):
        try:
            response = self.session.post(
                f"{self.base_url}/payments",
                json=payment_data,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Payment service error: {e}")
            raise

    def fallback_payment(self, payment_data):
        # Fallback to manual processing queue
        sqs = boto3.client('sqs')
        sqs.send_message(
            QueueUrl=os.environ['MANUAL_PROCESSING_QUEUE'],
            MessageBody=json.dumps(payment_data)
        )
        return {"status": "queued_for_manual_processing"}
```

### 4. Saga Pattern for Distributed Transactions
```python
# Step Functions State Machine for Order Saga
{
  "Comment": "Order processing saga",
  "StartAt": "ReserveInventory",
  "States": {
    "ReserveInventory": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:ReserveInventory",
      "Next": "ProcessPayment",
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "InventoryReservationFailed"
        }
      ]
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:ProcessPayment",
      "Next": "CreateOrder",
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "PaymentFailed"
        }
      ]
    },
    "CreateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:CreateOrder",
      "Next": "OrderCompleted",
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "OrderCreationFailed"
        }
      ]
    },
    "OrderCompleted": {
      "Type": "Succeed"
    },
    "PaymentFailed": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:ReleaseInventory",
      "Next": "OrderFailed"
    },
    "OrderCreationFailed": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "RefundPayment",
          "States": {
            "RefundPayment": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:region:account:function:RefundPayment",
              "End": true
            }
          }
        },
        {
          "StartAt": "ReleaseInventory",
          "States": {
            "ReleaseInventory": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:region:account:function:ReleaseInventory",
              "End": true
            }
          }
        }
      ],
      "Next": "OrderFailed"
    },
    "InventoryReservationFailed": {
      "Type": "Fail",
      "Cause": "Insufficient inventory"
    },
    "OrderFailed": {
      "Type": "Fail",
      "Cause": "Order processing failed"
    }
  }
}
```

## 🔄 Deployment Strategies

### 1. Blue-Green Deployment
```yaml
# Blue-Green deployment with Istio
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: user-service-deployment
spec:
  hosts:
  - user-service
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: user-service
        subset: green
  - route:
    - destination:
        host: user-service
        subset: blue

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: user-service-destination
spec:
  host: user-service
  subsets:
  - name: blue
    labels:
      version: blue
  - name: green
    labels:
      version: green
```

### 2. Canary Deployment
```yaml
# Canary deployment with traffic splitting
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: product-service-canary
spec:
  hosts:
  - product-service
  http:
  - route:
    - destination:
        host: product-service
        subset: stable
      weight: 90
    - destination:
        host: product-service
        subset: canary
      weight: 10
```

### 3. Rolling Deployment
```yaml
# Kubernetes rolling deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
      - name: order-service
        image: order-service:v2.0
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 20
```

## 📊 Service Communication Patterns

### Synchronous Communication
```python
# HTTP/REST with retry and timeout
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class ServiceClient:
    def __init__(self, base_url, timeout=5.0):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_user(self, user_id):
        response = await self.client.get(f"/users/{user_id}")
        response.raise_for_status()
        return response.json()

    async def create_order(self, order_data):
        response = await self.client.post("/orders", json=order_data)
        response.raise_for_status()
        return response.json()
```

### Asynchronous Communication
```python
# Event-driven communication with SQS
import boto3
import json

class EventPublisher:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.sns = boto3.client('sns')

    def publish_order_event(self, event_type, order_data):
        message = {
            'eventType': event_type,
            'orderId': order_data['id'],
            'timestamp': datetime.utcnow().isoformat(),
            'data': order_data
        }

        # Publish to SNS for fan-out
        self.sns.publish(
            TopicArn=os.environ['ORDER_EVENTS_TOPIC'],
            Message=json.dumps(message),
            MessageAttributes={
                'eventType': {
                    'DataType': 'String',
                    'StringValue': event_type
                }
            }
        )

class EventConsumer:
    def __init__(self, queue_url):
        self.sqs = boto3.client('sqs')
        self.queue_url = queue_url

    def process_messages(self):
        while True:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20
            )

            messages = response.get('Messages', [])
            for message in messages:
                try:
                    self.handle_message(json.loads(message['Body']))
                    self.sqs.delete_message(
                        QueueUrl=self.queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

    def handle_message(self, message):
        event_type = message['eventType']
        if event_type == 'OrderPlaced':
            self.handle_order_placed(message['data'])
        elif event_type == 'PaymentProcessed':
            self.handle_payment_processed(message['data'])
```

## 💰 Cost Optimization for Microservices

### Container Optimization
```dockerfile
# Multi-stage build for smaller images
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:16-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
USER node
CMD ["node", "server.js"]
```

### Resource Right-Sizing
```yaml
# Kubernetes resource limits and requests
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  template:
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        env:
        - name: NODE_ENV
          value: "production"
```

### Auto-Scaling Configuration
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: user-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: user-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 🔒 Security Best Practices

### Container Security
```dockerfile
# Security-hardened Dockerfile
FROM node:16-alpine AS builder
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodeuser -u 1001

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:16-alpine AS runtime
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodeuser -u 1001

WORKDIR /app
COPY --from=builder --chown=nodeuser:nodejs /app/node_modules ./node_modules
COPY --chown=nodeuser:nodejs . .

USER nodeuser
EXPOSE 3000
CMD ["node", "server.js"]
```

### Network Security
```yaml
# Network policies for microservices
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: user-service-netpol
spec:
  podSelector:
    matchLabels:
      app: user-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 3000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: user-database
    ports:
    - protocol: TCP
      port: 5432
```

## 📈 Monitoring and Observability

### Service Mesh Observability
```yaml
# Istio telemetry configuration
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: default
  namespace: ecommerce
spec:
  metrics:
  - providers:
    - name: prometheus
  - overrides:
    - match:
        metric: ALL_METRICS
      tagOverrides:
        request_id:
          value: "%{REQUEST_ID}"
  tracing:
  - providers:
    - name: jaeger
  accessLogging:
  - providers:
    - name: otel
```

### Custom Metrics
```python
# Application metrics with Prometheus
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')
ORDER_CREATED = Counter('orders_created_total', 'Total orders created')

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        start_time = time.time()

        def new_start_response(status, response_headers):
            REQUEST_COUNT.labels(
                method=environ['REQUEST_METHOD'],
                endpoint=environ['PATH_INFO']
            ).inc()

            REQUEST_LATENCY.observe(time.time() - start_time)
            return start_response(status, response_headers)

        return self.app(environ, new_start_response)

# Start metrics server
start_http_server(8000)
```

## 🎯 Success Criteria

### Technical Achievements
- [ ] **Service Independence**: Services can be deployed independently
- [ ] **Fault Isolation**: Failure in one service doesn't affect others
- [ ] **Scalability**: Individual services scale based on demand
- [ ] **Observability**: Comprehensive monitoring and tracing
- [ ] **Security**: mTLS and network policies implemented

### Operational Excellence
- [ ] **CI/CD**: Automated testing and deployment pipelines
- [ ] **Disaster Recovery**: Services recover automatically from failures
- [ ] **Performance**: Meet SLA requirements for each service
- [ ] **Cost Optimization**: Right-sized resources and auto-scaling
- [ ] **Documentation**: Complete API documentation and runbooks

## 🚀 Next Steps

After mastering microservices:
1. **Explore [Serverless Architecture](../05-serverless-architecture/)** - Event-driven serverless patterns
2. **Implement [Data Engineering](../06-data-engineering/)** - Data pipelines and analytics
3. **Build [Complex Projects](../07-real-world-projects/)** - Apply microservices to real applications

---

**Ready to build microservices?** Start with [Containerization](containerization/) to begin your microservices journey!

*Remember: Microservices are not a silver bullet—they bring complexity. Use them when the benefits outweigh the operational overhead.*