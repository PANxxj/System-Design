# Parking Lot System Design 🟢

## 🎯 Problem Statement

Design a parking lot system that can:
- Handle different vehicle types (car, motorcycle, truck)
- Track available spots and occupancy
- Calculate parking fees
- Handle entry and exit of vehicles

## 📋 Requirements Analysis

### Functional Requirements
1. **Vehicle Management**
   - Support different vehicle types
   - Issue parking tickets
   - Process vehicle exit and payment

2. **Spot Management**
   - Different spot sizes (compact, regular, large)
   - Track spot availability
   - Assign appropriate spots to vehicles

3. **Payment System**
   - Calculate fees based on time and vehicle type
   - Support different payment methods
   - Generate receipts

### Non-Functional Requirements
- System should handle 1000+ parking spots
- Response time < 2 seconds for operations
- 99.9% availability
- Concurrent access by multiple users

## 🏗️ Design Approach

### 1. Identify Core Entities
- **Vehicle**: Different types with different properties
- **ParkingSpot**: Different sizes for different vehicles
- **ParkingLot**: Container for all spots
- **Ticket**: Represents parking session
- **Payment**: Handles fee calculation and processing

### 2. Apply Design Patterns
- **Factory Pattern**: Create different vehicle types
- **Strategy Pattern**: Different pricing strategies
- **Observer Pattern**: Notify when spots become available
- **Singleton Pattern**: Single parking lot instance (if needed)

### 3. Consider Extensibility
- Easy to add new vehicle types
- Flexible pricing strategies
- Support for multiple parking lots

## 💻 Implementation

### Vehicle Hierarchy

```python
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
import uuid

class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"

class Vehicle(ABC):
    def __init__(self, license_plate: str):
        self.license_plate = license_plate
        self.vehicle_type = None

    @abstractmethod
    def get_required_spot_size(self):
        pass

    def __str__(self):
        return f"{self.vehicle_type.value} - {self.license_plate}"

class Motorcycle(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate)
        self.vehicle_type = VehicleType.MOTORCYCLE

    def get_required_spot_size(self):
        return SpotSize.COMPACT

class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate)
        self.vehicle_type = VehicleType.CAR

    def get_required_spot_size(self):
        return SpotSize.REGULAR

class Truck(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate)
        self.vehicle_type = VehicleType.TRUCK

    def get_required_spot_size(self):
        return SpotSize.LARGE
```

### Vehicle Factory

```python
class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type: VehicleType, license_plate: str) -> Vehicle:
        if vehicle_type == VehicleType.MOTORCYCLE:
            return Motorcycle(license_plate)
        elif vehicle_type == VehicleType.CAR:
            return Car(license_plate)
        elif vehicle_type == VehicleType.TRUCK:
            return Truck(license_plate)
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")
```

### Parking Spot System

```python
class SpotSize(Enum):
    COMPACT = "compact"
    REGULAR = "regular"
    LARGE = "large"

class ParkingSpot:
    def __init__(self, spot_id: str, size: SpotSize, floor: int = 1):
        self.spot_id = spot_id
        self.size = size
        self.floor = floor
        self.is_occupied = False
        self.vehicle = None
        self.occupied_since = None

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        """Check if vehicle can fit in this spot"""
        if self.is_occupied:
            return False

        required_size = vehicle.get_required_spot_size()

        # Spot size hierarchy: LARGE can fit all, REGULAR can fit REGULAR and COMPACT
        size_hierarchy = {
            SpotSize.LARGE: [SpotSize.LARGE, SpotSize.REGULAR, SpotSize.COMPACT],
            SpotSize.REGULAR: [SpotSize.REGULAR, SpotSize.COMPACT],
            SpotSize.COMPACT: [SpotSize.COMPACT]
        }

        return required_size in size_hierarchy[self.size]

    def park_vehicle(self, vehicle: Vehicle) -> bool:
        """Park vehicle in this spot"""
        if not self.can_fit_vehicle(vehicle):
            return False

        self.vehicle = vehicle
        self.is_occupied = True
        self.occupied_since = datetime.now()
        return True

    def remove_vehicle(self) -> Vehicle:
        """Remove vehicle from spot"""
        vehicle = self.vehicle
        self.vehicle = None
        self.is_occupied = False
        self.occupied_since = None
        return vehicle

    def __str__(self):
        status = "Occupied" if self.is_occupied else "Available"
        return f"Spot {self.spot_id} ({self.size.value}) - {status}"
```

