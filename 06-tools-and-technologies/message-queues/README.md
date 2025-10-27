# Message Queues and Event Streaming 🟡

## 🎯 Learning Objectives
- Understand message queue patterns and use cases
- Learn different messaging protocols and systems
- Master event-driven architecture design
- Implement reliable message processing patterns

## 📋 Message Queue Fundamentals

### What are Message Queues?

Message queues are communication systems that enable asynchronous message passing between different components of a distributed system. They provide loose coupling, reliability, and scalability.

### Key Concepts

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import threading
import json
import uuid
from datetime import datetime, timedelta
import heapq
from collections import defaultdict, deque

class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class MessageStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"

@dataclass
class Message:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    body: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 3
    ttl: float = 3600  # Time to live in seconds
    status: MessageStatus = MessageStatus.PENDING

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl

    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries

    def __lt__(self, other):
        # For priority queue ordering
        return self.priority.value > other.priority.value

class MessageQueue(ABC):
    """Abstract base class for message queues"""

    @abstractmethod
    def send(self, message: Message) -> bool:
        pass

    @abstractmethod
    def receive(self, timeout: float = None) -> Optional[Message]:
        pass

    @abstractmethod
    def ack(self, message_id: str) -> bool:
        pass

    @abstractmethod
    def nack(self, message_id: str, requeue: bool = True) -> bool:
        pass

    @abstractmethod
    def size(self) -> int:
        pass
```

## 🏗️ Message Queue Implementations

### 1. In-Memory Priority Queue

```python
import heapq
import threading
from queue import Empty

class InMemoryMessageQueue(MessageQueue):
    """
    In-memory implementation of a priority message queue
    """

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._queue = []
        self._in_flight = {}  # message_id -> message
        self._dead_letter = []
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)

    def send(self, message: Message) -> bool:
        """Send message to the queue"""
        with self._condition:
            if len(self._queue) >= self.max_size:
                return False

            # Add timestamp for FIFO ordering within same priority
            heapq.heappush(self._queue, (message.priority.value, message.timestamp, message))
            self._condition.notify()
            return True

    def receive(self, timeout: float = None) -> Optional[Message]:
        """Receive message from the queue"""
        with self._condition:
            deadline = time.time() + timeout if timeout else None

            while not self._queue:
                if timeout is not None:
                    remaining = deadline - time.time()
                    if remaining <= 0:
                        return None
                    if not self._condition.wait(remaining):
                        return None
                else:
                    self._condition.wait()

            # Get highest priority message
            priority, timestamp, message = heapq.heappop(self._queue)

            # Check if message is expired
            if message.is_expired():
                self._move_to_dead_letter(message, "Message expired")
                return self.receive(timeout)  # Try next message

            # Mark as in-flight
            message.status = MessageStatus.PROCESSING
            self._in_flight[message.id] = message
            return message

    def ack(self, message_id: str) -> bool:
        """Acknowledge message processing"""
        with self._lock:
            if message_id in self._in_flight:
                message = self._in_flight.pop(message_id)
                message.status = MessageStatus.COMPLETED
                return True
            return False

    def nack(self, message_id: str, requeue: bool = True) -> bool:
        """Negative acknowledge - message processing failed"""
        with self._condition:
            if message_id not in self._in_flight:
                return False

            message = self._in_flight.pop(message_id)
            message.retry_count += 1

            if requeue and message.can_retry():
                message.status = MessageStatus.PENDING
                heapq.heappush(self._queue, (message.priority.value, time.time(), message))
                self._condition.notify()
            else:
                self._move_to_dead_letter(message, "Max retries exceeded")

            return True

    def _move_to_dead_letter(self, message: Message, reason: str):
        """Move message to dead letter queue"""
        message.status = MessageStatus.DEAD_LETTER
        message.headers['dead_letter_reason'] = reason
        message.headers['dead_letter_timestamp'] = str(time.time())
        self._dead_letter.append(message)

    def size(self) -> int:
        """Get queue size"""
        with self._lock:
            return len(self._queue)

    def get_dead_letter_messages(self) -> List[Message]:
        """Get all dead letter messages"""
        with self._lock:
            return list(self._dead_letter)

    def get_in_flight_count(self) -> int:
        """Get count of in-flight messages"""
        with self._lock:
            return len(self._in_flight)

