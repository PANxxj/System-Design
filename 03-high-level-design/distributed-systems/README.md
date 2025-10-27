# Distributed Systems Fundamentals 🔴

## 🎯 Learning Objectives
- Understand distributed systems principles and challenges
- Master consistency, availability, and partition tolerance (CAP theorem)
- Learn consensus algorithms and distributed coordination
- Implement fault tolerance and resilience patterns

## 📋 Distributed Systems Overview

Distributed systems are collections of independent computers that appear to users as a single coherent system. They enable scalability, fault tolerance, and geographic distribution but introduce complexity around consistency, coordination, and failure handling.

## 🔧 Core Concepts and Implementation

### 1. CAP Theorem Implementation

```python
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import time
import threading
import random
import json
import hashlib
from abc import ABC, abstractmethod

class NodeState(Enum):
    HEALTHY = "healthy"
    PARTITIONED = "partitioned"
    FAILED = "failed"

class ConsistencyLevel(Enum):
    EVENTUAL = "eventual"
    STRONG = "strong"
    WEAK = "weak"

@dataclass
class DataRecord:
    key: str
    value: str
    version: int = 1
    timestamp: float = field(default_factory=time.time)
    node_id: str = ""

@dataclass
class WriteRequest:
    key: str
    value: str
    consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL
    timeout: float = 5.0

@dataclass
class ReadRequest:
    key: str
    consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL
    timeout: float = 5.0

class DistributedNode:
    """
    A node in a distributed system implementing CAP theorem trade-offs
    """

    def __init__(self, node_id: str, initial_data: Dict[str, str] = None):
        self.node_id = node_id
        self.state = NodeState.HEALTHY
        self.data: Dict[str, DataRecord] = {}
        self.peers: Set['DistributedNode'] = set()
        self.vector_clock: Dict[str, int] = {}
        self.lock = threading.RLock()

        # Initialize with data
        if initial_data:
            for key, value in initial_data.items():
                self.data[key] = DataRecord(key, value, 1, time.time(), node_id)

        # Network simulation
        self.network_delay = 0.1  # 100ms default
        self.failure_probability = 0.01  # 1% chance of failure

    def add_peer(self, peer: 'DistributedNode'):
        """Add peer node"""
        with self.lock:
            self.peers.add(peer)
            peer.peers.add(self)
            # Initialize vector clock entry
            self.vector_clock[peer.node_id] = 0
            peer.vector_clock[self.node_id] = 0

    def simulate_network_partition(self, partitioned_peers: Set['DistributedNode']):
        """Simulate network partition"""
        with self.lock:
            self.state = NodeState.PARTITIONED
            # Remove partitioned peers temporarily
            for peer in partitioned_peers:
                if peer in self.peers:
                    self.peers.discard(peer)

    def heal_partition(self, healed_peers: Set['DistributedNode']):
        """Heal network partition"""
        with self.lock:
            self.state = NodeState.HEALTHY
            # Re-add healed peers
            for peer in healed_peers:
                self.peers.add(peer)

    def write(self, request: WriteRequest) -> Tuple[bool, str]:
        """
        Write data with specified consistency level
        """
        with self.lock:
            if self.state == NodeState.FAILED:
                return False, "Node failed"

            # Update vector clock
            self.vector_clock[self.node_id] = self.vector_clock.get(self.node_id, 0) + 1

            # Create record
            record = DataRecord(
                key=request.key,
                value=request.value,
                version=self._get_next_version(request.key),
                timestamp=time.time(),
                node_id=self.node_id
            )

            if request.consistency_level == ConsistencyLevel.WEAK:
                # Just write locally
                self.data[request.key] = record
                return True, "Written locally"

            elif request.consistency_level == ConsistencyLevel.EVENTUAL:
                # Write locally, then propagate asynchronously
                self.data[request.key] = record
                self._propagate_write_async(record)
                return True, "Written with eventual consistency"

            elif request.consistency_level == ConsistencyLevel.STRONG:
                # Write to majority of nodes (including self)
                return self._write_with_consensus(record, request.timeout)

    def read(self, request: ReadRequest) -> Tuple[bool, Optional[DataRecord], str]:
        """
        Read data with specified consistency level
        """
        with self.lock:
            if self.state == NodeState.FAILED:
                return False, None, "Node failed"

            if request.consistency_level == ConsistencyLevel.WEAK:
                # Just read locally
                record = self.data.get(request.key)
                return True, record, "Read locally"

            elif request.consistency_level == ConsistencyLevel.EVENTUAL:
                # Read locally (may be stale)
                record = self.data.get(request.key)
                return True, record, "Read with eventual consistency"

            elif request.consistency_level == ConsistencyLevel.STRONG:
                # Read from majority to ensure latest value
                return self._read_with_consensus(request.key, request.timeout)

    def _get_next_version(self, key: str) -> int:
        """Get next version number for key"""
        if key in self.data:
            return self.data[key].version + 1
        return 1

    def _propagate_write_async(self, record: DataRecord):
        """Asynchronously propagate write to peers"""
        def propagate():
            time.sleep(self.network_delay)  # Simulate network delay

            for peer in list(self.peers):  # Copy to avoid modification during iteration
                if random.random() > self.failure_probability:
                    try:
                        peer._receive_write(record, self.vector_clock.copy())
                    except Exception as e:
                        print(f"Failed to propagate to {peer.node_id}: {e}")

        thread = threading.Thread(target=propagate, daemon=True)
        thread.start()

    def _receive_write(self, record: DataRecord, sender_vector_clock: Dict[str, int]):
        """Receive write from peer"""
        with self.lock:
            if self.state == NodeState.FAILED:
                return

            # Update vector clock
            for node_id, clock_value in sender_vector_clock.items():
                self.vector_clock[node_id] = max(
                    self.vector_clock.get(node_id, 0),
                    clock_value
                )

            # Apply write if newer
            if (record.key not in self.data or
                self._is_newer_record(record, self.data[record.key])):
                self.data[record.key] = record

    def _is_newer_record(self, new_record: DataRecord, existing_record: DataRecord) -> bool:
        """Determine if new record is newer than existing"""
        # Use timestamp for simple ordering (in practice, use vector clocks)
        return new_record.timestamp > existing_record.timestamp

    def _write_with_consensus(self, record: DataRecord, timeout: float) -> Tuple[bool, str]:
        """Write with strong consistency using majority consensus"""
        start_time = time.time()
        available_peers = [peer for peer in self.peers if peer.state != NodeState.FAILED]
        total_nodes = len(available_peers) + 1  # Include self
        required_nodes = (total_nodes // 2) + 1  # Majority

        # Always include self
        successful_writes = 1
        self.data[record.key] = record

        # Attempt to write to peers
        for peer in available_peers:
            if time.time() - start_time > timeout:
                break

            try:
                # Simulate network delay
                time.sleep(self.network_delay)

                if random.random() > self.failure_probability:
                    peer._receive_write(record, self.vector_clock.copy())
                    successful_writes += 1

                    if successful_writes >= required_nodes:
                        return True, f"Written to {successful_writes}/{total_nodes} nodes"

            except Exception as e:
                continue

        if successful_writes >= required_nodes:
            return True, f"Written to {successful_writes}/{total_nodes} nodes"
        else:
            # Rollback local write if consensus failed
            if record.key in self.data and self.data[record.key] == record:
                del self.data[record.key]
            return False, f"Failed to achieve consensus ({successful_writes}/{required_nodes} required)"

    def _read_with_consensus(self, key: str, timeout: float) -> Tuple[bool, Optional[DataRecord], str]:
        """Read with strong consistency using majority consensus"""
        start_time = time.time()
        available_peers = [peer for peer in self.peers if peer.state != NodeState.FAILED]
        total_nodes = len(available_peers) + 1
        required_nodes = (total_nodes // 2) + 1

        # Collect reads from majority
        reads = []
        if key in self.data:
            reads.append(self.data[key])

        for peer in available_peers:
            if time.time() - start_time > timeout:
                break

            try:
                time.sleep(self.network_delay)

                if random.random() > self.failure_probability:
                    peer_record = peer.data.get(key)
                    if peer_record:
                        reads.append(peer_record)

                    if len(reads) >= required_nodes:
                        break

            except Exception:
                continue

        if len(reads) >= required_nodes:
            # Return the most recent record
            latest_record = max(reads, key=lambda r: r.timestamp)
            return True, latest_record, f"Read from {len(reads)}/{total_nodes} nodes"
        else:
            return False, None, f"Failed to read from majority ({len(reads)}/{required_nodes} required)"

    def get_status(self) -> Dict:
        """Get node status"""
        with self.lock:
            return {
                'node_id': self.node_id,
                'state': self.state.value,
                'data_count': len(self.data),
                'peer_count': len(self.peers),
                'vector_clock': self.vector_clock.copy()
            }
```

