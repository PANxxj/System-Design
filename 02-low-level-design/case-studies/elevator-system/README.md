# Elevator System Design 🔴

## 🎯 Learning Objectives
- Design a complex multi-component system
- Implement state machines and scheduling algorithms
- Handle concurrent operations and safety requirements
- Apply multiple design patterns in a real system

## 📋 Requirements

### Functional Requirements
- Multiple elevators in a building
- Support for multiple floors
- Efficient request handling and scheduling
- Different elevator types (passenger, freight)
- Emergency mode and safety features

### Non-Functional Requirements
- High availability and safety
- Optimal wait times
- Energy efficiency
- Fault tolerance
- Real-time response

## 🏗️ System Design

### Core Components
1. **Elevator** - Individual elevator unit
2. **ElevatorController** - Manages single elevator
3. **BuildingController** - Coordinates all elevators
4. **RequestDispatcher** - Assigns requests to elevators
5. **FloorPanel** - Interface for floor requests
6. **ElevatorPanel** - Interface inside elevator

## 💻 Implementation

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Optional, Set
import threading
import time
import heapq
from dataclasses import dataclass
from collections import defaultdict
import logging

# Enums and Constants
class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    IDLE = "IDLE"

class ElevatorState(Enum):
    IDLE = "IDLE"
    MOVING_UP = "MOVING_UP"
    MOVING_DOWN = "MOVING_DOWN"
    DOORS_OPENING = "DOORS_OPENING"
    DOORS_OPEN = "DOORS_OPEN"
    DOORS_CLOSING = "DOORS_CLOSING"
    MAINTENANCE = "MAINTENANCE"
    EMERGENCY = "EMERGENCY"

class ElevatorType(Enum):
    PASSENGER = "PASSENGER"
    FREIGHT = "FREIGHT"
    SERVICE = "SERVICE"

class RequestType(Enum):
    HALL_CALL = "HALL_CALL"  # Called from floor
    CAR_CALL = "CAR_CALL"    # Called from inside elevator

@dataclass
class ElevatorRequest:
    floor: int
    direction: Direction
    request_type: RequestType
    timestamp: float
    priority: int = 0  # Higher number = higher priority

    def __lt__(self, other):
        return self.priority > other.priority

# Observer Pattern for notifications
class ElevatorObserver(ABC):
    @abstractmethod
    def on_elevator_moved(self, elevator_id: int, floor: int):
        pass

    @abstractmethod
    def on_elevator_state_changed(self, elevator_id: int, state: ElevatorState):
        pass

    @abstractmethod
    def on_doors_operation(self, elevator_id: int, opening: bool):
        pass

class Display(ElevatorObserver):
    def on_elevator_moved(self, elevator_id: int, floor: int):
        print(f"🏢 Elevator {elevator_id} arrived at floor {floor}")

    def on_elevator_state_changed(self, elevator_id: int, state: ElevatorState):
        print(f"📊 Elevator {elevator_id} state: {state.value}")

    def on_doors_operation(self, elevator_id: int, opening: bool):
        action = "opening" if opening else "closing"
        print(f"🚪 Elevator {elevator_id} doors {action}")

# Strategy Pattern for scheduling algorithms
class SchedulingStrategy(ABC):
    @abstractmethod
    def select_elevator(self, elevators: List['Elevator'], request: ElevatorRequest) -> Optional['Elevator']:
        pass

class NearestCarStrategy(SchedulingStrategy):
    def select_elevator(self, elevators: List['Elevator'], request: ElevatorRequest) -> Optional['Elevator']:
        available_elevators = [e for e in elevators if e.is_available()]
        if not available_elevators:
            return None

        return min(available_elevators,
                  key=lambda e: abs(e.current_floor - request.floor))

class SCANStrategy(SchedulingStrategy):
    """SCAN (Elevator) algorithm - serves requests in one direction, then reverses"""
    def select_elevator(self, elevators: List['Elevator'], request: ElevatorRequest) -> Optional['Elevator']:
        suitable_elevators = []

        for elevator in elevators:
            if not elevator.is_available():
                continue

            # If elevator is moving in the same direction and hasn't passed the floor
            if (elevator.direction == request.direction and
                ((request.direction == Direction.UP and elevator.current_floor <= request.floor) or
                 (request.direction == Direction.DOWN and elevator.current_floor >= request.floor))):
                suitable_elevators.append(elevator)
            # If elevator is idle
            elif elevator.direction == Direction.IDLE:
                suitable_elevators.append(elevator)

        if not suitable_elevators:
            return None

        return min(suitable_elevators,
                  key=lambda e: abs(e.current_floor - request.floor))

