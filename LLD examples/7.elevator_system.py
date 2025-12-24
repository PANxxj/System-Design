"""
ELEVATOR SYSTEM - Interview Level
==================================

Problem Statement:
Design an elevator system for a multi-floor building.

Requirements:
1. Multiple elevators
2. Handle up/down requests
3. Elevator scheduling (nearest car)
4. Door open/close
5. Emergency handling
6. Display current floor

Design Patterns:
- State Pattern (Elevator states)
- Strategy (Scheduling algorithms)
- Observer (Floor displays)

Time Complexity: O(n) for elevator selection
Space Complexity: O(n) for requests
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Set
import heapq


class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    IDLE = "IDLE"


class ElevatorState(Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    DOOR_OPEN = "DOOR_OPEN"
    MAINTENANCE = "MAINTENANCE"


class Request:
    def __init__(self, floor: int, direction: Direction):
        self.floor = floor
        self.direction = direction

    def __str__(self):
        return f"Floor {self.floor} - {self.direction.value}"


class Elevator:
    def __init__(self, elevator_id: int, max_floor: int):
        self.elevator_id = elevator_id
        self.current_floor = 1
        self.direction = Direction.IDLE
        self.state = ElevatorState.IDLE
        self.max_floor = max_floor

        # Pending requests (set of floors to visit)
        self.up_stops: Set[int] = set()  # Floors to stop while going up
        self.down_stops: Set[int] = set()  # Floors to stop while going down

        self.capacity = 10  # Max people
        self.current_load = 0

    def add_stop(self, floor: int):
        """Add a floor to stop at"""
        if floor < 1 or floor > self.max_floor:
            return

        if floor > self.current_floor:
            self.up_stops.add(floor)
        elif floor < self.current_floor:
            self.down_stops.add(floor)

    def move(self):
        """Move elevator one floor"""
        if self.state == ElevatorState.MAINTENANCE:
            return

        # Check if we need to stop at current floor
        if self.should_stop():
            self.stop()
            return

        # Decide direction
        if not self.up_stops and not self.down_stops:
            self.direction = Direction.IDLE
            self.state = ElevatorState.IDLE
            return

        # Moving up
        if self.up_stops and (not self.down_stops or self.direction == Direction.UP):
            self.direction = Direction.UP
            self.state = ElevatorState.MOVING
            self.current_floor += 1
            print(f"  Elevator {self.elevator_id}: Moving UP to floor {self.current_floor}")

        # Moving down
        elif self.down_stops:
            self.direction = Direction.DOWN
            self.state = ElevatorState.MOVING
            self.current_floor -= 1
            print(f"  Elevator {self.elevator_id}: Moving DOWN to floor {self.current_floor}")

    def should_stop(self) -> bool:
        """Check if elevator should stop at current floor"""
        if self.direction == Direction.UP and self.current_floor in self.up_stops:
            return True
        if self.direction == Direction.DOWN and self.current_floor in self.down_stops:
            return True
        return False

    def stop(self):
        """Stop at current floor"""
        self.state = ElevatorState.DOOR_OPEN
        print(f"  Elevator {self.elevator_id}: STOPPED at floor {self.current_floor} - Door OPEN")

        # Remove this floor from stops
        self.up_stops.discard(self.current_floor)
        self.down_stops.discard(self.current_floor)

        # Close door
        self.close_door()

    def close_door(self):
        """Close elevator door"""
        if self.state == ElevatorState.DOOR_OPEN:
            self.state = ElevatorState.IDLE
            print(f"  Elevator {self.elevator_id}: Door CLOSED")

    def is_available(self) -> bool:
        """Check if elevator is available"""
        return self.state != ElevatorState.MAINTENANCE

    def get_distance(self, floor: int) -> int:
        """Calculate distance to requested floor"""
        return abs(self.current_floor - floor)

    def is_moving_towards(self, floor: int, direction: Direction) -> bool:
        """Check if elevator is moving towards requested floor in same direction"""
        if self.direction == Direction.IDLE:
            return True

        if self.direction == direction:
            if direction == Direction.UP:
                return self.current_floor < floor
            else:
                return self.current_floor > floor

        return False

    def __str__(self):
        stops = list(self.up_stops) + list(self.down_stops)
        return (f"Elevator {self.elevator_id}: Floor {self.current_floor}, "
                f"{self.direction.value}, {self.state.value}, Stops: {sorted(stops)}")


class ElevatorScheduler(ABC):
    """Abstract scheduler"""

    @abstractmethod
    def select_elevator(self, elevators: List[Elevator], request: Request) -> Optional[Elevator]:
        pass


class NearestCarScheduler(ElevatorScheduler):
    """Selects nearest available elevator"""

    def select_elevator(self, elevators: List[Elevator], request: Request) -> Optional[Elevator]:
        available = [e for e in elevators if e.is_available()]

        if not available:
            return None

        # Find nearest elevator
        best_elevator = None
        min_distance = float('inf')

        for elevator in available:
            distance = elevator.get_distance(request.floor)

            # Prefer elevators moving in same direction
            if elevator.is_moving_towards(request.floor, request.direction):
                distance -= 100  # Bonus for same direction

            if distance < min_distance:
                min_distance = distance
                best_elevator = elevator

        return best_elevator


class ElevatorController:
    """Controls multiple elevators"""

    def __init__(self, num_elevators: int, num_floors: int):
        self.elevators = [Elevator(i + 1, num_floors) for i in range(num_elevators)]
        self.num_floors = num_floors
        self.scheduler = NearestCarScheduler()

    def request_elevator(self, floor: int, direction: Direction):
        """Request elevator from a floor"""
        print(f"\n📞 Request: Floor {floor} - {direction.value}")

        request = Request(floor, direction)
        elevator = self.scheduler.select_elevator(self.elevators, request)

        if elevator:
            print(f"✓ Assigned Elevator {elevator.elevator_id}")
            elevator.add_stop(floor)
        else:
            print("❌ No elevator available!")

    def destination_request(self, elevator_id: int, floor: int):
        """Request destination from inside elevator"""
        elevator = self.elevators[elevator_id - 1]
        print(f"\n🔘 Elevator {elevator_id}: Destination floor {floor}")
        elevator.add_stop(floor)

    def step(self):
        """Simulate one time step - move all elevators"""
        for elevator in self.elevators:
            if elevator.up_stops or elevator.down_stops:
                elevator.move()

    def run_simulation(self, steps: int):
        """Run simulation for given steps"""
        for i in range(steps):
            if i % 5 == 0:  # Print status every 5 steps
                print(f"\n--- Step {i} ---")
                self.display_status()

            self.step()

            # Check if all idle
            if all(e.direction == Direction.IDLE for e in self.elevators):
                print(f"\n✓ All elevators idle at step {i}")
                break

    def display_status(self):
        """Display status of all elevators"""
        print("\nElevator Status:")
        for elevator in self.elevators:
            print(f"  {elevator}")


def run_demo():
    """Run elevator system demo"""
    print("\n" + "="*70)
    print("ELEVATOR SYSTEM - DEMO".center(70))
    print("="*70 + "\n")

    # Create system with 3 elevators and 10 floors
    controller = ElevatorController(num_elevators=3, num_floors=10)

    print("Initialized system with 3 elevators, 10 floors")
    controller.display_status()

    # Scenario 1: Simple request
    print("\n" + "="*70)
    print("SCENARIO 1: Simple Requests")
    print("="*70)

    # Person at floor 5 wants to go down
    controller.request_elevator(5, Direction.DOWN)

    # Person inside elevator 1 wants to go to floor 1
    controller.destination_request(1, 1)

    # Simulate
    controller.run_simulation(20)

    # Scenario 2: Multiple requests
    print("\n" + "="*70)
    print("SCENARIO 2: Multiple Requests")
    print("="*70)

    # Reset elevators
    controller = ElevatorController(num_elevators=3, num_floors=10)

    # Multiple simultaneous requests
    controller.request_elevator(7, Direction.UP)
    controller.request_elevator(3, Direction.DOWN)
    controller.request_elevator(9, Direction.DOWN)

    # Destinations
    controller.destination_request(1, 10)
    controller.destination_request(2, 1)
    controller.destination_request(3, 5)

    controller.run_simulation(40)

    # Scenario 3: Same direction optimization
    print("\n" + "="*70)
    print("SCENARIO 3: Same Direction Optimization")
    print("="*70)

    controller = ElevatorController(num_elevators=2, num_floors=10)

    # Elevator 1 going from floor 1 to 10
    controller.request_elevator(1, Direction.UP)
    controller.destination_request(1, 10)

    # Someone at floor 5 also wants to go up
    # Should use elevator 1 since it's going up
    controller.request_elevator(5, Direction.UP)
    controller.destination_request(1, 7)

    controller.run_simulation(30)

    print("\n" + "="*70)
    print("DEMO COMPLETE".center(70))
    print("="*70 + "\n")


if __name__ == "__main__":
    run_demo()


"""
INTERVIEW DISCUSSION POINTS:
=============================