### 2. Consensus Algorithms - Raft Implementation

```python
import random
from enum import Enum

class RaftState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class LogEntry:
    term: int
    index: int
    command: str
    data: Dict[str, any] = field(default_factory=dict)
    committed: bool = False

@dataclass
class VoteRequest:
    term: int
    candidate_id: str
    last_log_index: int
    last_log_term: int

@dataclass
class VoteResponse:
    term: int
    vote_granted: bool

@dataclass
class AppendEntriesRequest:
    term: int
    leader_id: str
    prev_log_index: int
    prev_log_term: int
    entries: List[LogEntry]
    leader_commit: int

@dataclass
class AppendEntriesResponse:
    term: int
    success: bool
    match_index: int

class RaftNode:
    """
    Raft consensus algorithm implementation
    """

    def __init__(self, node_id: str, peers: List[str]):
        # Persistent state
        self.node_id = node_id
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []

        # Volatile state
        self.commit_index = 0
        self.last_applied = 0
        self.state = RaftState.FOLLOWER

        # Leader state
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}

        # Configuration
        self.peers = set(peers)
        self.election_timeout = random.uniform(5.0, 10.0)  # seconds
        self.heartbeat_interval = 2.0  # seconds

        # Runtime state
        self.last_heartbeat = time.time()
        self.votes_received = set()
        self.running = True
        self.lock = threading.RLock()

        # State machine
        self.state_machine: Dict[str, any] = {}

        # Start background thread
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        """Main Raft algorithm loop"""
        while self.running:
            with self.lock:
                if self.state == RaftState.FOLLOWER:
                    self._run_follower()
                elif self.state == RaftState.CANDIDATE:
                    self._run_candidate()
                elif self.state == RaftState.LEADER:
                    self._run_leader()

            time.sleep(0.1)  # Small delay to prevent busy waiting

    def _run_follower(self):
        """Follower state behavior"""
        if time.time() - self.last_heartbeat > self.election_timeout:
            # Start election
            self._become_candidate()

    def _run_candidate(self):
        """Candidate state behavior"""
        # Start election
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        self.last_heartbeat = time.time()

        # Request votes from peers
        self._request_votes()

        # Check if won election
        if len(self.votes_received) > len(self.peers) // 2:
            self._become_leader()
        elif time.time() - self.last_heartbeat > self.election_timeout:
            # Election timeout, restart
            self._become_candidate()

    def _run_leader(self):
        """Leader state behavior"""
        # Send heartbeats
        if time.time() - self.last_heartbeat > self.heartbeat_interval:
            self._send_heartbeats()
            self.last_heartbeat = time.time()

    def _become_candidate(self):
        """Transition to candidate state"""
        self.state = RaftState.CANDIDATE
        print(f"Node {self.node_id} became candidate for term {self.current_term + 1}")

    def _become_leader(self):
        """Transition to leader state"""
        self.state = RaftState.LEADER
        print(f"Node {self.node_id} became leader for term {self.current_term}")

        # Initialize leader state
        for peer in self.peers:
            self.next_index[peer] = len(self.log)
            self.match_index[peer] = 0

    def _become_follower(self, term: int):
        """Transition to follower state"""
        self.state = RaftState.FOLLOWER
        self.current_term = term
        self.voted_for = None
        self.votes_received.clear()
        print(f"Node {self.node_id} became follower for term {term}")

    def _request_votes(self):
        """Request votes from all peers"""
        vote_request = VoteRequest(
            term=self.current_term,
            candidate_id=self.node_id,
            last_log_index=len(self.log) - 1 if self.log else -1,
            last_log_term=self.log[-1].term if self.log else 0
        )

        # In real implementation, send over network
        # For simulation, we'll just count votes based on probability
        for peer in self.peers:
            if random.random() > 0.3:  # 70% chance of getting vote
                self.votes_received.add(peer)

    def _send_heartbeats(self):
        """Send heartbeat/append entries to all peers"""
        for peer in self.peers:
            prev_log_index = self.next_index[peer] - 1
            prev_log_term = self.log[prev_log_index].term if prev_log_index >= 0 else 0

            request = AppendEntriesRequest(
                term=self.current_term,
                leader_id=self.node_id,
                prev_log_index=prev_log_index,
                prev_log_term=prev_log_term,
                entries=[],  # Heartbeat - no entries
                leader_commit=self.commit_index
            )

            # Simulate network success/failure
            if random.random() > 0.1:  # 90% success rate
                self._handle_append_entries_response(peer, AppendEntriesResponse(
                    term=self.current_term,
                    success=True,
                    match_index=prev_log_index
                ))

    def append_entry(self, command: str, data: Dict[str, any] = None) -> bool:
        """Append new entry to log (only for leader)"""
        with self.lock:
            if self.state != RaftState.LEADER:
                return False

            entry = LogEntry(
                term=self.current_term,
                index=len(self.log),
                command=command,
                data=data or {}
            )

            self.log.append(entry)
            print(f"Leader {self.node_id} appended entry: {command}")

            # Replicate to peers
            self._replicate_log()
            return True

    def _replicate_log(self):
        """Replicate log entries to peers"""
        for peer in self.peers:
            # Send entries starting from next_index
            entries_to_send = self.log[self.next_index[peer]:]

            if entries_to_send:
                print(f"Replicating {len(entries_to_send)} entries to {peer}")
                # In real implementation, send over network
                # Simulate successful replication
                if random.random() > 0.2:  # 80% success rate
                    self.match_index[peer] = len(self.log) - 1
                    self.next_index[peer] = len(self.log)

        # Update commit index
        self._update_commit_index()

    def _update_commit_index(self):
        """Update commit index based on majority replication"""
        for i in range(self.commit_index + 1, len(self.log)):
            replicated_count = 1  # Count self

            for peer in self.peers:
                if self.match_index.get(peer, 0) >= i:
                    replicated_count += 1

            # If majority has replicated this entry
            if replicated_count > len(self.peers) // 2:
                self.commit_index = i
                self._apply_committed_entries()

    def _apply_committed_entries(self):
        """Apply committed entries to state machine"""
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied]

            # Apply to state machine
            if entry.command == "set":
                key = entry.data.get("key")
                value = entry.data.get("value")
                if key:
                    self.state_machine[key] = value
                    print(f"Applied to state machine: {key} = {value}")

    def get_state_machine(self) -> Dict[str, any]:
        """Get current state machine state"""
        with self.lock:
            return self.state_machine.copy()

    def get_status(self) -> Dict[str, any]:
        """Get node status"""
        with self.lock:
            return {
                'node_id': self.node_id,
                'state': self.state.value,
                'current_term': self.current_term,
                'log_length': len(self.log),
                'commit_index': self.commit_index,
                'last_applied': self.last_applied,
                'state_machine_size': len(self.state_machine)
            }
```