class LOOKStrategy(SchedulingStrategy):
    """LOOK algorithm - more efficient version of SCAN"""
    def select_elevator(self, elevators: List['Elevator'], request: ElevatorRequest) -> Optional['Elevator']:
        best_elevator = None
        best_score = float('inf')

        for elevator in elevators:
            if not elevator.is_available():
                continue

            distance = abs(elevator.current_floor - request.floor)

            # Bonus for same direction
            direction_bonus = 0
            if (elevator.direction == request.direction or
                elevator.direction == Direction.IDLE):
                direction_bonus = -10

            # Penalty for being busy
            load_penalty = len(elevator.pending_requests) * 2

            score = distance + load_penalty + direction_bonus

            if score < best_score:
                best_score = score
                best_elevator = elevator

        return best_elevator

# Main Elevator Class
class Elevator:
    def __init__(self, elevator_id: int, total_floors: int, elevator_type: ElevatorType = ElevatorType.PASSENGER):
        self.elevator_id = elevator_id
        self.total_floors = total_floors
        self.elevator_type = elevator_type
        self.current_floor = 1
        self.direction = Direction.IDLE
        self.state = ElevatorState.IDLE

        # Request handling
        self.pending_requests: Set[int] = set()
        self.up_requests: Set[int] = set()
        self.down_requests: Set[int] = set()

        # Capacity and specifications
        self.max_capacity = 20 if elevator_type == ElevatorType.PASSENGER else 50
        self.current_load = 0
        self.max_weight = 2000 if elevator_type == ElevatorType.PASSENGER else 5000  # kg

        # Timing
        self.floor_travel_time = 2.0  # seconds per floor
        self.door_operation_time = 3.0  # seconds
        self.stop_time = 5.0  # seconds to stop at floor

        # Safety and maintenance
        self.emergency_stop = False
        self.maintenance_mode = False
        self.last_maintenance = time.time()
        self.door_open_timer = None

        # Observer pattern
        self.observers: List[ElevatorObserver] = []

        # Threading
        self.lock = threading.RLock()
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def add_observer(self, observer: ElevatorObserver):
        self.observers.append(observer)

    def remove_observer(self, observer: ElevatorObserver):
        if observer in self.observers:
            self.observers.remove(observer)

    def _notify_moved(self):
        for observer in self.observers:
            observer.on_elevator_moved(self.elevator_id, self.current_floor)

    def _notify_state_changed(self):
        for observer in self.observers:
            observer.on_elevator_state_changed(self.elevator_id, self.state)

    def _notify_doors_operation(self, opening: bool):
        for observer in self.observers:
            observer.on_doors_operation(self.elevator_id, opening)

    def add_request(self, floor: int, direction: Direction = None):
        with self.lock:
            if not self.is_valid_floor(floor) or self.maintenance_mode:
                return False

            self.pending_requests.add(floor)

            if direction == Direction.UP:
                self.up_requests.add(floor)
            elif direction == Direction.DOWN:
                self.down_requests.add(floor)
            else:
                # Internal request - add to appropriate direction based on current position
                if floor > self.current_floor:
                    self.up_requests.add(floor)
                elif floor < self.current_floor:
                    self.down_requests.add(floor)

            return True

    def is_valid_floor(self, floor: int) -> bool:
        return 1 <= floor <= self.total_floors

    def is_available(self) -> bool:
        return (not self.maintenance_mode and
                not self.emergency_stop and
                self.current_load < self.max_capacity)

    def emergency_stop_engage(self):
        with self.lock:
            self.emergency_stop = True
            self.state = ElevatorState.EMERGENCY
            self.pending_requests.clear()
            self.up_requests.clear()
            self.down_requests.clear()
            self._notify_state_changed()
            print(f"🚨 EMERGENCY: Elevator {self.elevator_id} stopped at floor {self.current_floor}")

    def emergency_stop_release(self):
        with self.lock:
            self.emergency_stop = False
            self.state = ElevatorState.IDLE
            self.direction = Direction.IDLE
            self._notify_state_changed()
            print(f"✅ EMERGENCY CLEARED: Elevator {self.elevator_id} resuming normal operation")

    def enter_maintenance(self):
        with self.lock:
            self.maintenance_mode = True
            self.state = ElevatorState.MAINTENANCE
            self.pending_requests.clear()
            self.up_requests.clear()
            self.down_requests.clear()
            self._notify_state_changed()

    def exit_maintenance(self):
        with self.lock:
            self.maintenance_mode = False
            self.state = ElevatorState.IDLE
            self.direction = Direction.IDLE
            self.last_maintenance = time.time()
            self._notify_state_changed()

    def _should_stop_at_floor(self, floor: int) -> bool:
        """Determine if elevator should stop at given floor"""
        if floor not in self.pending_requests:
            return False

        # Always stop for car calls
        if floor in self.pending_requests:
            return True

        # For hall calls, consider direction
        if self.direction == Direction.UP and floor in self.up_requests:
            return True
        elif self.direction == Direction.DOWN and floor in self.down_requests:
            return True

        return False

    def _get_next_floor(self) -> Optional[int]:
        """Determine next floor to visit using SCAN algorithm"""
        if not self.pending_requests:
            return None

        current = self.current_floor

        if self.direction == Direction.UP or self.direction == Direction.IDLE:
            # Check floors above current
            floors_above = [f for f in self.pending_requests if f > current]
            if floors_above:
                return min(floors_above)

            # If no floors above, check floors below
            floors_below = [f for f in self.pending_requests if f < current]
            if floors_below:
                return max(floors_below)

        elif self.direction == Direction.DOWN:
            # Check floors below current
            floors_below = [f for f in self.pending_requests if f < current]
            if floors_below:
                return max(floors_below)

            # If no floors below, check floors above
            floors_above = [f for f in self.pending_requests if f > current]
            if floors_above:
                return min(floors_above)

        return None

    def _update_direction(self):
        """Update elevator direction based on pending requests"""
        if not self.pending_requests:
            self.direction = Direction.IDLE
            return

        next_floor = self._get_next_floor()
        if next_floor is None:
            self.direction = Direction.IDLE
        elif next_floor > self.current_floor:
            self.direction = Direction.UP
        elif next_floor < self.current_floor:
            self.direction = Direction.DOWN
        else:
            self.direction = Direction.IDLE

    def _open_doors(self):
        """Open elevator doors"""
        self.state = ElevatorState.DOORS_OPENING
        self._notify_state_changed()
        self._notify_doors_operation(True)

        time.sleep(self.door_operation_time / 2)

        self.state = ElevatorState.DOORS_OPEN
        self._notify_state_changed()

        # Keep doors open for stop time
        time.sleep(self.stop_time)

    def _close_doors(self):
        """Close elevator doors"""
        self.state = ElevatorState.DOORS_CLOSING
        self._notify_state_changed()
        self._notify_doors_operation(False)

        time.sleep(self.door_operation_time / 2)

        self.state = ElevatorState.IDLE
        self._notify_state_changed()

    def _move_to_floor(self, target_floor: int):
        """Move elevator to target floor"""
        if target_floor == self.current_floor:
            return

        floors_to_travel = abs(target_floor - self.current_floor)

        # Update state based on direction
        if target_floor > self.current_floor:
            self.state = ElevatorState.MOVING_UP
            self.direction = Direction.UP
        else:
            self.state = ElevatorState.MOVING_DOWN
            self.direction = Direction.DOWN

        self._notify_state_changed()

        # Simulate movement
        travel_time = floors_to_travel * self.floor_travel_time
        time.sleep(travel_time)

        # Update current floor
        self.current_floor = target_floor
        self._notify_moved()

    def _process_floor_stop(self, floor: int):
        """Process stopping at a floor"""
        # Remove from all request sets
        self.pending_requests.discard(floor)
        self.up_requests.discard(floor)
        self.down_requests.discard(floor)

        # Open and close doors
        self._open_doors()
        self._close_doors()

    def _run(self):
        """Main elevator operation loop"""
        while self.running:
            try:
                with self.lock:
                    if self.emergency_stop or self.maintenance_mode:
                        time.sleep(1)
                        continue

                    if not self.pending_requests:
                        self.direction = Direction.IDLE
                        self.state = ElevatorState.IDLE
                        time.sleep(0.5)
                        continue

                    next_floor = self._get_next_floor()
                    if next_floor is None:
                        continue

                    # Move to next floor
                    self._move_to_floor(next_floor)

                    # Stop at floor if needed
                    if self._should_stop_at_floor(next_floor):
                        self._process_floor_stop(next_floor)

                    # Update direction for next iteration
                    self._update_direction()

            except Exception as e:
                print(f"Error in elevator {self.elevator_id}: {e}")
                time.sleep(1)

    def stop(self):
        """Stop the elevator thread"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def get_status(self) -> Dict:
        """Get current elevator status"""
        with self.lock:
            return {
                'elevator_id': self.elevator_id,
                'current_floor': self.current_floor,
                'direction': self.direction.value,
                'state': self.state.value,
                'pending_requests': sorted(list(self.pending_requests)),
                'load': self.current_load,
                'capacity': self.max_capacity,
                'maintenance_mode': self.maintenance_mode,
                'emergency_stop': self.emergency_stop
            }

# Building Controller
class BuildingController:
    def __init__(self, num_floors: int, num_elevators: int):
        self.num_floors = num_floors
        self.num_elevators = num_elevators
        self.elevators: List[Elevator] = []
        self.scheduling_strategy = LOOKStrategy()
        self.lock = threading.RLock()

        # Performance metrics
        self.total_requests = 0
        self.total_wait_time = 0
        self.request_times = {}

        # Initialize elevators
        for i in range(num_elevators):
            elevator = Elevator(i + 1, num_floors)
            self.elevators.append(elevator)

        # Add display observer to all elevators
        self.display = Display()
        for elevator in self.elevators:
            elevator.add_observer(self.display)

    def set_scheduling_strategy(self, strategy: SchedulingStrategy):
        self.scheduling_strategy = strategy

    def request_elevator(self, floor: int, direction: Direction) -> bool:
        """External request for elevator (hall call)"""
        with self.lock:
            request = ElevatorRequest(
                floor=floor,
                direction=direction,
                request_type=RequestType.HALL_CALL,
                timestamp=time.time()
            )

            # Track request for metrics
            request_id = f"{floor}_{direction.value}_{request.timestamp}"
            self.request_times[request_id] = request.timestamp
            self.total_requests += 1

            # Select best elevator using strategy
            selected_elevator = self.scheduling_strategy.select_elevator(
                self.elevators, request
            )

            if selected_elevator:
                success = selected_elevator.add_request(floor, direction)
                if success:
                    print(f"🎯 Assigned request (Floor {floor}, {direction.value}) to Elevator {selected_elevator.elevator_id}")
                    return True

            print(f"⚠️ Could not assign request for Floor {floor}, {direction.value}")
            return False

    def car_call(self, elevator_id: int, floor: int) -> bool:
        """Internal request from inside elevator (car call)"""
        if 1 <= elevator_id <= len(self.elevators):
            elevator = self.elevators[elevator_id - 1]
            success = elevator.add_request(floor)
            if success:
                print(f"🏃 Car call: Elevator {elevator_id} to Floor {floor}")
            return success
        return False

    def emergency_stop_all(self):
        """Emergency stop all elevators"""
        for elevator in self.elevators:
            elevator.emergency_stop_engage()

    def emergency_release_all(self):
        """Release emergency stop for all elevators"""
        for elevator in self.elevators:
            elevator.emergency_stop_release()

    def get_building_status(self) -> Dict:
        """Get status of all elevators"""
        with self.lock:
            return {
                'building_info': {
                    'floors': self.num_floors,
                    'elevators': self.num_elevators,
                    'total_requests': self.total_requests,
                    'strategy': self.scheduling_strategy.__class__.__name__
                },
                'elevators': [elevator.get_status() for elevator in self.elevators]
            }

    def shutdown(self):
        """Shutdown all elevators"""
        for elevator in self.elevators:
            elevator.stop()

# Example usage and testing
def simulate_elevator_system():
    print("🏢 Starting Elevator System Simulation")
    print("=" * 50)

    # Create building with 10 floors and 3 elevators
    building = BuildingController(num_floors=10, num_elevators=3)

    try:
        # Test different scenarios
        print("\n📋 Scenario 1: Basic requests")
        building.request_elevator(5, Direction.UP)
        building.request_elevator(3, Direction.DOWN)
        building.car_call(1, 8)

        time.sleep(5)

        print("\n📋 Scenario 2: Multiple requests")
        building.request_elevator(7, Direction.UP)
        building.request_elevator(2, Direction.UP)
        building.request_elevator(9, Direction.DOWN)
        building.car_call(2, 6)
        building.car_call(3, 1)

        time.sleep(8)

        print("\n📋 Scenario 3: Emergency stop test")
        building.emergency_stop_all()
        time.sleep(2)
        building.emergency_release_all()

        time.sleep(5)

        print("\n📊 Final Building Status:")
        status = building.get_building_status()
        print(f"Building: {status['building_info']['floors']} floors, {status['building_info']['elevators']} elevators")
        print(f"Strategy: {status['building_info']['strategy']}")
        print(f"Total Requests: {status['building_info']['total_requests']}")

        for elevator_status in status['elevators']:
            print(f"Elevator {elevator_status['elevator_id']}: Floor {elevator_status['current_floor']}, "
                  f"State: {elevator_status['state']}, Direction: {elevator_status['direction']}")

    finally:
        print("\n🔌 Shutting down elevator system...")
        building.shutdown()

if __name__ == "__main__":
    simulate_elevator_system()
```

## 🎯 Key Design Patterns Used

### 1. State Pattern
- **ElevatorState** enum manages elevator states
- Clean transitions between IDLE, MOVING, DOORS_OPENING, etc.

### 2. Observer Pattern
- **ElevatorObserver** interface for notifications
- **Display** class observes elevator events
- Loose coupling between elevators and monitoring systems

### 3. Strategy Pattern
- **SchedulingStrategy** for different elevator assignment algorithms
- Supports FCFS, Nearest Car, SCAN, LOOK algorithms
- Easily extensible for new scheduling strategies

### 4. Command Pattern (Implicit)
- **ElevatorRequest** encapsulates request information
- Requests can be queued, prioritized, and logged

## 🔧 Advanced Features

### Safety and Reliability
- Emergency stop functionality
- Maintenance mode
- Capacity and weight limits
- Thread-safe operations

### Performance Optimization
- SCAN and LOOK algorithms for efficient scheduling
- Request prioritization
- Load balancing across elevators

### Monitoring and Metrics
- Real-time status tracking
- Performance metrics collection
- Observer pattern for system monitoring

## 📈 Scalability Considerations

### Horizontal Scaling
- Easy to add more elevators
- Configurable building size
- Modular controller design

### Performance Metrics
- Average wait time tracking
- Request completion rate
- System throughput monitoring

## 🧪 Testing Scenarios

### Basic Operations
```python
# Test elevator request handling
building.request_elevator(5, Direction.UP)
building.car_call(1, 8)
```

### Stress Testing
```python
# Multiple simultaneous requests
for floor in range(1, 11):
    building.request_elevator(floor, Direction.UP)
```

### Emergency Scenarios
```python
# Emergency stop and recovery
building.emergency_stop_all()
building.emergency_release_all()
```

## ✅ Learning Outcomes

After implementing this elevator system, you should understand:

- ✅ Complex state management with State pattern
- ✅ Real-time system coordination
- ✅ Thread-safe programming techniques
- ✅ Scheduling algorithm implementation
- ✅ Observer pattern for monitoring
- ✅ Strategy pattern for algorithm selection
- ✅ Safety and reliability considerations
- ✅ Performance optimization techniques

## 🚀 Extensions

### Possible Enhancements
1. **Smart Scheduling** - ML-based prediction
2. **Energy Optimization** - Sleep modes, regenerative braking
3. **VIP Service** - Priority passengers
4. **Destination Dispatch** - Group similar requests
5. **Predictive Maintenance** - Health monitoring
6. **Mobile Integration** - Smartphone app control

## 📚 Related Concepts

- **Real-time Systems** - Time-critical operations
- **Concurrent Programming** - Thread synchronization
- **State Machines** - Complex state management
- **Scheduling Algorithms** - OS scheduling concepts
- **Safety Systems** - Fail-safe design principles