"""
PARKING LOT SYSTEM DESIGN - Interview Level
============================================

Problem Statement:
Design a parking lot system that can park different types of vehicles.

Key Requirements:
1. Multiple floors with different spot types
2. Different vehicle types (Motorcycle, Car, Truck)
3. Park/Unpark vehicles with ticket system
4. Calculate parking fees
5. Display available spots

Design Patterns Used:
- Singleton (ParkingLot)
- Factory (Vehicle creation)
- Strategy (Pricing)

Time Complexity: O(n) for finding spots, O(1) for park/unpark
Space Complexity: O(n) where n is total spots
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, List, Dict


# ==================== ENUMS ====================

class VehicleType(Enum):
    MOTORCYCLE = 1
    CAR = 2
    TRUCK = 3


class SpotSize(Enum):
    SMALL = 1   # Motorcycle
    MEDIUM = 2  # Car
    LARGE = 3   # Truck


# ==================== VEHICLE ====================

class Vehicle(ABC):
    def __init__(self, license_plate: str):
        self.license_plate = license_plate

    @abstractmethod
    def get_type(self) -> VehicleType:
        pass

    @abstractmethod
    def can_fit_in_spot(self, spot_size: SpotSize) -> bool:
        pass


class Motorcycle(Vehicle):
    def get_type(self) -> VehicleType:
        return VehicleType.MOTORCYCLE

    def can_fit_in_spot(self, spot_size: SpotSize) -> bool:
        # Motorcycle can fit in any spot size
        return spot_size in [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE]


class Car(Vehicle):
    def get_type(self) -> VehicleType:
        return VehicleType.CAR

    def can_fit_in_spot(self, spot_size: SpotSize) -> bool:
        return spot_size in [SpotSize.MEDIUM, SpotSize.LARGE]


class Truck(Vehicle):
    def get_type(self) -> VehicleType:
        return VehicleType.TRUCK

    def can_fit_in_spot(self, spot_size: SpotSize) -> bool:
        return spot_size == SpotSize.LARGE


# ==================== PARKING SPOT ====================

class ParkingSpot:
    def __init__(self, spot_number: int, size: SpotSize, floor: int):
        self.spot_number = spot_number
        self.size = size
        self.floor = floor
        self.vehicle: Optional[Vehicle] = None
        self.is_free = True

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        return self.is_free and vehicle.can_fit_in_spot(self.size)

    def park(self, vehicle: Vehicle) -> bool:
        if self.can_fit_vehicle(vehicle):
            self.vehicle = vehicle
            self.is_free = False
            return True
        return False

    def unpark(self) -> Optional[Vehicle]:
        if not self.is_free:
            vehicle = self.vehicle
            self.vehicle = None
            self.is_free = True
            return vehicle
        return None

    def __str__(self):
        status = "Free" if self.is_free else f"Occupied({self.vehicle.license_plate})"
        return f"Spot {self.spot_number} [Floor {self.floor}, {self.size.name}] - {status}"


# ==================== PARKING FLOOR ====================

class ParkingFloor:
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.spots: List[ParkingSpot] = []

    def add_spot(self, spot: ParkingSpot):
        self.spots.append(spot)

    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Find first available spot that fits the vehicle"""
        for spot in self.spots:
            if spot.can_fit_vehicle(vehicle):
                return spot
        return None

    def get_available_count(self) -> Dict[SpotSize, int]:
        """Get count of available spots by size"""
        counts = {SpotSize.SMALL: 0, SpotSize.MEDIUM: 0, SpotSize.LARGE: 0}
        for spot in self.spots:
            if spot.is_free:
                counts[spot.size] += 1
        return counts


# ==================== PARKING TICKET ====================

class ParkingTicket:
    ticket_counter = 0

    def __init__(self, vehicle: Vehicle, spot: ParkingSpot):
        ParkingTicket.ticket_counter += 1
        self.ticket_id = f"T{ParkingTicket.ticket_counter:04d}"
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()
        self.exit_time: Optional[datetime] = None

    def calculate_duration_hours(self) -> float:
        end_time = self.exit_time or datetime.now()
        duration = (end_time - self.entry_time).total_seconds() / 3600
        return max(1.0, duration)  # Minimum 1 hour


# ==================== PRICING STRATEGY ====================

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, ticket: ParkingTicket) -> float:
        pass


class HourlyPricing(PricingStrategy):
    RATES = {
        VehicleType.MOTORCYCLE: 2.0,
        VehicleType.CAR: 5.0,
        VehicleType.TRUCK: 10.0
    }

    def calculate_price(self, ticket: ParkingTicket) -> float:
        hours = ticket.calculate_duration_hours()
        rate = self.RATES.get(ticket.vehicle.get_type(), 5.0)
        return round(hours * rate, 2)


# ==================== PARKING LOT (SINGLETON) ====================