### 3. Vector Clocks for Distributed Ordering

```python
class VectorClock:
    """
    Vector clock implementation for distributed event ordering
    """

    def __init__(self, node_id: str, nodes: List[str]):
        self.node_id = node_id
        self.clock = {node: 0 for node in nodes}

    def tick(self):
        """Increment local clock"""
        self.clock[self.node_id] += 1

    def update(self, other_clock: Dict[str, int]):
        """Update clock with received clock"""
        for node in self.clock:
            if node in other_clock:
                self.clock[node] = max(self.clock[node], other_clock[node])

        # Increment local clock
        self.tick()

    def compare(self, other_clock: Dict[str, int]) -> str:
        """Compare two vector clocks"""
        self_greater = False
        other_greater = False

        for node in self.clock:
            if node in other_clock:
                if self.clock[node] > other_clock[node]:
                    self_greater = True
                elif self.clock[node] < other_clock[node]:
                    other_greater = True

        if self_greater and not other_greater:
            return "greater"
        elif other_greater and not self_greater:
            return "less"
        elif not self_greater and not other_greater:
            return "equal"
        else:
            return "concurrent"

    def happens_before(self, other_clock: Dict[str, int]) -> bool:
        """Check if this event happens before other event"""
        return self.compare(other_clock) == "less"

    def copy(self) -> Dict[str, int]:
        """Get copy of clock"""
        return self.clock.copy()

@dataclass
class DistributedEvent:
    event_id: str
    node_id: str
    event_type: str
    data: Dict[str, any]
    vector_clock: Dict[str, int]
    timestamp: float = field(default_factory=time.time)

class DistributedEventLogger:
    """
    Distributed event logger using vector clocks
    """

    def __init__(self, node_id: str, nodes: List[str]):
        self.node_id = node_id
        self.vector_clock = VectorClock(node_id, nodes)
        self.events: List[DistributedEvent] = []
        self.lock = threading.Lock()

    def log_event(self, event_type: str, data: Dict[str, any]) -> DistributedEvent:
        """Log local event"""
        with self.lock:
            self.vector_clock.tick()

            event = DistributedEvent(
                event_id=str(uuid.uuid4()),
                node_id=self.node_id,
                event_type=event_type,
                data=data,
                vector_clock=self.vector_clock.copy()
            )

            self.events.append(event)
            return event

    def receive_event(self, event: DistributedEvent):
        """Receive event from another node"""
        with self.lock:
            self.vector_clock.update(event.vector_clock)
            self.events.append(event)

    def get_causal_history(self, target_event: DistributedEvent) -> List[DistributedEvent]:
        """Get all events that causally precede target event"""
        causal_events = []

        for event in self.events:
            if event == target_event:
                continue

            # Check if event happens before target
            target_vc = VectorClock(target_event.node_id, list(target_event.vector_clock.keys()))
            target_vc.clock = target_event.vector_clock.copy()

            if target_vc.happens_before(event.vector_clock):
                causal_events.append(event)

        return sorted(causal_events, key=lambda e: e.timestamp)

    def get_concurrent_events(self, event1: DistributedEvent, event2: DistributedEvent) -> bool:
        """Check if two events are concurrent"""
        vc1 = VectorClock(event1.node_id, list(event1.vector_clock.keys()))
        vc1.clock = event1.vector_clock.copy()

        return vc1.compare(event2.vector_clock) == "concurrent"
```