class TopicBasedMessageBroker:
    """
    Message broker with topic-based routing
    """

    def __init__(self):
        self.topics: Dict[str, InMemoryMessageQueue] = {}
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.lock = threading.RLock()

    def create_topic(self, topic_name: str, max_size: int = 10000) -> bool:
        """Create a new topic"""
        with self.lock:
            if topic_name not in self.topics:
                self.topics[topic_name] = InMemoryMessageQueue(max_size)
                return True
            return False

    def publish(self, topic: str, message: Message) -> bool:
        """Publish message to topic"""
        with self.lock:
            if topic not in self.topics:
                self.create_topic(topic)

            message.topic = topic
            success = self.topics[topic].send(message)

            # Notify subscribers
            if success:
                self._notify_subscribers(topic, message)

            return success

    def subscribe(self, topic: str, callback: Callable[[Message], None]) -> bool:
        """Subscribe to topic with callback"""
        with self.lock:
            if topic not in self.topics:
                self.create_topic(topic)

            self.subscribers[topic].append(callback)
            return True

    def unsubscribe(self, topic: str, callback: Callable) -> bool:
        """Unsubscribe from topic"""
        with self.lock:
            if topic in self.subscribers and callback in self.subscribers[topic]:
                self.subscribers[topic].remove(callback)
                return True
            return False

    def consume(self, topic: str, timeout: float = None) -> Optional[Message]:
        """Consume message from topic"""
        with self.lock:
            if topic not in self.topics:
                return None

            return self.topics[topic].receive(timeout)

    def ack(self, topic: str, message_id: str) -> bool:
        """Acknowledge message"""
        with self.lock:
            if topic in self.topics:
                return self.topics[topic].ack(message_id)
            return False

    def nack(self, topic: str, message_id: str, requeue: bool = True) -> bool:
        """Negative acknowledge message"""
        with self.lock:
            if topic in self.topics:
                return self.topics[topic].nack(message_id, requeue)
            return False

    def _notify_subscribers(self, topic: str, message: Message):
        """Notify all subscribers of a topic"""
        for callback in self.subscribers.get(topic, []):
            try:
                threading.Thread(
                    target=callback,
                    args=(message,),
                    daemon=True
                ).start()
            except Exception as e:
                print(f"Error notifying subscriber: {e}")

    def get_topic_stats(self, topic: str) -> Dict[str, Any]:
        """Get statistics for a topic"""
        with self.lock:
            if topic not in self.topics:
                return {}

            queue = self.topics[topic]
            return {
                'topic': topic,
                'queue_size': queue.size(),
                'in_flight_count': queue.get_in_flight_count(),
                'dead_letter_count': len(queue.get_dead_letter_messages()),
                'subscriber_count': len(self.subscribers.get(topic, []))
            }
```

### 2. Event Streaming System

```python
from typing import Generator

@dataclass
class StreamEvent:
    stream_id: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    sequence_number: int = 0
    partition_key: str = ""

