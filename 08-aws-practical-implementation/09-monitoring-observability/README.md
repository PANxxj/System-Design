# Monitoring and Observability on AWS 📊

Master comprehensive monitoring, logging, and observability strategies for production AWS applications.

## 🎯 Learning Objectives

After completing this section, you'll be able to:
- Implement comprehensive monitoring strategies
- Set up centralized logging and log analysis
- Create effective alerting and notification systems
- Build observability into distributed systems
- Troubleshoot issues using monitoring data

## 📚 Prerequisites

**Required Completion**:
- [x] [Scalable Architectures](../03-scalable-architectures/) - Understanding of distributed systems
- [x] [Microservices Implementation](../04-microservices-implementation/) - Service-oriented architecture
- [x] [Basic Web Application](../02-basic-web-application/) - Application deployment

**Technical Skills**:
- Understanding of metrics, logs, and traces
- Basic knowledge of JSON and query languages
- Experience with distributed applications
- Familiarity with AWS services

## ⏱️ Time Commitment

**Total Duration**: 3-4 weeks (20-25 hours)
- **Week 1**: CloudWatch fundamentals and custom metrics (6-7 hours)
- **Week 2**: Centralized logging and log analysis (6-7 hours)
- **Week 3**: Distributed tracing and APM (5-6 hours)
- **Week 4**: Advanced monitoring and cost optimization (3-4 hours)

## 🏗️ Observability Architecture

### The Three Pillars of Observability
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     METRICS     │    │      LOGS       │    │     TRACES      │
│                 │    │                 │    │                 │
│ • CPU Usage     │    │ • Application   │    │ • Request Flow  │
│ • Response Time │    │ • Error Logs    │    │ • Dependencies  │
│ • Error Rate    │    │ • Access Logs   │    │ • Performance   │
│ • Throughput    │    │ • Audit Trails  │    │ • Bottlenecks   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │   OBSERVABILITY         │
                    │   PLATFORM              │
                    │                         │
                    │ • CloudWatch            │
                    │ • X-Ray                 │
                    │ • OpenSearch            │
                    │ • Grafana               │
                    └─────────────────────────┘
```

### Complete Monitoring Stack
```
Applications → CloudWatch Agent → CloudWatch Metrics
     ↓              ↓                      ↓
   X-Ray        Log Groups            Custom Dashboards
     ↓              ↓                      ↓
  Traces    OpenSearch/ELK           CloudWatch Alarms
     ↓              ↓                      ↓
  Jaeger      Kibana Dashboards           SNS Alerts
     ↓              ↓                      ↓
 Service Map   Log Analysis           PagerDuty/Slack
```

## 🗂️ Section Contents

### Week 1: CloudWatch Fundamentals
- [CloudWatch Metrics](cloudwatch/metrics.md)
- [Custom Metrics and Dimensions](cloudwatch/custom-metrics.md)
- [CloudWatch Dashboards](cloudwatch/dashboards.md)
- [CloudWatch Alarms](cloudwatch/alarms.md)

### Week 2: Centralized Logging
- [Log Aggregation Strategies](centralized-logging/log-aggregation.md)
- [CloudWatch Logs](centralized-logging/cloudwatch-logs.md)
- [ELK Stack on AWS](centralized-logging/elk-stack.md)
- [Log Analysis and Queries](centralized-logging/log-analysis.md)

### Week 3: Distributed Tracing
- [X-Ray Implementation](distributed-tracing/xray-setup.md)
- [Custom Tracing](distributed-tracing/custom-tracing.md)
- [Service Maps](distributed-tracing/service-maps.md)
- [Performance Analysis](distributed-tracing/performance-analysis.md)

### Week 4: Advanced Monitoring
- [Infrastructure Monitoring](advanced-monitoring/infrastructure.md)
- [Application Performance Monitoring](advanced-monitoring/apm.md)
- [Cost Monitoring](advanced-monitoring/cost-monitoring.md)
- [Compliance and Security Monitoring](advanced-monitoring/security-monitoring.md)

## 🛠️ Hands-on Labs

### Lab 1: Complete E-commerce Monitoring (Week 1-2)
**Objective**: Implement comprehensive monitoring for a microservices e-commerce platform

**Components to Monitor**:
- Web tier (Load balancers, EC2/ECS)
- Application tier (Microservices)
- Data tier (RDS, DynamoDB, ElastiCache)
- Infrastructure (VPC, Security Groups)

**Metrics Collection**:
```yaml
Business Metrics:
  - Orders per minute
  - Revenue per hour
  - Cart abandonment rate
  - User session duration