## 🔄 Fault Tolerance Patterns

### 1. Circuit Breaker Pattern

```python
class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """
    Circuit breaker for fault tolerance in distributed systems
    """

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitBreakerState.CLOSED
        self.lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time >= self.timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)

                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0

                return result

            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitBreakerState.OPEN

                raise e

    def get_state(self) -> Dict[str, any]:
        """Get circuit breaker state"""
        with self.lock:
            return {
                'state': self.state.value,
                'failure_count': self.failure_count,
                'failure_threshold': self.failure_threshold,
                'last_failure_time': self.last_failure_time
            }
```

### 2. Retry with Exponential Backoff

```python
import random

class RetryPolicy:
    """
    Retry policy with exponential backoff and jitter
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def execute(self, func, *args, **kwargs):
        """Execute function with retry policy"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt == self.max_retries:
                    break

                # Calculate delay with exponential backoff and jitter
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                jitter = random.uniform(0, delay * 0.1)  # 10% jitter
                total_delay = delay + jitter

                print(f"Attempt {attempt + 1} failed, retrying in {total_delay:.2f}s: {e}")
                time.sleep(total_delay)

        raise last_exception

# Example usage
def unreliable_operation():
    """Simulated unreliable operation"""
    if random.random() < 0.7:  # 70% failure rate
        raise Exception("Operation failed")
    return "Success"

retry_policy = RetryPolicy(max_retries=3, base_delay=1.0)
try:
    result = retry_policy.execute(unreliable_operation)
    print(f"Operation succeeded: {result}")
except Exception as e:
    print(f"Operation failed after all retries: {e}")
```