### Pricing Strategy

```python
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fee(self, vehicle: Vehicle, duration_hours: float) -> float:
        pass

class HourlyPricingStrategy(PricingStrategy):
    def __init__(self):
        self.rates = {
            VehicleType.MOTORCYCLE: 2.0,  # $2/hour
            VehicleType.CAR: 5.0,         # $5/hour
            VehicleType.TRUCK: 10.0       # $10/hour
        }

    def calculate_fee(self, vehicle: Vehicle, duration_hours: float) -> float:
        rate = self.rates[vehicle.vehicle_type]
        return rate * max(1, duration_hours)  # Minimum 1 hour

class FlatRatePricingStrategy(PricingStrategy):
    def __init__(self):
        self.rates = {
            VehicleType.MOTORCYCLE: 5.0,
            VehicleType.CAR: 10.0,
            VehicleType.TRUCK: 20.0
        }

    def calculate_fee(self, vehicle: Vehicle, duration_hours: float) -> float:
        return self.rates[vehicle.vehicle_type]
```

### Ticket System

```python
class ParkingTicket:
    def __init__(self, vehicle: Vehicle, spot: ParkingSpot):
        self.ticket_id = str(uuid.uuid4())
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = datetime.now()
        self.exit_time = None
        self.fee = 0.0
        self.is_paid = False

    def calculate_duration_hours(self) -> float:
        """Calculate parking duration in hours"""
        end_time = self.exit_time or datetime.now()
        duration = end_time - self.entry_time
        return duration.total_seconds() / 3600

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.vehicle} at {self.spot.spot_id}"
```

### Main Parking Lot System

```python
from typing import List, Optional
from collections import defaultdict

class ParkingLot:
    def __init__(self, name: str, pricing_strategy: PricingStrategy):
        self.name = name
        self.spots = []
        self.active_tickets = {}  # ticket_id -> ParkingTicket
        self.pricing_strategy = pricing_strategy

        # Track spots by size for efficient allocation
        self.spots_by_size = defaultdict(list)

    def add_spot(self, spot: ParkingSpot):
        """Add a parking spot to the lot"""
        self.spots.append(spot)
        self.spots_by_size[spot.size].append(spot)

    def get_available_spots_count(self, size: SpotSize = None) -> int:
        """Get count of available spots"""
        if size:
            return len([spot for spot in self.spots_by_size[size] if not spot.is_occupied])
        return len([spot for spot in self.spots if not spot.is_occupied])

    def find_available_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        """Find the best available spot for vehicle"""
        required_size = vehicle.get_required_spot_size()

        # Try to find exact size match first
        for spot in self.spots_by_size[required_size]:
            if spot.can_fit_vehicle(vehicle):
                return spot

        # If no exact match, try larger spots
        size_order = [SpotSize.REGULAR, SpotSize.LARGE]
        if required_size == SpotSize.COMPACT:
            for size in size_order:
                for spot in self.spots_by_size[size]:
                    if spot.can_fit_vehicle(vehicle):
                        return spot
        elif required_size == SpotSize.REGULAR:
            for spot in self.spots_by_size[SpotSize.LARGE]:
                if spot.can_fit_vehicle(vehicle):
                    return spot

        return None

    def park_vehicle(self, vehicle_type: VehicleType, license_plate: str) -> Optional[ParkingTicket]:
        """Park a vehicle and return parking ticket"""
        # Create vehicle using factory
        vehicle = VehicleFactory.create_vehicle(vehicle_type, license_plate)

        # Find available spot
        spot = self.find_available_spot(vehicle)
        if not spot:
            return None

        # Park vehicle
        if spot.park_vehicle(vehicle):
            ticket = ParkingTicket(vehicle, spot)
            self.active_tickets[ticket.ticket_id] = ticket
            return ticket

        return None

    def exit_vehicle(self, ticket_id: str) -> tuple[float, ParkingTicket]:
        """Process vehicle exit and calculate fee"""
        if ticket_id not in self.active_tickets:
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        ticket = self.active_tickets[ticket_id]

        # Calculate fee
        duration_hours = ticket.calculate_duration_hours()
        fee = self.pricing_strategy.calculate_fee(ticket.vehicle, duration_hours)

        # Update ticket
        ticket.exit_time = datetime.now()
        ticket.fee = fee

        # Remove vehicle from spot
        ticket.spot.remove_vehicle()

        # Remove from active tickets
        del self.active_tickets[ticket_id]

        return fee, ticket

    def get_parking_summary(self) -> dict:
        """Get parking lot status summary"""
        total_spots = len(self.spots)
        occupied_spots = len([spot for spot in self.spots if spot.is_occupied])

        summary = {
            'name': self.name,
            'total_spots': total_spots,
            'occupied_spots': occupied_spots,
            'available_spots': total_spots - occupied_spots,
            'occupancy_rate': (occupied_spots / total_spots) * 100 if total_spots > 0 else 0,
            'spots_by_size': {}
        }

        for size in SpotSize:
            size_spots = self.spots_by_size[size]
            occupied_size_spots = len([spot for spot in size_spots if spot.is_occupied])
            summary['spots_by_size'][size.value] = {
                'total': len(size_spots),
                'occupied': occupied_size_spots,
                'available': len(size_spots) - occupied_size_spots
            }

        return summary

    def __str__(self):
        summary = self.get_parking_summary()
        return f"ParkingLot '{summary['name']}': {summary['occupied_spots']}/{summary['total_spots']} spots occupied"
```