class EventStream:
    """
    Event stream implementation similar to Kafka
    """

    def __init__(self, stream_name: str, partition_count: int = 4):
        self.stream_name = stream_name
        self.partition_count = partition_count
        self.partitions: List[List[StreamEvent]] = [[] for _ in range(partition_count)]
        self.sequence_numbers: List[int] = [0] * partition_count
        self.consumer_offsets: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self.lock = threading.RLock()

    def _get_partition(self, partition_key: str) -> int:
        """Get partition number for given key"""
        return hash(partition_key) % self.partition_count

    def append(self, event: StreamEvent) -> bool:
        """Append event to stream"""
        with self.lock:
            partition = self._get_partition(event.partition_key or event.stream_id)
            event.sequence_number = self.sequence_numbers[partition]

            self.partitions[partition].append(event)
            self.sequence_numbers[partition] += 1
            return True

    def read(self, consumer_group: str, from_offset: int = 0,
             partition: int = None) -> Generator[StreamEvent, None, None]:
        """Read events from stream"""
        partitions_to_read = [partition] if partition is not None else range(self.partition_count)

        for part_num in partitions_to_read:
            with self.lock:
                current_offset = self.consumer_offsets[consumer_group][part_num]
                start_offset = max(current_offset, from_offset)

                for i in range(start_offset, len(self.partitions[part_num])):
                    event = self.partitions[part_num][i]
                    yield event
                    self.consumer_offsets[consumer_group][part_num] = i + 1

    def get_latest_offset(self, partition: int = None) -> Dict[int, int]:
        """Get latest offset for partitions"""
        with self.lock:
            if partition is not None:
                return {partition: len(self.partitions[partition])}
            return {i: len(self.partitions[i]) for i in range(self.partition_count)}

    def commit_offset(self, consumer_group: str, partition: int, offset: int):
        """Commit consumer offset"""
        with self.lock:
            self.consumer_offsets[consumer_group][partition] = offset

    def get_stream_info(self) -> Dict[str, Any]:
        """Get stream information"""
        with self.lock:
            return {
                'stream_name': self.stream_name,
                'partition_count': self.partition_count,
                'total_events': sum(len(partition) for partition in self.partitions),
                'partition_sizes': [len(partition) for partition in self.partitions],
                'consumer_groups': dict(self.consumer_offsets)
            }

class EventStreamProcessor:
    """
    Stream processor for real-time event processing
    """

    def __init__(self, stream: EventStream, consumer_group: str):
        self.stream = stream
        self.consumer_group = consumer_group
        self.processors: List[Callable[[StreamEvent], None]] = []
        self.running = False
        self.worker_threads = []

    def add_processor(self, processor: Callable[[StreamEvent], None]):
        """Add event processor function"""
        self.processors.append(processor)

    def start(self, num_workers: int = 2):
        """Start processing events"""
        self.running = True

        for i in range(num_workers):
            worker = threading.Thread(
                target=self._process_events,
                args=(i,),
                daemon=True
            )
            worker.start()
            self.worker_threads.append(worker)

    def stop(self):
        """Stop processing events"""
        self.running = False
        for worker in self.worker_threads:
            worker.join()

    def _process_events(self, worker_id: int):
        """Worker thread to process events"""
        while self.running:
            try:
                for event in self.stream.read(self.consumer_group):
                    if not self.running:
                        break

                    for processor in self.processors:
                        try:
                            processor(event)
                        except Exception as e:
                            print(f"Error processing event {event.event_id}: {e}")

                time.sleep(0.1)  # Prevent busy waiting

            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
                time.sleep(1)