class ParkingLot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.floors: List[ParkingFloor] = []
        self.active_tickets: Dict[str, ParkingTicket] = {}
        self.pricing_strategy: PricingStrategy = HourlyPricing()
        self._initialized = True

    def add_floor(self, floor: ParkingFloor):
        self.floors.append(floor)

    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingTicket]:
        """Park vehicle and return ticket"""
        # Find available spot across all floors
        for floor in self.floors:
            spot = floor.find_available_spot(vehicle)
            if spot:
                if spot.park(vehicle):
                    ticket = ParkingTicket(vehicle, spot)
                    self.active_tickets[ticket.ticket_id] = ticket
                    print(f"✓ Parked {vehicle.get_type().name} ({vehicle.license_plate})")
                    print(f"  Location: Floor {spot.floor}, Spot {spot.spot_number}")
                    print(f"  Ticket ID: {ticket.ticket_id}")
                    return ticket

        print(f"✗ No available spot for {vehicle.get_type().name}")
        return None

    def unpark_vehicle(self, ticket_id: str) -> float:
        """Unpark vehicle and return fee"""
        if ticket_id not in self.active_tickets:
            print(f"✗ Invalid ticket: {ticket_id}")
            return 0.0

        ticket = self.active_tickets[ticket_id]
        ticket.exit_time = datetime.now()

        # Calculate fee
        fee = self.pricing_strategy.calculate_price(ticket)

        # Remove vehicle from spot
        ticket.spot.unpark()

        # Remove ticket
        del self.active_tickets[ticket_id]

        duration = ticket.calculate_duration_hours()
        print(f"✓ Unparked {ticket.vehicle.get_type().name} ({ticket.vehicle.license_plate})")
        print(f"  Duration: {duration:.1f} hours")
        print(f"  Fee: ${fee:.2f}")

        return fee

    def display_availability(self):
        """Display available spots per floor"""
        print("\n" + "="*50)
        print("PARKING AVAILABILITY")
        print("="*50)

        for floor in self.floors:
            counts = floor.get_available_count()
            print(f"\nFloor {floor.floor_number}:")
            print(f"  Small (Motorcycle): {counts[SpotSize.SMALL]}")
            print(f"  Medium (Car):       {counts[SpotSize.MEDIUM]}")
            print(f"  Large (Truck):      {counts[SpotSize.LARGE]}")

        print("="*50 + "\n")

    def get_total_spots(self) -> int:
        return sum(len(floor.spots) for floor in self.floors)

    def get_occupied_spots(self) -> int:
        return len(self.active_tickets)


# ==================== DEMO ====================

def run_demo():
    """Demonstrate the parking lot system"""

    print("\n" + "="*60)
    print("PARKING LOT SYSTEM - DEMO".center(60))
    print("="*60 + "\n")

    # Initialize parking lot
    parking_lot = ParkingLot()

    # Create 3 floors
    for floor_num in range(1, 4):
        floor = ParkingFloor(floor_num)

        # Add spots to each floor
        spot_id = 1

        # 10 small spots per floor
        for _ in range(10):
            floor.add_spot(ParkingSpot(spot_id, SpotSize.SMALL, floor_num))
            spot_id += 1

        # 20 medium spots per floor
        for _ in range(20):
            floor.add_spot(ParkingSpot(spot_id, SpotSize.MEDIUM, floor_num))
            spot_id += 1

        # 5 large spots per floor
        for _ in range(5):
            floor.add_spot(ParkingSpot(spot_id, SpotSize.LARGE, floor_num))
            spot_id += 1

        parking_lot.add_floor(floor)

    print(f"Initialized parking lot with {parking_lot.get_total_spots()} total spots")
    parking_lot.display_availability()

    # Test: Park vehicles
    print("\n--- PARKING VEHICLES ---\n")

    vehicles = [
        Car("ABC123"),
        Motorcycle("M001"),
        Truck("TRK999"),
        Car("XYZ789"),
        Motorcycle("M002"),
    ]

    tickets = []
    for vehicle in vehicles:
        ticket = parking_lot.park_vehicle(vehicle)
        if ticket:
            tickets.append(ticket)
        print()

    parking_lot.display_availability()

    # Simulate time passing for first 2 vehicles
    print("⏰ Simulating 2.5 hours for first 2 vehicles...\n")
    for ticket in tickets[:2]:
        ticket.entry_time = datetime.now() - timedelta(hours=2, minutes=30)

    # Test: Unpark vehicles
    print("\n--- UNPARKING VEHICLES ---\n")

    for ticket in tickets[:2]:
        parking_lot.unpark_vehicle(ticket.ticket_id)
        print()

    parking_lot.display_availability()

    # Test: Try to park when spots are limited
    print("\n--- EDGE CASE: Parking Multiple Trucks ---\n")
    print("Attempting to park 6 trucks (only 5 large spots per floor)...\n")

    for i in range(6):
        truck = Truck(f"TRUCK{i+1}")
        parking_lot.park_vehicle(truck)
        print()

    parking_lot.display_availability()

    print("="*60)
    print(f"Summary: {parking_lot.get_occupied_spots()} occupied, "
          f"{parking_lot.get_total_spots() - parking_lot.get_occupied_spots()} available")
    print("="*60 + "\n")


# ==================== MAIN ====================

if __name__ == "__main__":
    run_demo()


"""
INTERVIEW DISCUSSION POINTS:
=============================

1. REQUIREMENTS CLARIFICATION:
   - How many floors? Different vehicle types?
   - Pricing model? Reservation system?
   - Concurrency requirements?

2. DESIGN CHOICES:
   - Singleton for ParkingLot (one instance per system)
   - Strategy pattern for pricing (easy to add new models)
   - Simple linear search for spots (can optimize with hashmap)

3. SCALABILITY:
   - Current: O(n) spot finding - acceptable for small lots
   - Optimization: Index available spots by size
   - For large scale: Use priority queue or availability bitmap

4. EXTENSIONS:
   - Add reservation system
   - Priority parking for disabled/VIP
   - Multiple entry/exit gates
   - Payment processing integration
   - Real-time availability updates (Observer pattern)
   - Database persistence

5. TRADE-OFFS:
   - Simplicity vs Features
   - Performance vs Memory
   - Thread-safety (add locks if needed)

6. TIME COMPLEXITY:
   - Park: O(f*s) where f=floors, s=spots per floor
   - Unpark: O(1) with ticket hashmap
   - Display: O(f*s)

7. IMPROVEMENTS:
   - Cache available spots by size
   - Add logging and monitoring
   - Handle concurrent requests (threading.Lock)
   - Add unit tests
"""