Technical Metrics:
  - Response time percentiles (P50, P95, P99)
  - Error rates by service
  - Throughput (RPS)
  - Database connection pool usage

Infrastructure Metrics:
  - CPU/Memory utilization
  - Network I/O
  - Disk usage and IOPS
  - Load balancer health
```

### Lab 2: Centralized Logging Implementation (Week 2)
**Objective**: Set up centralized logging with search and analysis capabilities

**Log Sources**:
- Application logs from all microservices
- Access logs from load balancers
- Database slow query logs
- Security logs from WAF and VPC Flow Logs

**Log Processing Pipeline**:
```
Applications → CloudWatch Logs → Kinesis Data Firehose → S3
     ↓                               ↓
Log Groups                    OpenSearch Service
     ↓                               ↓
Log Insights                   Kibana Dashboards
```

### Lab 3: Distributed Tracing Setup (Week 3)
**Objective**: Implement end-to-end request tracing across microservices

**Tracing Implementation**:
- X-Ray tracing for Lambda functions
- Custom instrumentation for containerized services
- Database query tracing
- External API call tracing

**Service Map Creation**:
```python
# X-Ray instrumentation example
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch AWS SDK calls
patch_all()

@xray_recorder.capture('order_processing')
def process_order(order_data):
    with xray_recorder.in_subsegment('validate_order'):
        validate_order(order_data)

    with xray_recorder.in_subsegment('check_inventory'):
        inventory_result = check_inventory(order_data['items'])

    with xray_recorder.in_subsegment('process_payment'):
        payment_result = process_payment(order_data['payment'])

    return create_order(order_data, inventory_result, payment_result)
```

## 📊 Monitoring Strategies

### 1. The Four Golden Signals
```yaml
Latency:
  Description: Time taken to serve a request
  Metrics:
    - P50, P95, P99 response times
    - Database query times
    - Cache hit/miss latency
  Thresholds:
    - Warning: P95 > 500ms
    - Critical: P95 > 1000ms

Traffic:
  Description: Demand on the system
  Metrics:
    - Requests per second
    - Transactions per minute
    - Concurrent users
  Monitoring:
    - Baseline trending
    - Capacity planning

Errors:
  Description: Rate of failed requests
  Metrics:
    - HTTP 4xx/5xx error rates
    - Application exception rates
    - Database connection errors
  Thresholds:
    - Warning: Error rate > 1%
    - Critical: Error rate > 5%

Saturation:
  Description: How full the service is
  Metrics:
    - CPU/Memory utilization
    - Database connection pool usage
    - Queue depth
  Thresholds:
    - Warning: Utilization > 70%
    - Critical: Utilization > 90%
```

### 2. RED Method (Rate, Errors, Duration)
```python
# Custom metrics implementation for RED method
import boto3
import time
from functools import wraps

class MetricsCollector:
    def __init__(self, service_name):
        self.cloudwatch = boto3.client('cloudwatch')
        self.service_name = service_name

    def record_request(self, endpoint, duration, status_code):
        """Record request metrics following RED method"""

        # Rate: Request count
        self.cloudwatch.put_metric_data(
            Namespace=f'Application/{self.service_name}',
            MetricData=[
                {
                    'MetricName': 'RequestCount',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'Service', 'Value': self.service_name},
                        {'Name': 'Endpoint', 'Value': endpoint}
                    ]
                }
            ]
        )

        # Errors: Error rate
        is_error = 1 if status_code >= 400 else 0
        self.cloudwatch.put_metric_data(
            Namespace=f'Application/{self.service_name}',
            MetricData=[
                {
                    'MetricName': 'ErrorCount',
                    'Value': is_error,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'Service', 'Value': self.service_name},
                        {'Name': 'Endpoint', 'Value': endpoint}
                    ]
                }
            ]
        )

        # Duration: Response time
        self.cloudwatch.put_metric_data(
            Namespace=f'Application/{self.service_name}',
            MetricData=[
                {
                    'MetricName': 'ResponseTime',
                    'Value': duration * 1000,  # Convert to milliseconds
                    'Unit': 'Milliseconds',
                    'Dimensions': [
                        {'Name': 'Service', 'Value': self.service_name},
                        {'Name': 'Endpoint', 'Value': endpoint}
                    ]
                }
            ]
        )