```

### 3. Reliable Message Processing Patterns

```python
class MessageProcessor:
    """
    Reliable message processor with various processing patterns
    """

    def __init__(self, queue: MessageQueue):
        self.queue = queue
        self.processors: Dict[str, Callable[[Message], bool]] = {}
        self.running = False
        self.workers = []
        self.metrics = {
            'processed': 0,
            'failed': 0,
            'retried': 0
        }

    def register_processor(self, message_type: str, processor: Callable[[Message], bool]):
        """Register processor for specific message type"""
        self.processors[message_type] = processor

    def start_workers(self, num_workers: int = 4):
        """Start worker threads to process messages"""
        self.running = True

        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(f"worker-{i}",),
                daemon=True
            )
            worker.start()
            self.workers.append(worker)

    def stop_workers(self):
        """Stop all worker threads"""
        self.running = False
        for worker in self.workers:
            worker.join()

    def _worker_loop(self, worker_name: str):
        """Main worker loop to process messages"""
        while self.running:
            try:
                message = self.queue.receive(timeout=1.0)
                if message is None:
                    continue

                success = self._process_message(message)

                if success:
                    self.queue.ack(message.id)
                    self.metrics['processed'] += 1
                else:
                    self.queue.nack(message.id, requeue=True)
                    self.metrics['failed'] += 1
                    if message.retry_count > 0:
                        self.metrics['retried'] += 1

            except Exception as e:
                print(f"Worker {worker_name} error: {e}")
                time.sleep(1)

    def _process_message(self, message: Message) -> bool:
        """Process individual message"""
        message_type = message.headers.get('type', 'default')

        if message_type not in self.processors:
            print(f"No processor for message type: {message_type}")
            return False

        try:
            return self.processors[message_type](message)
        except Exception as e:
            print(f"Error processing message {message.id}: {e}")
            return False

# Batch processing pattern
class BatchMessageProcessor:
    """
    Process messages in batches for efficiency
    """

    def __init__(self, queue: MessageQueue, batch_size: int = 10, batch_timeout: float = 5.0):
        self.queue = queue
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.running = False

    def start_batch_processing(self, processor: Callable[[List[Message]], List[bool]]):
        """Start batch processing with given processor function"""
        self.running = True

        def batch_worker():
            batch = []
            last_batch_time = time.time()

            while self.running:
                # Collect messages for batch
                message = self.queue.receive(timeout=0.1)

                if message:
                    batch.append(message)

                # Process batch if full or timeout reached
                current_time = time.time()
                should_process = (
                    len(batch) >= self.batch_size or
                    (batch and current_time - last_batch_time >= self.batch_timeout)
                )

                if should_process and batch:
                    try:
                        results = processor(batch)

                        # ACK/NACK based on results
                        for i, message in enumerate(batch):
                            if i < len(results) and results[i]:
                                self.queue.ack(message.id)
                            else:
                                self.queue.nack(message.id, requeue=True)

                    except Exception as e:
                        print(f"Batch processing error: {e}")
                        # NACK all messages in batch
                        for message in batch:
                            self.queue.nack(message.id, requeue=True)

                    batch = []
                    last_batch_time = current_time

        thread = threading.Thread(target=batch_worker, daemon=True)
        thread.start()
        return thread

    def stop(self):
        """Stop batch processing"""
        self.running = False