## 📊 Distributed System Testing

```python
class DistributedSystemSimulator:
    """
    Simulator for testing distributed system behaviors
    """

    def __init__(self):
        self.nodes: List[RaftNode] = []
        self.network_partitions: Set[Tuple[str, str]] = set()
        self.failed_nodes: Set[str] = set()

    def add_node(self, node_id: str, peers: List[str]) -> RaftNode:
        """Add node to cluster"""
        node = RaftNode(node_id, peers)
        self.nodes.append(node)
        return node

    def create_cluster(self, node_count: int) -> List[RaftNode]:
        """Create a cluster of nodes"""
        node_ids = [f"node_{i}" for i in range(node_count)]

        for i, node_id in enumerate(node_ids):
            peers = [nid for nid in node_ids if nid != node_id]
            self.add_node(node_id, peers)

        return self.nodes

    def simulate_network_partition(self, partition1: List[str], partition2: List[str]):
        """Simulate network partition between two groups"""
        for node1 in partition1:
            for node2 in partition2:
                self.network_partitions.add((node1, node2))
                self.network_partitions.add((node2, node1))

        print(f"Created network partition: {partition1} <-> {partition2}")

    def heal_network_partition(self):
        """Heal all network partitions"""
        self.network_partitions.clear()
        print("Healed all network partitions")

    def fail_node(self, node_id: str):
        """Simulate node failure"""
        self.failed_nodes.add(node_id)
        node = next((n for n in self.nodes if n.node_id == node_id), None)
        if node:
            node.running = False
        print(f"Failed node: {node_id}")

    def recover_node(self, node_id: str):
        """Recover failed node"""
        self.failed_nodes.discard(node_id)
        print(f"Recovered node: {node_id}")

    def get_cluster_status(self) -> Dict[str, any]:
        """Get status of entire cluster"""
        leaders = [n for n in self.nodes if n.state == RaftState.LEADER]
        followers = [n for n in self.nodes if n.state == RaftState.FOLLOWER]
        candidates = [n for n in self.nodes if n.state == RaftState.CANDIDATE]

        return {
            'total_nodes': len(self.nodes),
            'leaders': len(leaders),
            'followers': len(followers),
            'candidates': len(candidates),
            'failed_nodes': len(self.failed_nodes),
            'network_partitions': len(self.network_partitions),
            'leader_nodes': [n.node_id for n in leaders] if leaders else None
        }

    def run_simulation(self, duration: float = 30.0):
        """Run simulation for specified duration"""
        print(f"Starting distributed system simulation for {duration} seconds...")

        start_time = time.time()

        while time.time() - start_time < duration:
            # Random events
            if random.random() < 0.1:  # 10% chance
                if random.random() < 0.5:
                    # Create partition
                    if len(self.nodes) >= 3:
                        split_point = len(self.nodes) // 2
                        partition1 = [n.node_id for n in self.nodes[:split_point]]
                        partition2 = [n.node_id for n in self.nodes[split_point:]]
                        self.simulate_network_partition(partition1, partition2)
                else:
                    # Heal partition
                    self.heal_network_partition()

            # Print status
            status = self.get_cluster_status()
            print(f"Cluster status: {status}")

            time.sleep(5)

        print("Simulation completed")

# Example usage
def test_distributed_system():
    """Test distributed system with various failure scenarios"""
    simulator = DistributedSystemSimulator()

    # Create 5-node cluster
    nodes = simulator.create_cluster(5)

    # Let cluster stabilize
    time.sleep(5)

    # Try to append some entries
    for node in nodes:
        if node.state == RaftState.LEADER:
            node.append_entry("set", {"key": "test_key", "value": "test_value"})
            break

    # Run simulation
    simulator.run_simulation(20)

if __name__ == "__main__":
    test_distributed_system()
```

