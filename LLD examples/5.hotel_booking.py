"""
HOTEL BOOKING SYSTEM - Interview Level
=======================================

Problem Statement:
Design a hotel booking system for reserving rooms.

Requirements:
1. Multiple room types (Single, Double, Suite)
2. Room availability check
3. Booking creation and cancellation
4. Price calculation
5. Search available rooms by date

Design Patterns:
- Singleton (Hotel)
- Factory (Room types)
- Strategy (Pricing)
- Observer (Booking notifications)

Time Complexity: O(n) for availability check
Space Complexity: O(n) for rooms and bookings
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


class RoomType(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    SUITE = "SUITE"


class RoomStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BOOKED = "BOOKED"
    MAINTENANCE = "MAINTENANCE"


class Room:
    def __init__(self, room_number: str, room_type: RoomType, base_price: float):
        self.room_number = room_number
        self.room_type = room_type
        self.base_price = base_price
        self.status = RoomStatus.AVAILABLE

    def is_available(self) -> bool:
        return self.status == RoomStatus.AVAILABLE

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type.value}) - ${self.base_price}/night"


class Guest:
    def __init__(self, guest_id: str, name: str, email: str, phone: str):
        self.guest_id = guest_id
        self.name = name
        self.email = email
        self.phone = phone

    def __str__(self):
        return f"{self.name} ({self.email})"


class Booking:
    booking_counter = 0

    def __init__(self, guest: Guest, room: Room, check_in: datetime, check_out: datetime):
        Booking.booking_counter += 1
        self.booking_id = f"BK{Booking.booking_counter:05d}"
        self.guest = guest
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.booking_date = datetime.now()
        self.total_price = 0.0
        self.is_cancelled = False

    def get_num_nights(self) -> int:
        """Calculate number of nights"""
        delta = self.check_out - self.check_in
        return max(1, delta.days)

    def overlaps_with(self, check_in: datetime, check_out: datetime) -> bool:
        """Check if this booking overlaps with given dates"""
        return not (self.check_out <= check_in or self.check_in >= check_out)

    def __str__(self):
        status = "Cancelled" if self.is_cancelled else "Active"
        return (f"Booking {self.booking_id} [{status}]\n"
                f"  Guest: {self.guest.name}\n"
                f"  Room: {self.room.room_number}\n"
                f"  Check-in: {self.check_in.strftime('%Y-%m-%d')}\n"
                f"  Check-out: {self.check_out.strftime('%Y-%m-%d')}\n"
                f"  Total: ${self.total_price:.2f}")


class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, room: Room, num_nights: int) -> float:
        pass


class StandardPricing(PricingStrategy):
    def calculate_price(self, room: Room, num_nights: int) -> float:
        """Simple pricing: base_price * nights"""
        return room.base_price * num_nights


class SeasonalPricing(PricingStrategy):
    def __init__(self, peak_multiplier: float = 1.5):
        self.peak_multiplier = peak_multiplier

    def calculate_price(self, room: Room, num_nights: int) -> float:
        """Seasonal pricing with peak season multiplier"""
        # Simple logic: summer months (6-8) are peak season
        current_month = datetime.now().month
        multiplier = self.peak_multiplier if 6 <= current_month <= 8 else 1.0
        return room.base_price * num_nights * multiplier


class Hotel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.name = "Grand Hotel"
        self.rooms: Dict[str, Room] = {}
        self.guests: Dict[str, Guest] = {}
        self.bookings: List[Booking] = []
        self.pricing_strategy: PricingStrategy = StandardPricing()
        self._initialized = True

    def add_room(self, room: Room):
        """Add room to hotel"""
        self.rooms[room.room_number] = room

    def register_guest(self, guest: Guest):
        """Register a guest"""
        self.guests[guest.guest_id] = guest
        print(f"✓ Registered guest: {guest}")

    def search_available_rooms(self, check_in: datetime, check_out: datetime,
                               room_type: Optional[RoomType] = None) -> List[Room]:
        """Search for available rooms"""
        available = []

        for room in self.rooms.values():
            # Skip if room type doesn't match
            if room_type and room.room_type != room_type:
                continue

            # Skip if room is not available
            if not room.is_available():
                continue

            # Check if room has any overlapping bookings
            is_free = True
            for booking in self.bookings:
                if (booking.room.room_number == room.room_number and
                    not booking.is_cancelled and
                    booking.overlaps_with(check_in, check_out)):
                    is_free = False
                    break

            if is_free:
                available.append(room)

        return available

    def create_booking(self, guest_id: str, room_number: str,
                       check_in: datetime, check_out: datetime) -> Optional[Booking]:
        """Create a new booking"""
        # Validate guest
        guest = self.guests.get(guest_id)
        if not guest:
            print(f"❌ Guest {guest_id} not found!")
            return None

        # Validate room
        room = self.rooms.get(room_number)
        if not room:
            print(f"❌ Room {room_number} not found!")
            return None

        # Validate dates
        if check_in >= check_out:
            print(f"❌ Invalid dates! Check-out must be after check-in.")
            return None

        if check_in < datetime.now():
            print(f"❌ Check-in date cannot be in the past!")
            return None

        # Check availability
        available_rooms = self.search_available_rooms(check_in, check_out)
        if room not in available_rooms:
            print(f"❌ Room {room_number} is not available for selected dates!")
            return None

        # Create booking
        booking = Booking(guest, room, check_in, check_out)

        # Calculate price
        num_nights = booking.get_num_nights()
        booking.total_price = self.pricing_strategy.calculate_price(room, num_nights)

        # Store booking
        self.bookings.append(booking)

        print(f"✓ Booking created successfully!")
        print(f"  Booking ID: {booking.booking_id}")
        print(f"  {num_nights} night(s) @ ${room.base_price}/night")
        print(f"  Total: ${booking.total_price:.2f}")

        return booking

    def cancel_booking(self, booking_id: str) -> bool:
        """Cancel a booking"""
        for booking in self.bookings:
            if booking.booking_id == booking_id:
                if booking.is_cancelled:
                    print(f"❌ Booking {booking_id} is already cancelled!")
                    return False

                booking.is_cancelled = True
                print(f"✓ Booking {booking_id} cancelled successfully!")
                print(f"  Refund: ${booking.total_price:.2f}")
                return True

        print(f"❌ Booking {booking_id} not found!")
        return False

    def get_booking(self, booking_id: str) -> Optional[Booking]:
        """Get booking by ID"""
        for booking in self.bookings:
            if booking.booking_id == booking_id:
                return booking
        return None

    def display_rooms(self):
        """Display all rooms"""
        print("\n" + "="*60)
        print("HOTEL ROOMS")
        print("="*60)

        for room_type in RoomType:
            print(f"\n{room_type.value} Rooms:")
            rooms = [r for r in self.rooms.values() if r.room_type == room_type]
            for room in rooms:
                status = "✓ Available" if room.is_available() else "✗ Unavailable"
                print(f"  {room.room_number}: ${room.base_price}/night - {status}")

        print("="*60 + "\n")

    def display_bookings(self, active_only: bool = False):
        """Display bookings"""
        print("\n" + "="*60)
        title = "ACTIVE BOOKINGS" if active_only else "ALL BOOKINGS"
        print(title)
        print("="*60 + "\n")

        bookings_to_show = [b for b in self.bookings if not active_only or not b.is_cancelled]

        if not bookings_to_show:
            print("No bookings found.")
        else:
            for booking in bookings_to_show:
                print(booking)
                print()

        print("="*60 + "\n")


def run_demo():
    """Run hotel booking demo"""
    print("\n" + "="*70)
    print("HOTEL BOOKING SYSTEM - DEMO".center(70))
    print("="*70 + "\n")

    hotel = Hotel()

    # Add rooms
    print("--- Setting up Hotel Rooms ---\n")

    # Single rooms (101-105)
    for i in range(101, 106):
        hotel.add_room(Room(str(i), RoomType.SINGLE, 100.0))

    # Double rooms (201-210)
    for i in range(201, 211):
        hotel.add_room(Room(str(i), RoomType.DOUBLE, 150.0))

    # Suites (301-303)
    for i in range(301, 304):
        hotel.add_room(Room(str(i), RoomType.SUITE, 300.0))

    print(f"✓ Added {len(hotel.rooms)} rooms\n")

    hotel.display_rooms()

    # Register guests
    print("--- Registering Guests ---\n")

    guests = [
        Guest("G001", "Alice Johnson", "alice@email.com", "555-0101"),
        Guest("G002", "Bob Smith", "bob@email.com", "555-0102"),
        Guest("G003", "Charlie Brown", "charlie@email.com", "555-0103"),
    ]

    for guest in guests:
        hotel.register_guest(guest)

    print()

    # Create bookings
    print("--- Creating Bookings ---\n")

    today = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    # Booking 1: Alice books a double room for 3 nights
    check_in_1 = today + timedelta(days=2)
    check_out_1 = check_in_1 + timedelta(days=3)
    booking1 = hotel.create_booking("G001", "201", check_in_1, check_out_1)
    print()

    # Booking 2: Bob books a suite for 2 nights
    check_in_2 = today + timedelta(days=5)
    check_out_2 = check_in_2 + timedelta(days=2)
    booking2 = hotel.create_booking("G002", "301", check_in_2, check_out_2)
    print()

    # Booking 3: Charlie books a single room for 1 night
    check_in_3 = today + timedelta(days=1)
    check_out_3 = check_in_3 + timedelta(days=1)
    booking3 = hotel.create_booking("G003", "101", check_in_3, check_out_3)
    print()

    # Test: Search available rooms
    print("--- Searching Available Rooms ---\n")

    search_check_in = today + timedelta(days=2)
    search_check_out = search_check_in + timedelta(days=2)

    print(f"Searching for available rooms:")
    print(f"  Check-in: {search_check_in.strftime('%Y-%m-%d')}")
    print(f"  Check-out: {search_check_out.strftime('%Y-%m-%d')}\n")

    available = hotel.search_available_rooms(search_check_in, search_check_out)
    print(f"Found {len(available)} available rooms:")
    for room in available[:5]:  # Show first 5
        print(f"  - {room}")
    print()

    # Test: Try to book already booked room
    print("--- Attempting to Book Already Booked Room ---\n")
    hotel.create_booking("G002", "201", check_in_1, check_out_1)
    print()

    # Display all bookings
    hotel.display_bookings()

    # Test: Cancel booking
    print("--- Cancelling Booking ---\n")
    if booking2:
        hotel.cancel_booking(booking2.booking_id)
    print()

    # Display active bookings
    hotel.display_bookings(active_only=True)

    # Test: Search by room type
    print("--- Searching by Room Type ---\n")
    print("Available SUITE rooms for next week:")
    available_suites = hotel.search_available_rooms(next_week, next_week + timedelta(days=2), RoomType.SUITE)
    print(f"  Found {len(available_suites)} suite(s)")
    for room in available_suites:
        print(f"    - {room}")
    print()

    print("="*70)
    print("DEMO COMPLETE".center(70))
    print("="*70 + "\n")


if __name__ == "__main__":
    run_demo()


"""
INTERVIEW DISCUSSION POINTS:
=============================