### Payment System

```python
class PaymentMethod(Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    MOBILE_PAY = "mobile_pay"

class Payment:
    def __init__(self, ticket: ParkingTicket, amount: float, method: PaymentMethod):
        self.payment_id = str(uuid.uuid4())
        self.ticket = ticket
        self.amount = amount
        self.method = method
        self.timestamp = datetime.now()
        self.is_successful = False

    def process_payment(self) -> bool:
        """Process payment (simplified implementation)"""
        # In real implementation, this would integrate with payment gateways
        if self.amount >= self.ticket.fee:
            self.is_successful = True
            self.ticket.is_paid = True
            return True
        return False

class Receipt:
    def __init__(self, payment: Payment):
        self.receipt_id = str(uuid.uuid4())
        self.payment = payment
        self.generated_at = datetime.now()

    def generate_receipt_text(self) -> str:
        """Generate receipt text"""
        ticket = self.payment.ticket
        duration = ticket.calculate_duration_hours()

        receipt_text = f"""
========= PARKING RECEIPT =========
Receipt ID: {self.receipt_id}
Ticket ID: {ticket.ticket_id}
Vehicle: {ticket.vehicle}
Spot: {ticket.spot.spot_id}
Entry Time: {ticket.entry_time.strftime('%Y-%m-%d %H:%M:%S')}
Exit Time: {ticket.exit_time.strftime('%Y-%m-%d %H:%M:%S')}
Duration: {duration:.2f} hours
Fee: ${ticket.fee:.2f}
Payment Method: {self.payment.method.value}
Payment Status: {'PAID' if self.payment.is_successful else 'PENDING'}
Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
===================================
        """
        return receipt_text.strip()
```

## 🧪 Usage Example