## ✅ Key Concepts Summary

### 1. **CAP Theorem**
- **Consistency**: All nodes see the same data simultaneously
- **Availability**: System remains operational
- **Partition Tolerance**: System continues despite network failures
- **Trade-offs**: Can only guarantee 2 out of 3 in presence of partitions

### 2. **Consensus Algorithms**
- **Raft**: Leader-based consensus with strong consistency
- **PBFT**: Byzantine fault tolerance for malicious failures
- **Paxos**: Complex but proven consensus algorithm

### 3. **Consistency Models**
- **Strong Consistency**: All reads receive most recent write
- **Eventual Consistency**: System will become consistent over time
- **Causal Consistency**: Causally related operations are ordered

### 4. **Fault Tolerance Patterns**
- **Circuit Breaker**: Prevent cascading failures
- **Retry with Backoff**: Handle transient failures
- **Bulkhead**: Isolate critical resources

## 🎯 Design Principles

### 1. **Design for Failure**
- Assume components will fail
- Implement graceful degradation
- Use redundancy and replication

### 2. **Loose Coupling**
- Minimize dependencies between components
- Use message queues for async communication
- Implement service discovery

### 3. **Observability**
- Comprehensive logging and metrics
- Distributed tracing
- Health checks and monitoring

### 4. **Scalability**
- Horizontal scaling over vertical
- Stateless service design
- Efficient load balancing

## ✅ Best Practices

1. **Start Simple**: Begin with single-node, add distribution gradually
2. **Test Failure Scenarios**: Use chaos engineering principles
3. **Monitor Everything**: Implement comprehensive observability
4. **Design for Eventual Consistency**: Avoid strong consistency unless required
5. **Use Proven Patterns**: Leverage established distributed system patterns
6. **Plan for Network Partitions**: Always consider partition scenarios

## 🚀 Next Steps

- Study [Scalability Patterns](../scalability-patterns/)
- Learn [Data Management](../data-management/) in distributed systems
- Practice with [Real-World Examples](../../04-real-world-examples/)
- Explore [Advanced Performance Tuning](../../07-advanced-topics/performance-tuning/)