1. REQUIREMENTS CLARIFICATION:
   - Payment processing?
   - Cancellation policy (full/partial refund)?
   - Multiple guests per room?
   - Amenities tracking?
   - Loyalty programs?

2. DESIGN CHOICES:
   - Singleton for Hotel
   - Strategy for pricing (seasonal, dynamic)
   - Date overlap check for availability
   - Booking as separate entity

3. EXTENSIONS:
   - Multiple hotels (hotel chain)
   - Room amenities (WiFi, AC, etc.)
   - Meal plans (breakfast, half-board, full-board)
   - Special requests (high floor, sea view)
   - Group bookings
   - Waitlist for fully booked dates
   - Early check-in/late checkout
   - Housekeeping schedule

4. OPTIMIZATIONS:
   - Index bookings by date range
   - Cache availability for popular dates
   - Pre-calculate availability calendar
   - Use interval trees for date overlap

5. EDGE CASES:
   - Same-day booking and checkout
   - Booking modification
   - No-show handling
   - Overbooking strategy
   - Maintenance period blocking

6. COMPLEXITY:
   - Search availability: O(n*m) where n=rooms, m=bookings
   - Create booking: O(n) for availability check
   - Cancel booking: O(n)
   - Optimization: O(log n) with interval tree

7. REAL-WORLD:
   - Integration with payment gateways
   - Email/SMS notifications
   - Mobile app
   - Dynamic pricing based on demand
   - Integration with OTAs (Booking.com, etc.)
   - Revenue management system
"""