1. REQUIREMENTS CLARIFICATION:
   - Number of elevators/floors?
   - Capacity per elevator?
   - Priority handling (emergency, VIP)?
   - Express elevators?
   - Peak hour handling?

2. DESIGN CHOICES:
   - Strategy pattern for scheduling
   - Separate up/down stop lists
   - Distance-based elevator selection
   - Simple state machine

3. SCHEDULING ALGORITHMS:
   - Nearest Car (implemented)
   - SCAN (elevator keeps going in same direction)
   - LOOK (like SCAN but reverses at last request)
   - Destination Dispatch (assign elevator at request time)

4. EXTENSIONS:
   - Express elevators (skip floors)
   - Floor restrictions (key card required)
   - Load balancing
   - Energy optimization
   - Peak hour modes
   - Emergency evacuation mode
   - Service/maintenance mode

5. OPTIMIZATIONS:
   - Predictive algorithms (ML-based)
   - Zone-based dispatch
   - Destination grouping
   - Idle positioning (park at busy floors)

6. EDGE CASES:
   - All elevators full
   - Emergency stop
   - Power failure
   - Doors stuck open
   - Overload condition

7. COMPLEXITY:
   - Select elevator: O(n) where n=number of elevators
   - Move elevator: O(1)
   - Add stop: O(1)
   - Can optimize with priority queues

8. REAL-WORLD:
   - Sensor integration
   - Real-time monitoring
   - Analytics (wait times, usage patterns)
   - Integration with building systems
   - Mobile app for calling elevator
"""