def monitor_endpoint(service_name, endpoint):
    """Decorator to monitor endpoint performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = MetricsCollector(service_name)
            start_time = time.time()
            status_code = 200

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_request(endpoint, duration, status_code)

        return wrapper
    return decorator

# Usage example
@monitor_endpoint('user-service', '/users')
def get_users():
    # Application logic
    return fetch_users_from_database()
```

### 3. USE Method (Utilization, Saturation, Errors)
```python
# Infrastructure monitoring following USE method
class InfrastructureMonitor:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')

    def monitor_ec2_instance(self, instance_id):
        """Monitor EC2 instance using USE method"""

        # Utilization metrics
        utilization_metrics = [
            'CPUUtilization',
            'NetworkIn',
            'NetworkOut',
            'DiskReadBytes',
            'DiskWriteBytes'
        ]

        for metric in utilization_metrics:
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName=metric,
                Dimensions=[
                    {'Name': 'InstanceId', 'Value': instance_id}
                ],
                StartTime=datetime.utcnow() - timedelta(minutes=5),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average', 'Maximum']
            )

            if response['Datapoints']:
                latest = max(response['Datapoints'], key=lambda x: x['Timestamp'])
                self.check_utilization_threshold(metric, latest['Average'])

    def monitor_rds_instance(self, db_instance_id):
        """Monitor RDS instance for saturation"""

        saturation_metrics = {
            'DatabaseConnections': 80,  # Threshold percentage
            'ReadLatency': 0.2,         # 200ms threshold
            'WriteLatency': 0.2,        # 200ms threshold
            'FreeStorageSpace': 20      # 20% free space minimum
        }

        for metric, threshold in saturation_metrics.items():
            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName=metric,
                Dimensions=[
                    {'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}
                ],
                StartTime=datetime.utcnow() - timedelta(minutes=10),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )

            if response['Datapoints']:
                latest = max(response['Datapoints'], key=lambda x: x['Timestamp'])
                self.check_saturation_threshold(metric, latest['Average'], threshold)
```

## 🔍 Log Analysis Strategies

### 1. Structured Logging
```python
import json
import logging
from datetime import datetime

class StructuredLogger:
    def __init__(self, service_name):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)

        # Configure structured logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_event(self, event_type, message, **kwargs):
        """Log structured event"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'event_type': event_type,
            'message': message,
            'level': 'INFO',
            **kwargs
        }

        self.logger.info(json.dumps(log_entry))

    def log_request(self, request_id, method, path, status_code, duration):
        """Log HTTP request"""
        self.log_event(
            'http_request',
            f'{method} {path} - {status_code}',
            request_id=request_id,
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration * 1000
        )

    def log_error(self, error, context=None):
        """Log error with context"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'event_type': 'error',
            'level': 'ERROR',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }

        self.logger.error(json.dumps(log_entry))

# Usage
logger = StructuredLogger('order-service')

# Log successful operation
logger.log_event('order_created', 'Order created successfully',
                 order_id='ord_123', customer_id='cust_456', amount=99.99)

# Log HTTP request
logger.log_request('req_789', 'POST', '/orders', 201, 0.156)

# Log error
try:
    process_payment(order_data)
except PaymentError as e:
    logger.log_error(e, {'order_id': 'ord_123', 'payment_method': 'credit_card'})
```

### 2. Log Correlation
```python
import uuid
from contextvars import ContextVar

# Context variable for request correlation
correlation_id_var: ContextVar[str] = ContextVar('correlation_id')

class CorrelationMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Generate or extract correlation ID
        correlation_id = environ.get('HTTP_X_CORRELATION_ID', str(uuid.uuid4()))
        correlation_id_var.set(correlation_id)

        def new_start_response(status, response_headers):
            # Add correlation ID to response headers
            response_headers.append(('X-Correlation-ID', correlation_id))
            return start_response(status, response_headers)

        return self.app(environ, new_start_response)

class CorrelatedLogger:
    def __init__(self, service_name):
        self.service_name = service_name

    def log(self, level, message, **kwargs):
        """Log with correlation ID"""
        correlation_id = correlation_id_var.get('unknown')

        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': self.service_name,
            'correlation_id': correlation_id,
            'level': level,
            'message': message,
            **kwargs
        }

        print(json.dumps(log_entry))

# Service calls with correlation
async def call_user_service(user_id):
    """Call user service with correlation ID"""
    correlation_id = correlation_id_var.get('unknown')

    headers = {'X-Correlation-ID': correlation_id}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'http://user-service/users/{user_id}',
            headers=headers
        )
        return response.json()
```

### 3. Log Aggregation and Search
```yaml
# CloudWatch Logs Insights queries
# Find errors in the last hour
fields @timestamp, @message, error_type, service
| filter @timestamp > @timestamp - 1h
| filter level = "ERROR"
| sort @timestamp desc
| limit 100

# Analyze response times by endpoint
fields @timestamp, duration_ms, path
| filter event_type = "http_request"
| filter @timestamp > @timestamp - 1h
| stats avg(duration_ms), max(duration_ms), count() by path
| sort avg desc

# Track user journey by correlation ID
fields @timestamp, @message, service, event_type
| filter correlation_id = "specific-correlation-id"
| sort @timestamp asc

# Find slow database queries
fields @timestamp, @message, query_duration
| filter service = "database"
| filter query_duration > 1000
| sort query_duration desc
| limit 20
```

## 🚨 Alerting Strategies

### 1. Alert Hierarchy
```yaml
Critical Alerts (Immediate Response):
  - Service completely down (100% error rate)
  - Database unavailable
  - Payment processing failures
  - Security breaches
  Notification: PagerDuty + Phone + Slack
  Response Time: < 5 minutes

Warning Alerts (Business Hours Response):
  - High error rate (> 5%)
  - Slow response times (P95 > 1s)
  - High resource utilization (> 80%)
  - Failed backup jobs
  Notification: Slack + Email
  Response Time: < 1 hour

Informational Alerts (Next Business Day):
  - Cost anomalies
  - Capacity planning warnings
  - Performance degradation trends
  - Non-critical configuration drifts
  Notification: Email + Dashboard
  Response Time: < 24 hours
```

### 2. Smart Alerting Implementation
```python
import boto3
from datetime import datetime, timedelta

class IntelligentAlerting:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.sns = boto3.client('sns')

    def create_composite_alarm(self, alarm_name, alarms_list):
        """Create composite alarm based on multiple conditions"""

        # Create composite alarm that triggers when multiple conditions are met
        self.cloudwatch.put_composite_alarm(
            AlarmName=alarm_name,
            AlarmDescription='Composite alarm for service health',
            ActionsEnabled=True,
            AlarmActions=[
                os.environ['CRITICAL_ALERT_TOPIC_ARN']
            ],
            AlarmRule=f"({' AND '.join(alarms_list)})",
            InsufficientDataActions=[],
            OKActions=[]
        )

    def create_anomaly_alarm(self, metric_name, threshold_std_dev=2):
        """Create anomaly detection alarm"""

        # Create anomaly detector
        self.cloudwatch.put_anomaly_detector(
            Namespace='Application/UserService',
            MetricName=metric_name,
            Dimensions=[
                {'Name': 'Service', 'Value': 'user-service'}
            ],
            Stat='Average'
        )

        # Create alarm based on anomaly detection
        self.cloudwatch.put_metric_alarm(
            AlarmName=f'{metric_name}-Anomaly',
            ComparisonOperator='LessThanLowerOrGreaterThanUpperThreshold',
            EvaluationPeriods=2,
            Metrics=[
                {
                    'Id': 'm1',
                    'ReturnData': True,
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'Application/UserService',
                            'MetricName': metric_name,
                            'Dimensions': [
                                {'Name': 'Service', 'Value': 'user-service'}
                            ]
                        },
                        'Period': 300,
                        'Stat': 'Average'
                    }
                },
                {
                    'Id': 'ad1',
                    'Expression': f'ANOMALY_DETECTION_FUNCTION(m1, {threshold_std_dev})'
                }
            ],
            ThresholdMetricId='ad1',
            ActionsEnabled=True,
            AlarmActions=[
                os.environ['WARNING_ALERT_TOPIC_ARN']
            ]
        )

    def suppress_alert_during_deployment(self, alarm_name, duration_minutes=30):
        """Temporarily suppress alerts during deployment"""

        # Disable alarm
        self.cloudwatch.disable_alarm_actions(AlarmNames=[alarm_name])

        # Schedule re-enabling (this would be done via Lambda + EventBridge)
        # For brevity, showing the concept
        lambda_client = boto3.client('lambda')
        lambda_client.invoke(
            FunctionName='ReenableAlarmFunction',
            InvocationType='Event',
            Payload=json.dumps({
                'alarm_name': alarm_name,
                'delay_minutes': duration_minutes
            })
        )
```

### 3. Alert Fatigue Prevention
```python
class AlertManager:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.alerts_table = self.dynamodb.Table('AlertHistory')

    def should_send_alert(self, alert_type, service, threshold_minutes=60):
        """Prevent duplicate alerts within threshold period"""

        # Check if similar alert was sent recently
        recent_alerts = self.alerts_table.query(
            KeyConditionExpression=Key('alert_type').eq(alert_type),
            FilterExpression=Attr('service').eq(service) &
                           Attr('timestamp').gt(
                               (datetime.utcnow() - timedelta(minutes=threshold_minutes)).isoformat()
                           )
        )

        if recent_alerts['Count'] > 0:
            return False

        # Record this alert
        self.alerts_table.put_item(
            Item={
                'alert_type': alert_type,
                'service': service,
                'timestamp': datetime.utcnow().isoformat(),
                'ttl': int((datetime.utcnow() + timedelta(days=7)).timestamp())
            }
        )

        return True

    def escalate_alert(self, alert_data, escalation_level=1):
        """Escalate unacknowledged alerts"""

        if escalation_level == 1:
            # Send to primary on-call
            self.send_notification('primary-oncall', alert_data)
        elif escalation_level == 2:
            # Send to secondary on-call
            self.send_notification('secondary-oncall', alert_data)
        elif escalation_level >= 3:
            # Send to management
            self.send_notification('management', alert_data)
```

## 💰 Cost Monitoring

### CloudWatch Cost Optimization
```python
class CostMonitor:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')
        self.ce = boto3.client('ce')  # Cost Explorer

    def monitor_cloudwatch_costs(self):
        """Monitor CloudWatch usage and costs"""

        # Get CloudWatch usage metrics
        response = self.ce.get_dimension_values(
            TimePeriod={
                'Start': (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'End': datetime.utcnow().strftime('%Y-%m-%d')
            },
            Dimension='SERVICE',
            Context='COST_AND_USAGE'
        )

        cloudwatch_costs = self.ce.get_cost_and_usage(
            TimePeriod={
                'Start': (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'End': datetime.utcnow().strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )

        # Analyze and optimize
        for result in cloudwatch_costs['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['BlendedCost']['Amount'])

                if service == 'Amazon CloudWatch' and cost > 100:  # $100 threshold
                    self.recommend_optimizations(cost)

    def recommend_optimizations(self, current_cost):
        """Recommend cost optimizations"""
        recommendations = []

        # Check log retention periods
        logs_client = boto3.client('logs')
        log_groups = logs_client.describe_log_groups()

        for group in log_groups['logGroups']:
            retention_days = group.get('retentionInDays')
            if not retention_days or retention_days > 30:
                recommendations.append(
                    f"Consider reducing retention for {group['logGroupName']} to 30 days"
                )

        # Check custom metrics volume
        # This would involve analyzing metric usage patterns

        return recommendations
```

## 🎯 Success Criteria

### Technical Achievements
- [ ] **Complete Visibility**: 100% of services have monitoring
- [ ] **Fast Detection**: Issues detected within 1 minute
- [ ] **Low Noise**: < 5% false positive alert rate
- [ ] **Quick Resolution**: Mean time to resolution < 30 minutes
- [ ] **Cost Efficiency**: Monitoring costs < 5% of total infrastructure

### Operational Excellence
- [ ] **Dashboards**: Real-time visibility into system health
- [ ] **Runbooks**: Documented response procedures for all alerts
- [ ] **Training**: Team can effectively use monitoring tools
- [ ] **Continuous Improvement**: Regular review and optimization of monitoring
- [ ] **Compliance**: Audit logs and security monitoring in place

## 🚀 Next Steps

After mastering monitoring and observability:
1. **Implement [Cost Optimization](../10-cost-optimization/)** - Advanced cost management
2. **Apply to [Real-world Projects](../07-real-world-projects/)** - Production monitoring
3. **Explore [Advanced Topics](../../07-advanced-topics/)** - Chaos engineering and SRE practices

---

**Ready to monitor everything?** Start with [CloudWatch Fundamentals](cloudwatch/) to build your observability foundation!

*Remember: You can't improve what you can't measure. Comprehensive monitoring is the foundation of reliable systems.*