# Circuit breaker pattern for message processing
class CircuitBreakerMessageProcessor:
    """
    Message processor with circuit breaker pattern for fault tolerance
    """

    def __init__(self, queue: MessageQueue, failure_threshold: int = 5, timeout: int = 30):
        self.queue = queue
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def process_with_circuit_breaker(self, processor: Callable[[Message], bool]) -> bool:
        """Process message with circuit breaker protection"""
        message = self.queue.receive(timeout=1.0)
        if not message:
            return False

        # Check circuit breaker state
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
            else:
                # Circuit is open, reject message
                self.queue.nack(message.id, requeue=True)
                return False

        try:
            success = processor(message)

            if success:
                self.queue.ack(message.id)
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                return True
            else:
                self._handle_failure()
                self.queue.nack(message.id, requeue=True)
                return False

        except Exception as e:
            print(f"Processing error: {e}")
            self._handle_failure()
            self.queue.nack(message.id, requeue=True)
            return False

    def _handle_failure(self):
        """Handle processing failure"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            print(f"Circuit breaker opened due to {self.failure_count} failures")
```

## 📊 Message Queue Patterns and Use Cases

### 1. Work Queue Pattern

```python
# Example: Image processing work queue
def setup_image_processing_queue():
    """Setup work queue for image processing tasks"""
    broker = TopicBasedMessageBroker()
    broker.create_topic("image_processing")

    # Image processor
    def process_image(message: Message):
        image_url = message.body.get('image_url')
        processing_type = message.body.get('type', 'resize')

        print(f"Processing image: {image_url} with type: {processing_type}")

        # Simulate image processing
        time.sleep(2)

        # Simulate occasional failures
        import random
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("Image processing failed")

        print(f"Successfully processed image: {image_url}")
        return True

    # Setup processor
    processor = MessageProcessor(broker.topics["image_processing"])
    processor.register_processor("image_resize", lambda msg: process_image(msg))
    processor.start_workers(num_workers=3)

    return broker, processor

# Usage
broker, processor = setup_image_processing_queue()

# Send image processing tasks
for i in range(10):
    message = Message(
        body={
            'image_url': f'https://example.com/image_{i}.jpg',
            'type': 'resize',
            'width': 800,
            'height': 600
        },
        headers={'type': 'image_resize'},
        priority=MessagePriority.NORMAL
    )
    broker.publish("image_processing", message)
```

### 2. Publish-Subscribe Pattern

```python
# Example: User activity event system
def setup_user_activity_events():
    """Setup pub-sub system for user activity events"""
    broker = TopicBasedMessageBroker()

    # Analytics subscriber
    def analytics_handler(message: Message):
        event_type = message.body.get('event_type')
        user_id = message.body.get('user_id')
        print(f"Analytics: Recording {event_type} for user {user_id}")

    # Notification subscriber
    def notification_handler(message: Message):
        event_type = message.body.get('event_type')
        if event_type in ['login', 'purchase']:
            user_id = message.body.get('user_id')
            print(f"Notification: Sending welcome/thank you to user {user_id}")

    # Subscribe to user events
    broker.subscribe("user_events", analytics_handler)
    broker.subscribe("user_events", notification_handler)

    return broker

# Usage
broker = setup_user_activity_events()

# Publish user events
events = [
    {'event_type': 'login', 'user_id': 'user123'},
    {'event_type': 'view_product', 'user_id': 'user123', 'product_id': 'prod456'},
    {'event_type': 'purchase', 'user_id': 'user123', 'amount': 99.99}
]

for event in events:
    message = Message(body=event, headers={'type': 'user_activity'})
    broker.publish("user_events", message)
```

### 3. Event Sourcing Pattern

```python
# Example: Order event sourcing
class OrderEventStore:
    """Event store for order events"""

    def __init__(self):
        self.stream = EventStream("orders", partition_count=4)

    def create_order(self, order_id: str, customer_id: str, items: List[Dict]):
        """Create order event"""
        event = StreamEvent(
            stream_id="orders",
            event_type="order_created",
            data={
                'order_id': order_id,
                'customer_id': customer_id,
                'items': items,
                'status': 'pending'
            },
            partition_key=order_id
        )
        self.stream.append(event)

    def update_order_status(self, order_id: str, status: str):
        """Update order status event"""
        event = StreamEvent(
            stream_id="orders",
            event_type="order_status_updated",
            data={
                'order_id': order_id,
                'status': status
            },
            partition_key=order_id
        )
        self.stream.append(event)

    def add_payment(self, order_id: str, payment_method: str, amount: float):
        """Add payment event"""
        event = StreamEvent(
            stream_id="orders",
            event_type="payment_added",
            data={
                'order_id': order_id,
                'payment_method': payment_method,
                'amount': amount
            },
            partition_key=order_id
        )
        self.stream.append(event)

    def get_order_history(self, order_id: str) -> List[StreamEvent]:
        """Get all events for an order"""
        events = []
        for event in self.stream.read("order_reader"):
            if event.data.get('order_id') == order_id:
                events.append(event)
        return events

    def rebuild_order_state(self, order_id: str) -> Dict:
        """Rebuild order state from events"""
        order_state = {}
        events = self.get_order_history(order_id)

        for event in sorted(events, key=lambda e: e.sequence_number):
            if event.event_type == "order_created":
                order_state.update(event.data)
            elif event.event_type == "order_status_updated":
                order_state['status'] = event.data['status']
            elif event.event_type == "payment_added":
                if 'payments' not in order_state:
                    order_state['payments'] = []
                order_state['payments'].append({
                    'method': event.data['payment_method'],
                    'amount': event.data['amount']
                })

        return order_state

# Usage
order_store = OrderEventStore()

# Create and update order
order_store.create_order("order123", "customer456", [
    {'product': 'laptop', 'price': 999.99},
    {'product': 'mouse', 'price': 29.99}
])

order_store.update_order_status("order123", "confirmed")
order_store.add_payment("order123", "credit_card", 1029.98)
order_store.update_order_status("order123", "shipped")

# Rebuild order state
final_state = order_store.rebuild_order_state("order123")
print("Final order state:", json.dumps(final_state, indent=2))
```

## 🔧 Message Queue Technologies Comparison

### Popular Message Queue Systems

```python
@dataclass
class MessageQueueComparison:
    """
    Comparison of popular message queue technologies
    """
    name: str
    type: str  # queue, stream, pub_sub
    throughput: str  # messages/second
    latency: str
    durability: bool
    ordering_guarantee: str
    use_cases: List[str]

message_queue_technologies = [
    MessageQueueComparison(
        name="Apache Kafka",
        type="stream",
        throughput="2M+ msg/sec",
        latency="2-5ms",
        durability=True,
        ordering_guarantee="Per partition",
        use_cases=["Event streaming", "Log aggregation", "Real-time analytics"]
    ),
    MessageQueueComparison(
        name="RabbitMQ",
        type="queue",
        throughput="50K msg/sec",
        latency="<1ms",
        durability=True,
        ordering_guarantee="FIFO per queue",
        use_cases=["Task queues", "RPC", "Workflow orchestration"]
    ),
    MessageQueueComparison(
        name="Amazon SQS",
        type="queue",
        throughput="300K msg/sec",
        latency="10-20ms",
        durability=True,
        ordering_guarantee="FIFO queues available",
        use_cases=["Microservices decoupling", "Batch processing"]
    ),
    MessageQueueComparison(
        name="Redis Pub/Sub",
        type="pub_sub",
        throughput="1M+ msg/sec",
        latency="<1ms",
        durability=False,
        ordering_guarantee="None",
        use_cases=["Real-time notifications", "Chat applications"]
    ),
    MessageQueueComparison(
        name="Apache Pulsar",
        type="stream",
        throughput="1M+ msg/sec",
        latency="5-10ms",
        durability=True,
        ordering_guarantee="Per partition",
        use_cases=["Event streaming", "Message queuing", "Functions"]
    )
]

def compare_message_queues():
    """Print comparison table of message queue technologies"""
    print("MESSAGE QUEUE TECHNOLOGY COMPARISON")
    print("=" * 80)
    print(f"{'Name':<15} {'Type':<8} {'Throughput':<12} {'Latency':<8} {'Durable':<8} {'Ordering':<15}")
    print("-" * 80)

    for mq in message_queue_technologies:
        print(f"{mq.name:<15} {mq.type:<8} {mq.throughput:<12} {mq.latency:<8} "
              f"{str(mq.durability):<8} {mq.ordering_guarantee:<15}")

    print("\nUSE CASES:")
    for mq in message_queue_technologies:
        print(f"\n{mq.name}:")
        for use_case in mq.use_cases:
            print(f"  - {use_case}")

compare_message_queues()
```

## 📈 Monitoring and Metrics

```python
class MessageQueueMetrics:
    """
    Comprehensive metrics collection for message queues
    """

    def __init__(self):
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'messages_acked': 0,
            'messages_nacked': 0,
            'messages_dead_letter': 0,
            'processing_time_total': 0.0,
            'error_count': 0
        }
        self.start_time = time.time()

    def record_message_sent(self):
        self.metrics['messages_sent'] += 1

    def record_message_received(self):
        self.metrics['messages_received'] += 1

    def record_message_acked(self, processing_time: float):
        self.metrics['messages_acked'] += 1
        self.metrics['processing_time_total'] += processing_time

    def record_message_nacked(self):
        self.metrics['messages_nacked'] += 1

    def record_dead_letter(self):
        self.metrics['messages_dead_letter'] += 1

    def record_error(self):
        self.metrics['error_count'] += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        uptime = time.time() - self.start_time
        messages_processed = self.metrics['messages_acked']

        return {
            'uptime_seconds': round(uptime, 2),
            'messages_sent': self.metrics['messages_sent'],
            'messages_received': self.metrics['messages_received'],
            'messages_processed': messages_processed,
            'messages_failed': self.metrics['messages_nacked'],
            'dead_letter_count': self.metrics['messages_dead_letter'],
            'error_count': self.metrics['error_count'],
            'throughput_msg_per_sec': round(messages_processed / uptime, 2) if uptime > 0 else 0,
            'avg_processing_time_ms': round(
                (self.metrics['processing_time_total'] / messages_processed) * 1000, 2
            ) if messages_processed > 0 else 0,
            'success_rate': round(
                (messages_processed / self.metrics['messages_received']) * 100, 2
            ) if self.metrics['messages_received'] > 0 else 0
        }

# Integration with message processor
class MonitoredMessageProcessor(MessageProcessor):
    """Message processor with metrics collection"""

    def __init__(self, queue: MessageQueue):
        super().__init__(queue)
        self.metrics = MessageQueueMetrics()

    def _process_message(self, message: Message) -> bool:
        """Process message with metrics collection"""
        start_time = time.time()
        self.metrics.record_message_received()

        try:
            success = super()._process_message(message)
            processing_time = time.time() - start_time

            if success:
                self.metrics.record_message_acked(processing_time)
            else:
                self.metrics.record_message_nacked()

            return success

        except Exception as e:
            self.metrics.record_error()
            raise e

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.get_summary()
```

## ✅ Best Practices

### 1. **Message Design**
- Keep messages small and focused
- Include correlation IDs for tracing
- Use versioned message schemas
- Implement idempotent message processing

### 2. **Reliability**
- Always acknowledge message processing
- Implement dead letter queues
- Use circuit breakers for fault tolerance
- Monitor queue depths and processing times

### 3. **Performance**
- Batch process messages when possible
- Use appropriate queue types for use case
- Implement backpressure mechanisms
- Optimize serialization/deserialization

### 4. **Scalability**
- Partition streams by key for parallel processing
- Use consumer groups for load balancing
- Implement auto-scaling based on queue depth
- Consider sharding for very high throughput

## 🎯 Common Use Cases

### 1. **Microservices Communication**
- Async communication between services
- Event-driven architecture
- Service decoupling

### 2. **Data Processing Pipelines**
- ETL workflows
- Stream processing
- Batch job orchestration

### 3. **Real-time Applications**
- Chat applications
- Live notifications
- Gaming leaderboards

### 4. **System Integration**
- Legacy system integration
- API rate limiting
- Data synchronization

## ✅ Key Takeaways

1. **Choose the Right Tool**: Match queue type to use case
2. **Design for Reliability**: Always handle failures gracefully
3. **Monitor Everything**: Track metrics and set up alerting
4. **Plan for Scale**: Consider partitioning and load balancing
5. **Test Failure Scenarios**: Ensure system handles edge cases
6. **Optimize for Latency vs Throughput**: Based on requirements

## 🚀 Next Steps

- Study [Monitoring and Observability](../monitoring/)
- Learn [Caching Strategies](../caching/)
- Practice [System Design Interviews](../../05-interview-preparation/)
- Explore [Advanced Performance Tuning](../../07-advanced-topics/performance-tuning/)