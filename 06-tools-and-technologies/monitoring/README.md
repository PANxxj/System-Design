# Monitoring and Observability Tools

## Overview
Comprehensive monitoring and observability are essential for maintaining healthy distributed systems. This guide covers monitoring tools, metrics collection, alerting, and observability best practices with practical implementations.

## Table of Contents
1. [Monitoring Stack Architecture](#monitoring-stack-architecture)
2. [Metrics Collection](#metrics-collection)
3. [Logging Systems](#logging-systems)
4. [Distributed Tracing](#distributed-tracing)
5. [Alerting and Notification](#alerting-and-notification)
6. [Dashboards and Visualization](#dashboards-and-visualization)
7. [Implementation Examples](#implementation-examples)

## Monitoring Stack Architecture

### Complete Monitoring Stack Setup

```python
import asyncio
import time
import psutil
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import requests
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import structlog

@dataclass
class MetricData:
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = None
    metric_type: str = "gauge"  # gauge, counter, histogram

    def __post_init__(self):
        if self.labels is None:
            self.labels = {}

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    service: str
    message: str
    context: Dict[str, Any] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}

class PrometheusMetrics:
    def __init__(self, service_name: str):
        self.service_name = service_name

        # Standard metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )

        self.request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )

        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections'
        )

        self.memory_usage = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes'
        )

        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage'
        )

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()

        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def update_system_metrics(self):
        """Update system-level metrics"""
        # Memory metrics
        memory = psutil.virtual_memory()
        self.memory_usage.set(memory.used)

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.set(cpu_percent)

    def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics server"""
        start_http_server(port)
        logging.info(f"Metrics server started on port {port}")
```

## Metrics Collection

### Custom Metrics Collector

```python
class MetricsCollector:
    def __init__(self, prometheus_gateway: str, influxdb_client=None):
        self.prometheus_gateway = prometheus_gateway
        self.influxdb = influxdb_client
        self.custom_metrics = {}
        self.collection_interval = 10  # seconds

    async def start_collection(self):
        """Start metrics collection loop"""
        while True:
            try:
                await self.collect_application_metrics()
                await self.collect_infrastructure_metrics()
                await self.collect_business_metrics()

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                logging.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self.collection_interval)

    async def collect_application_metrics(self):
        """Collect application-specific metrics"""
        metrics = []

        # Database connection pool metrics
        db_metrics = await self.get_database_metrics()
        metrics.extend(db_metrics)

        # Cache hit rate metrics
        cache_metrics = await self.get_cache_metrics()
        metrics.extend(cache_metrics)

        # Queue length metrics
        queue_metrics = await self.get_queue_metrics()
        metrics.extend(queue_metrics)

        # Send to time series database
        await self.send_metrics(metrics)

    async def get_database_metrics(self) -> List[MetricData]:
        """Collect database performance metrics"""
        metrics = []

        # Simulate database metrics collection
        db_pools = ['primary', 'replica_1', 'replica_2']

        for pool_name in db_pools:
            # Active connections
            active_connections = await self.get_db_active_connections(pool_name)
            metrics.append(MetricData(
                name="db_active_connections",
                value=active_connections,
                timestamp=datetime.utcnow(),
                labels={"pool": pool_name}
            ))

            # Query response time
            avg_response_time = await self.get_db_avg_response_time(pool_name)
            metrics.append(MetricData(
                name="db_avg_response_time_ms",
                value=avg_response_time,
                timestamp=datetime.utcnow(),
                labels={"pool": pool_name}
            ))

            # Connection pool utilization
            pool_utilization = await self.get_db_pool_utilization(pool_name)
            metrics.append(MetricData(
                name="db_pool_utilization_percent",
                value=pool_utilization,
                timestamp=datetime.utcnow(),
                labels={"pool": pool_name}
            ))

        return metrics

    async def get_cache_metrics(self) -> List[MetricData]:
        """Collect cache performance metrics"""
        metrics = []

        # Redis metrics
        redis_info = await self.get_redis_info()

        metrics.append(MetricData(
            name="cache_hit_rate",
            value=redis_info.get('hit_rate', 0),
            timestamp=datetime.utcnow(),
            labels={"cache_type": "redis"}
        ))

        metrics.append(MetricData(
            name="cache_memory_usage_bytes",
            value=redis_info.get('used_memory', 0),
            timestamp=datetime.utcnow(),
            labels={"cache_type": "redis"}
        ))

        return metrics

    async def collect_business_metrics(self):
        """Collect business-specific metrics"""
        business_metrics = []

        # User engagement metrics
        active_users = await self.get_active_users_count()
        business_metrics.append(MetricData(
            name="active_users_5min",
            value=active_users,
            timestamp=datetime.utcnow(),
            metric_type="gauge"
        ))

        # Revenue metrics
        hourly_revenue = await self.get_hourly_revenue()
        business_metrics.append(MetricData(
            name="revenue_hourly_usd",
            value=hourly_revenue,
            timestamp=datetime.utcnow(),
            metric_type="gauge"
        ))

        # Error rate metrics
        error_rate = await self.calculate_error_rate()
        business_metrics.append(MetricData(
            name="error_rate_percent",
            value=error_rate,
            timestamp=datetime.utcnow(),
            metric_type="gauge"
        ))

        await self.send_metrics(business_metrics)

class CustomMetricsDecorator:
    def __init__(self, metrics_collector: MetricsCollector):
        self.collector = metrics_collector

    def track_execution_time(self, metric_name: str, labels: Dict[str, str] = None):
        """Decorator to track function execution time"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    success = True
                except Exception as e:
                    success = False
                    raise
                finally:
                    execution_time = time.time() - start_time

                    metric_labels = labels or {}
                    metric_labels['function'] = func.__name__
                    metric_labels['success'] = str(success)

                    metric = MetricData(
                        name=metric_name,
                        value=execution_time,
                        timestamp=datetime.utcnow(),
                        labels=metric_labels,
                        metric_type="histogram"
                    )

                    await self.collector.send_metrics([metric])

                return result
            return wrapper
        return decorator

    def count_invocations(self, metric_name: str, labels: Dict[str, str] = None):
        """Decorator to count function invocations"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                metric_labels = labels or {}
                metric_labels['function'] = func.__name__

                metric = MetricData(
                    name=metric_name,
                    value=1,
                    timestamp=datetime.utcnow(),
                    labels=metric_labels,
                    metric_type="counter"
                )

                await self.collector.send_metrics([metric])

                return await func(*args, **kwargs)
            return wrapper
        return decorator
```

## Logging Systems

### Structured Logging Implementation

```python
class StructuredLogger:
    def __init__(self, service_name: str, log_level: str = "INFO"):
        self.service_name = service_name

        # Configure structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        self.logger = structlog.get_logger(service_name)

    def log_request(self, request_id: str, method: str, path: str,
                   user_id: str = None, **kwargs):
        """Log HTTP request"""
        self.logger.info(
            "HTTP request",
            request_id=request_id,
            method=method,
            path=path,
            user_id=user_id,
            **kwargs
        )

    def log_error(self, error: Exception, context: Dict[str, Any] = None,
                  trace_id: str = None):
        """Log error with context"""
        error_context = context or {}
        error_context.update({
            "error_type": type(error).__name__,
            "error_message": str(error),
            "trace_id": trace_id
        })

        self.logger.error(
            "Error occurred",
            **error_context,
            exc_info=True
        )

    def log_business_event(self, event_type: str, user_id: str,
                          event_data: Dict[str, Any]):
        """Log business events for analytics"""
        self.logger.info(
            "Business event",
            event_type=event_type,
            user_id=user_id,
            event_data=event_data,
            timestamp=datetime.utcnow().isoformat()
        )

class LogAggregator:
    def __init__(self, elasticsearch_client, kafka_producer=None):
        self.es = elasticsearch_client
        self.kafka = kafka_producer
        self.log_buffer = []
        self.buffer_size = 1000
        self.flush_interval = 30  # seconds

    async def start_log_aggregation(self):
        """Start log aggregation service"""
        # Start buffer flushing task
        asyncio.create_task(self.flush_logs_periodically())

        # Process logs from various sources
        await self.process_log_streams()

    async def process_log_streams(self):
        """Process logs from multiple sources"""
        # File-based logs
        asyncio.create_task(self.tail_log_files())

        # Kafka logs
        if self.kafka:
            asyncio.create_task(self.consume_kafka_logs())

        # Syslog
        asyncio.create_task(self.process_syslog())

    async def tail_log_files(self):
        """Tail application log files"""
        import asyncio
        import aiofiles

        log_files = [
            "/var/log/application/app.log",
            "/var/log/application/error.log",
            "/var/log/nginx/access.log"
        ]

        for log_file in log_files:
            asyncio.create_task(self.tail_file(log_file))

    async def tail_file(self, file_path: str):
        """Tail individual log file"""
        try:
            # Simple file tailing implementation
            with open(file_path, 'r') as file:
                # Go to end of file
                file.seek(0, 2)

                while True:
                    line = file.readline()
                    if line:
                        await self.process_log_line(line, file_path)
                    else:
                        await asyncio.sleep(0.1)

        except FileNotFoundError:
            logging.warning(f"Log file not found: {file_path}")
        except Exception as e:
            logging.error(f"Error tailing file {file_path}: {e}")

    async def process_log_line(self, line: str, source: str):
        """Process individual log line"""
        try:
            # Parse log line (assuming JSON format)
            log_entry = json.loads(line.strip())
            log_entry['source'] = source
            log_entry['ingested_at'] = datetime.utcnow().isoformat()

            # Add to buffer
            self.log_buffer.append(log_entry)

            # Flush if buffer is full
            if len(self.log_buffer) >= self.buffer_size:
                await self.flush_logs()

        except json.JSONDecodeError:
            # Handle non-JSON logs
            log_entry = {
                'message': line.strip(),
                'source': source,
                'ingested_at': datetime.utcnow().isoformat(),
                'level': 'info'
            }
            self.log_buffer.append(log_entry)

    async def flush_logs(self):
        """Flush log buffer to Elasticsearch"""
        if not self.log_buffer:
            return

        try:
            # Bulk index to Elasticsearch
            actions = []
            for log_entry in self.log_buffer:
                action = {
                    "_index": f"logs-{datetime.utcnow().strftime('%Y.%m.%d')}",
                    "_source": log_entry
                }
                actions.append(action)

            # Bulk insert
            await self.es.bulk(actions)

            # Clear buffer
            self.log_buffer.clear()

        except Exception as e:
            logging.error(f"Failed to flush logs to Elasticsearch: {e}")

    async def flush_logs_periodically(self):
        """Periodically flush logs"""
        while True:
            await asyncio.sleep(self.flush_interval)
            await self.flush_logs()
```

## Distributed Tracing

### OpenTelemetry Implementation

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import uuid

class DistributedTracing:
    def __init__(self, service_name: str, jaeger_endpoint: str):
        self.service_name = service_name

        # Configure tracer
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)

        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )

        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

        self.tracer = tracer

    def start_span(self, operation_name: str, parent_context=None) -> trace.Span:
        """Start a new span"""
        if parent_context:
            with trace.use_span(parent_context):
                span = self.tracer.start_span(operation_name)
        else:
            span = self.tracer.start_span(operation_name)

        return span

    def trace_function(self, operation_name: str = None):
        """Decorator to trace function execution"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"

                with self.tracer.start_as_current_span(op_name) as span:
                    # Add function metadata
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)

                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("function.result", "success")
                        return result
                    except Exception as e:
                        span.set_attribute("function.result", "error")
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        raise

            return wrapper
        return decorator

    def trace_http_request(self, method: str, url: str, status_code: int,
                          duration: float, **kwargs):
        """Trace HTTP request"""
        with self.tracer.start_as_current_span("http_request") as span:
            span.set_attribute("http.method", method)
            span.set_attribute("http.url", url)
            span.set_attribute("http.status_code", status_code)
            span.set_attribute("http.duration", duration)

            for key, value in kwargs.items():
                span.set_attribute(f"http.{key}", str(value))

    def trace_database_query(self, query: str, duration: float,
                           affected_rows: int = None):
        """Trace database query"""
        with self.tracer.start_as_current_span("database_query") as span:
            span.set_attribute("db.statement", query)
            span.set_attribute("db.duration", duration)

            if affected_rows is not None:
                span.set_attribute("db.affected_rows", affected_rows)

class TraceContext:
    def __init__(self):
        self.trace_id = None
        self.span_id = None
        self.parent_span_id = None

    @classmethod
    def generate_trace_id(cls) -> str:
        """Generate new trace ID"""
        return str(uuid.uuid4())

    @classmethod
    def generate_span_id(cls) -> str:
        """Generate new span ID"""
        return str(uuid.uuid4())

    def create_child_context(self) -> 'TraceContext':
        """Create child trace context"""
        child_context = TraceContext()
        child_context.trace_id = self.trace_id
        child_context.parent_span_id = self.span_id
        child_context.span_id = self.generate_span_id()

        return child_context
```

## Alerting and Notification

### Alert Management System

```python
class AlertManager:
    def __init__(self, notification_channels: Dict[str, Any]):
        self.notification_channels = notification_channels
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = []

    def define_alert_rule(self, rule_name: str, condition: str,
                         severity: str, notification_channels: List[str]):
        """Define new alert rule"""
        self.alert_rules[rule_name] = {
            'condition': condition,
            'severity': severity,
            'notification_channels': notification_channels,
            'created_at': datetime.utcnow(),
            'enabled': True
        }

    async def evaluate_alerts(self, metrics: List[MetricData]):
        """Evaluate metrics against alert rules"""
        for metric in metrics:
            await self.check_metric_against_rules(metric)

    async def check_metric_against_rules(self, metric: MetricData):
        """Check single metric against all rules"""
        for rule_name, rule in self.alert_rules.items():
            if not rule['enabled']:
                continue

            if await self.evaluate_condition(metric, rule['condition']):
                await self.trigger_alert(rule_name, metric, rule)

    async def evaluate_condition(self, metric: MetricData, condition: str) -> bool:
        """Evaluate alert condition"""
        # Simple condition evaluation (would be more sophisticated in production)
        try:
            # Replace metric placeholders with actual values
            condition_code = condition.replace('value', str(metric.value))
            condition_code = condition_code.replace('metric_name', f"'{metric.name}'")

            return eval(condition_code)
        except Exception as e:
            logging.error(f"Error evaluating condition '{condition}': {e}")
            return False

    async def trigger_alert(self, rule_name: str, metric: MetricData, rule: Dict):
        """Trigger alert and send notifications"""
        alert_id = str(uuid.uuid4())

        alert = {
            'alert_id': alert_id,
            'rule_name': rule_name,
            'severity': rule['severity'],
            'metric_name': metric.name,
            'metric_value': metric.value,
            'timestamp': datetime.utcnow(),
            'status': 'firing'
        }

        # Check if this is a duplicate alert (same rule firing repeatedly)
        if self.is_duplicate_alert(rule_name, metric):
            return

        # Add to active alerts
        self.active_alerts[alert_id] = alert

        # Send notifications
        await self.send_notifications(alert, rule['notification_channels'])

        # Add to history
        self.alert_history.append(alert)

    def is_duplicate_alert(self, rule_name: str, metric: MetricData) -> bool:
        """Check if this is a duplicate alert"""
        # Check if same rule has fired in last 5 minutes
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)

        for alert in self.active_alerts.values():
            if (alert['rule_name'] == rule_name and
                alert['timestamp'] > cutoff_time and
                alert['status'] == 'firing'):
                return True

        return False

    async def send_notifications(self, alert: Dict, channels: List[str]):
        """Send alert notifications to specified channels"""
        for channel in channels:
            if channel in self.notification_channels:
                await self.send_notification(alert, channel)

    async def send_notification(self, alert: Dict, channel: str):
        """Send notification to specific channel"""
        channel_config = self.notification_channels[channel]

        if channel_config['type'] == 'slack':
            await self.send_slack_notification(alert, channel_config)
        elif channel_config['type'] == 'email':
            await self.send_email_notification(alert, channel_config)
        elif channel_config['type'] == 'pagerduty':
            await self.send_pagerduty_notification(alert, channel_config)

    async def send_slack_notification(self, alert: Dict, config: Dict):
        """Send Slack notification"""
        webhook_url = config['webhook_url']

        message = {
            "text": f"🚨 Alert: {alert['rule_name']}",
            "attachments": [
                {
                    "color": "danger" if alert['severity'] == 'critical' else "warning",
                    "fields": [
                        {
                            "title": "Metric",
                            "value": alert['metric_name'],
                            "short": True
                        },
                        {
                            "title": "Value",
                            "value": str(alert['metric_value']),
                            "short": True
                        },
                        {
                            "title": "Severity",
                            "value": alert['severity'],
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": alert['timestamp'].isoformat(),
                            "short": True
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(webhook_url, json=message)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed to send Slack notification: {e}")

    async def resolve_alert(self, alert_id: str):
        """Resolve an active alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert['status'] = 'resolved'
            alert['resolved_at'] = datetime.utcnow()

            # Remove from active alerts
            del self.active_alerts[alert_id]

            # Send resolution notification
            await self.send_resolution_notification(alert)

class AlertRuleBuilder:
    """Builder for creating complex alert rules"""

    def __init__(self):
        self.conditions = []
        self.severity = 'warning'
        self.channels = []

    def when_metric(self, metric_name: str):
        """Start building condition for specific metric"""
        self.current_metric = metric_name
        return self

    def greater_than(self, threshold: float):
        """Add greater than condition"""
        self.conditions.append(f"metric_name == '{self.current_metric}' and value > {threshold}")
        return self

    def less_than(self, threshold: float):
        """Add less than condition"""
        self.conditions.append(f"metric_name == '{self.current_metric}' and value < {threshold}")
        return self

    def for_duration(self, minutes: int):
        """Add duration condition"""
        # This would require more sophisticated state tracking
        return self

    def with_severity(self, severity: str):
        """Set alert severity"""
        self.severity = severity
        return self

    def notify(self, channels: List[str]):
        """Set notification channels"""
        self.channels = channels
        return self

    def build(self, rule_name: str) -> Dict:
        """Build the final alert rule"""
        return {
            'name': rule_name,
            'condition': ' and '.join(self.conditions),
            'severity': self.severity,
            'notification_channels': self.channels
        }

# Example usage:
# rule = (AlertRuleBuilder()
#         .when_metric('cpu_usage_percent')
#         .greater_than(90)
#         .with_severity('critical')
#         .notify(['slack-ops', 'pagerduty'])
#         .build('high_cpu_alert'))
```

This comprehensive monitoring and observability guide provides production-ready tools and patterns for maintaining visibility into distributed systems. The implementations cover metrics collection, structured logging, distributed tracing, and intelligent alerting - all essential for operating reliable services at scale.