```python
def main():
    # Create parking lot with hourly pricing
    pricing_strategy = HourlyPricingStrategy()
    parking_lot = ParkingLot("Downtown Parking", pricing_strategy)

    # Add parking spots
    # Floor 1: Mixed spots
    for i in range(1, 6):
        parking_lot.add_spot(ParkingSpot(f"A{i:02d}", SpotSize.COMPACT, floor=1))
    for i in range(6, 16):
        parking_lot.add_spot(ParkingSpot(f"A{i:02d}", SpotSize.REGULAR, floor=1))
    for i in range(16, 21):
        parking_lot.add_spot(ParkingSpot(f"A{i:02d}", SpotSize.LARGE, floor=1))

    print("=== Parking Lot System Demo ===")
    print(parking_lot)
    print(f"Available spots: {parking_lot.get_available_spots_count()}")

    # Park vehicles
    print("\n--- Parking Vehicles ---")

    # Park a car
    car_ticket = parking_lot.park_vehicle(VehicleType.CAR, "ABC123")
    if car_ticket:
        print(f"Car parked: {car_ticket}")
    else:
        print("Failed to park car")

    # Park a motorcycle
    motorcycle_ticket = parking_lot.park_vehicle(VehicleType.MOTORCYCLE, "XYZ789")
    if motorcycle_ticket:
        print(f"Motorcycle parked: {motorcycle_ticket}")
    else:
        print("Failed to park motorcycle")

    # Park a truck
    truck_ticket = parking_lot.park_vehicle(VehicleType.TRUCK, "TRUCK01")
    if truck_ticket:
        print(f"Truck parked: {truck_ticket}")
    else:
        print("Failed to park truck")

    print(f"\nAfter parking: {parking_lot}")

    # Simulate some time passing
    import time
    print("\n--- Simulating 2 hours parking ---")

    # In real scenario, vehicles would stay parked for actual time
    # For demo, we'll manually set exit time
    if car_ticket:
        car_ticket.entry_time = datetime.now() - timedelta(hours=2)

    # Process vehicle exit
    print("\n--- Vehicle Exit ---")
    if car_ticket:
        try:
            fee, completed_ticket = parking_lot.exit_vehicle(car_ticket.ticket_id)
            print(f"Car exit fee: ${fee:.2f}")

            # Process payment
            payment = Payment(completed_ticket, fee, PaymentMethod.CREDIT_CARD)
            if payment.process_payment():
                receipt = Receipt(payment)
                print("\nReceipt:")
                print(receipt.generate_receipt_text())
            else:
                print("Payment failed")
        except ValueError as e:
            print(f"Exit error: {e}")

    # Final status
    print(f"\nFinal status: {parking_lot}")

    # Detailed summary
    summary = parking_lot.get_parking_summary()
    print(f"\nDetailed Summary:")
    print(f"Occupancy Rate: {summary['occupancy_rate']:.1f}%")
    for size, stats in summary['spots_by_size'].items():
        print(f"{size.title()} spots: {stats['occupied']}/{stats['total']} occupied")

if __name__ == "__main__":
    main()
```

## 🔧 Extensions and Improvements

### 1. Add Observer Pattern for Notifications

```python
from abc import ABC, abstractmethod
from typing import List

class ParkingObserver(ABC):
    @abstractmethod
    def notify_spot_available(self, spot: ParkingSpot):
        pass

    @abstractmethod
    def notify_lot_full(self, lot: ParkingLot):
        pass

class NotificationService(ParkingObserver):
    def notify_spot_available(self, spot: ParkingSpot):
        print(f"NOTIFICATION: Spot {spot.spot_id} is now available!")

    def notify_lot_full(self, lot: ParkingLot):
        print(f"ALERT: Parking lot '{lot.name}' is full!")

# Add to ParkingLot class:
class ParkingLot:
    def __init__(self, name: str, pricing_strategy: PricingStrategy):
        # ... existing code ...
        self.observers: List[ParkingObserver] = []

    def add_observer(self, observer: ParkingObserver):
        self.observers.append(observer)

    def notify_observers_spot_available(self, spot: ParkingSpot):
        for observer in self.observers:
            observer.notify_spot_available(spot)

    def notify_observers_lot_full(self):
        for observer in self.observers:
            observer.notify_lot_full(self)
```

### 2. Add Reservation System

```python
class Reservation:
    def __init__(self, vehicle: Vehicle, start_time: datetime, duration_hours: int):
        self.reservation_id = str(uuid.uuid4())
        self.vehicle = vehicle
        self.start_time = start_time
        self.end_time = start_time + timedelta(hours=duration_hours)
        self.spot = None
        self.is_active = True

class ReservationManager:
    def __init__(self, parking_lot: ParkingLot):
        self.parking_lot = parking_lot
        self.reservations = {}

    def make_reservation(self, vehicle: Vehicle, start_time: datetime, duration_hours: int) -> Optional[Reservation]:
        """Make a reservation for future parking"""
        reservation = Reservation(vehicle, start_time, duration_hours)

        # Check if spot will be available
        available_spot = self._find_available_spot_for_time(vehicle, start_time, duration_hours)
        if available_spot:
            reservation.spot = available_spot
            self.reservations[reservation.reservation_id] = reservation
            return reservation

        return None

    def _find_available_spot_for_time(self, vehicle: Vehicle, start_time: datetime, duration_hours: int) -> Optional[ParkingSpot]:
        """Find spot available for specific time period"""
        # Implementation would check existing reservations and current occupancy
        # For now, simplified to just find any available spot
        return self.parking_lot.find_available_spot(vehicle)
```

### 3. Add Multiple Floors Support

```python
class ParkingFloor:
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.spots = []
        self.spots_by_size = defaultdict(list)

    def add_spot(self, spot: ParkingSpot):
        spot.floor = self.floor_number
        self.spots.append(spot)
        self.spots_by_size[spot.size].append(spot)

class MultiFloorParkingLot(ParkingLot):
    def __init__(self, name: str, pricing_strategy: PricingStrategy):
        super().__init__(name, pricing_strategy)
        self.floors = {}  # floor_number -> ParkingFloor

    def add_floor(self, floor_number: int):
        self.floors[floor_number] = ParkingFloor(floor_number)

    def add_spot_to_floor(self, floor_number: int, spot: ParkingSpot):
        if floor_number not in self.floors:
            self.add_floor(floor_number)

        self.floors[floor_number].add_spot(spot)
        self.add_spot(spot)  # Also add to main collection
```

## ✅ Key Design Principles Applied

1. **Single Responsibility Principle**: Each class has one reason to change
2. **Open/Closed Principle**: Easy to add new vehicle types or pricing strategies
3. **Liskov Substitution Principle**: Vehicle subtypes are interchangeable
4. **Interface Segregation**: Focused interfaces for different concerns
5. **Dependency Inversion**: Depends on abstractions (PricingStrategy)

## 📊 System Capabilities

- ✅ **Scalable**: Can handle multiple floors and hundreds of spots
- ✅ **Extensible**: Easy to add new vehicle types, pricing strategies
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Testable**: Each component can be tested independently
- ✅ **Robust**: Handles edge cases and errors gracefully

## 🧪 Testing Strategy

```python
import unittest
from unittest.mock import Mock, patch

class TestParkingLot(unittest.TestCase):
    def setUp(self):
        self.pricing_strategy = HourlyPricingStrategy()
        self.parking_lot = ParkingLot("Test Lot", self.pricing_strategy)

        # Add test spots
        self.parking_lot.add_spot(ParkingSpot("A01", SpotSize.COMPACT))
        self.parking_lot.add_spot(ParkingSpot("A02", SpotSize.REGULAR))
        self.parking_lot.add_spot(ParkingSpot("A03", SpotSize.LARGE))

    def test_park_car_success(self):
        ticket = self.parking_lot.park_vehicle(VehicleType.CAR, "TEST123")
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.vehicle.license_plate, "TEST123")

    def test_park_when_no_spots_available(self):
        # Fill all spots
        self.parking_lot.park_vehicle(VehicleType.TRUCK, "TRUCK1")
        self.parking_lot.park_vehicle(VehicleType.CAR, "CAR1")
        self.parking_lot.park_vehicle(VehicleType.MOTORCYCLE, "MOTO1")

        # Try to park another vehicle
        ticket = self.parking_lot.park_vehicle(VehicleType.CAR, "CAR2")
        self.assertIsNone(ticket)

    def test_calculate_parking_fee(self):
        ticket = self.parking_lot.park_vehicle(VehicleType.CAR, "TEST123")

        # Mock 2 hours parking
        ticket.entry_time = datetime.now() - timedelta(hours=2)

        fee, _ = self.parking_lot.exit_vehicle(ticket.ticket_id)
        expected_fee = 5.0 * 2  # $5/hour for car, 2 hours
        self.assertEqual(fee, expected_fee)

if __name__ == "__main__":
    unittest.main()
```

This parking lot system demonstrates clean object-oriented design with proper use of design patterns, extensibility, and real-world functionality.