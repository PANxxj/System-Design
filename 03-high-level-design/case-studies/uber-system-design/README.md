# Uber System Design 🔴

## 🎯 Learning Objectives
- Design a ride-sharing platform at massive scale
- Handle real-time location tracking and matching
- Implement dynamic pricing algorithms
- Design for global availability and low latency

## 📋 Problem Statement

Design a ride-sharing service like Uber that can:

1. **User Management**: Handle riders and drivers globally
2. **Real-time Matching**: Connect riders with nearby drivers efficiently
3. **Location Tracking**: Track driver locations in real-time
4. **Trip Management**: Handle booking, navigation, and completion
5. **Pricing**: Implement dynamic pricing based on demand/supply
6. **Payments**: Process payments securely and reliably
7. **Scalability**: Support millions of users across multiple cities

## 📊 Scale Estimation

### Traffic Estimates
- **Daily Active Users**: 100 million (50M riders, 50M drivers)
- **Daily Trips**: 50 million trips
- **Peak Hour Traffic**: 5x average (250M location updates/hour)
- **Global Presence**: 500+ cities across 60+ countries

### Storage Estimates
- **Trip Data**: 50M trips/day × 2KB = 100GB/day
- **Location Data**: 50M drivers × 4 updates/min × 100 bytes = 20GB/hour
- **User Data**: 100M users × 1KB = 100GB
- **Total Storage**: ~50TB/year (with retention and replicas)

### Bandwidth Estimates
- **Location Updates**: 20GB/hour ÷ 3600 = 5.5MB/s
- **API Calls**: 50M trips × 20 API calls × 1KB = 1TB/day = 12MB/s
- **Total Bandwidth**: ~100MB/s peak

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile Apps   │    │   Web Portal    │    │  Admin Portal   │
│  (iOS/Android)  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                ┌─────────────────▼─────────────────┐
                │          Load Balancer           │
                │         (AWS ALB/NLB)            │
                └─────────────────┬─────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│  User Service  │    │ Location Service │    │  Trip Service    │
│                │    │                  │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Driver Service │    │ Matching Service │    │ Payment Service  │
│                │    │                  │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Pricing Service│    │Notification Svc  │    │  Analytics Svc   │
│                │    │                  │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
```

### Microservices Architecture

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime
import uuid

# Core Domain Models
class UserType(Enum):
    RIDER = "rider"
    DRIVER = "driver"

class TripStatus(Enum):
    REQUESTED = "requested"
    DRIVER_ASSIGNED = "driver_assigned"
    DRIVER_ARRIVED = "driver_arrived"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class VehicleType(Enum):
    ECONOMY = "economy"
    PREMIUM = "premium"
    LUXURY = "luxury"
    SUV = "suv"

@dataclass
class Location:
    latitude: float
    longitude: float
    timestamp: datetime
    accuracy: float = 10.0  # meters

@dataclass
class User:
    user_id: str
    user_type: UserType
    name: str
    email: str
    phone: str
    created_at: datetime
    rating: float = 5.0
    total_trips: int = 0

@dataclass
class Driver(User):
    license_number: str
    vehicle_type: VehicleType
    vehicle_details: Dict
    is_online: bool = False
    current_location: Optional[Location] = None
    total_earnings: float = 0.0

@dataclass
class Trip:
    trip_id: str
    rider_id: str
    driver_id: Optional[str]
    pickup_location: Location
    destination_location: Location
    vehicle_type: VehicleType
    status: TripStatus
    requested_at: datetime
    estimated_price: float
    actual_price: Optional[float] = None
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
```

## 🗂️ Core Services Design

### 1. Location Service

```python
import redis
import json
from typing import List, Tuple
from geopy.distance import geodesic
import time

class LocationService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.location_ttl = 300  # 5 minutes

    def update_driver_location(self, driver_id: str, location: Location):
        """Update driver's current location"""
        location_key = f"driver_location:{driver_id}"
        location_data = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timestamp': location.timestamp.isoformat(),
            'accuracy': location.accuracy
        }

        # Store in Redis with TTL
        self.redis.setex(
            location_key,
            self.location_ttl,
            json.dumps(location_data)
        )

        # Update geospatial index for nearby driver queries
        self.redis.geoadd(
            "drivers_geo",
            location.longitude,
            location.latitude,
            driver_id
        )

        # Publish location update for real-time tracking
        self.redis.publish(
            f"location_updates:{driver_id}",
            json.dumps(location_data)
        )

    def get_driver_location(self, driver_id: str) -> Optional[Location]:
        """Get driver's current location"""
        location_key = f"driver_location:{driver_id}"
        location_data = self.redis.get(location_key)

        if location_data:
            data = json.loads(location_data)
            return Location(
                latitude=data['latitude'],
                longitude=data['longitude'],
                timestamp=datetime.fromisoformat(data['timestamp']),
                accuracy=data['accuracy']
            )
        return None

    def find_nearby_drivers(self, location: Location, radius_km: float = 5,
                          vehicle_type: VehicleType = None, limit: int = 10) -> List[Tuple[str, float]]:
        """Find nearby online drivers"""
        # Use Redis GEORADIUS to find drivers within radius
        nearby_drivers = self.redis.georadius(
            "drivers_geo",
            location.longitude,
            location.latitude,
            radius_km,
            unit='km',
            withdist=True,
            sort='ASC',
            count=limit * 2  # Get more to filter by status and vehicle type
        )

        # Filter by online status and vehicle type
        filtered_drivers = []
        for driver_data in nearby_drivers:
            driver_id = driver_data[0].decode('utf-8')
            distance = float(driver_data[1])

            # Check if driver is online and available
            if self._is_driver_available(driver_id, vehicle_type):
                filtered_drivers.append((driver_id, distance))

            if len(filtered_drivers) >= limit:
                break

        return filtered_drivers

    def _is_driver_available(self, driver_id: str, required_vehicle_type: VehicleType = None) -> bool:
        """Check if driver is online and available"""
        # Check online status
        online_status = self.redis.get(f"driver_online:{driver_id}")
        if not online_status or online_status.decode('utf-8') != 'true':
            return False

        # Check if driver is currently on a trip
        current_trip = self.redis.get(f"driver_current_trip:{driver_id}")
        if current_trip:
            return False

        # Check vehicle type if specified
        if required_vehicle_type:
            driver_vehicle = self.redis.get(f"driver_vehicle:{driver_id}")
            if not driver_vehicle or driver_vehicle.decode('utf-8') != required_vehicle_type.value:
                return False

        return True

    def set_driver_online_status(self, driver_id: str, is_online: bool,
                               vehicle_type: VehicleType = None):
        """Set driver's online status"""
        if is_online:
            self.redis.set(f"driver_online:{driver_id}", 'true')
            if vehicle_type:
                self.redis.set(f"driver_vehicle:{driver_id}", vehicle_type.value)
        else:
            self.redis.delete(f"driver_online:{driver_id}")
            self.redis.delete(f"driver_vehicle:{driver_id}")
            # Remove from geo index
            self.redis.zrem("drivers_geo", driver_id)

    def track_trip_location(self, trip_id: str, driver_id: str, location: Location):
        """Track location during a trip for real-time updates"""
        trip_location_key = f"trip_location:{trip_id}"
        location_data = {
            'driver_id': driver_id,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timestamp': location.timestamp.isoformat()
        }

        # Store latest location
        self.redis.setex(trip_location_key, 3600, json.dumps(location_data))

        # Publish for real-time tracking
        self.redis.publish(f"trip_tracking:{trip_id}", json.dumps(location_data))

        # Store location history
        self.redis.lpush(
            f"trip_history:{trip_id}",
            json.dumps(location_data)
        )
        self.redis.expire(f"trip_history:{trip_id}", 86400)  # 24 hours
```

### 2. Matching Service

```python
import heapq
from typing import List, Optional
import asyncio

class MatchingService:
    def __init__(self, location_service: LocationService, pricing_service):
        self.location_service = location_service
        self.pricing_service = pricing_service
        self.pending_requests = {}  # trip_id -> PendingRequest
        self.driver_assignments = {}  # driver_id -> trip_id

    async def request_ride(self, rider_id: str, pickup_location: Location,
                          destination_location: Location,
                          vehicle_type: VehicleType) -> Optional[Trip]:
        """Process a ride request"""
        # Generate trip ID
        trip_id = str(uuid.uuid4())

        # Calculate estimated price
        estimated_price = await self.pricing_service.calculate_estimated_price(
            pickup_location, destination_location, vehicle_type
        )

        # Create trip
        trip = Trip(
            trip_id=trip_id,
            rider_id=rider_id,
            driver_id=None,
            pickup_location=pickup_location,
            destination_location=destination_location,
            vehicle_type=vehicle_type,
            status=TripStatus.REQUESTED,
            requested_at=datetime.now(),
            estimated_price=estimated_price
        )

        # Find and assign driver
        assigned_driver = await self._find_and_assign_driver(trip)

        if assigned_driver:
            trip.driver_id = assigned_driver
            trip.status = TripStatus.DRIVER_ASSIGNED
            await self._notify_assignment(trip)

        return trip

    async def _find_and_assign_driver(self, trip: Trip) -> Optional[str]:
        """Find and assign the best available driver"""
        nearby_drivers = self.location_service.find_nearby_drivers(
            trip.pickup_location,
            radius_km=10,
            vehicle_type=trip.vehicle_type,
            limit=20
        )

        if not nearby_drivers:
            # No drivers available - add to waiting queue
            await self._add_to_waiting_queue(trip)
            return None

        # Score drivers based on distance, rating, and other factors
        scored_drivers = await self._score_drivers(nearby_drivers, trip)

        # Try to assign drivers in order of score
        for driver_id, score in scored_drivers:
            if await self._try_assign_driver(driver_id, trip.trip_id):
                return driver_id

        return None

    async def _score_drivers(self, nearby_drivers: List[Tuple[str, float]],
                           trip: Trip) -> List[Tuple[str, float]]:
        """Score drivers based on multiple factors"""
        scored_drivers = []

        for driver_id, distance in nearby_drivers:
            # Get driver details (from cache or database)
            driver_rating = await self._get_driver_rating(driver_id)
            driver_acceptance_rate = await self._get_driver_acceptance_rate(driver_id)

            # Calculate composite score
            distance_score = max(0, 10 - distance)  # Closer is better
            rating_score = driver_rating * 2  # Rating 0-5, multiply by 2
            acceptance_score = driver_acceptance_rate * 5  # 0-1, multiply by 5

            total_score = distance_score + rating_score + acceptance_score

            scored_drivers.append((driver_id, total_score))

        # Sort by score (highest first)
        scored_drivers.sort(key=lambda x: x[1], reverse=True)
        return scored_drivers

    async def _try_assign_driver(self, driver_id: str, trip_id: str) -> bool:
        """Try to assign a driver to a trip"""
        # Check if driver is still available (double-check)
        if not self.location_service._is_driver_available(driver_id):
            return False

        # Use Redis for atomic assignment
        assignment_key = f"driver_assignment:{driver_id}"
        result = self.location_service.redis.set(
            assignment_key, trip_id, nx=True, ex=300  # 5 minute timeout
        )

        if result:
            self.driver_assignments[driver_id] = trip_id
            # Send notification to driver
            await self._notify_driver_assignment(driver_id, trip_id)
            return True

        return False

    async def driver_response(self, driver_id: str, trip_id: str, accepted: bool) -> bool:
        """Handle driver's response to trip assignment"""
        if driver_id not in self.driver_assignments:
            return False

        if self.driver_assignments[driver_id] != trip_id:
            return False

        if accepted:
            # Driver accepted - confirm assignment
            await self._confirm_assignment(driver_id, trip_id)
            return True
        else:
            # Driver declined - find another driver
            del self.driver_assignments[driver_id]
            self.location_service.redis.delete(f"driver_assignment:{driver_id}")

            # Try to find another driver
            trip = await self._get_trip(trip_id)
            if trip:
                alternative_driver = await self._find_and_assign_driver(trip)
                if not alternative_driver:
                    await self._handle_no_driver_available(trip)

            return False

    async def _add_to_waiting_queue(self, trip: Trip):
        """Add trip to waiting queue when no drivers available"""
        # Use priority queue based on surge pricing willingness, user tier, etc.
        priority = self._calculate_waiting_priority(trip)

        waiting_key = f"waiting_queue:{trip.vehicle_type.value}"
        self.location_service.redis.zadd(
            waiting_key,
            {trip.trip_id: priority}
        )

        # Notify rider about wait time
        await self._notify_rider_waiting(trip)

    async def driver_became_available(self, driver_id: str, location: Location):
        """Handle when a driver becomes available"""
        # Check waiting queue for nearby requests
        vehicle_type = await self._get_driver_vehicle_type(driver_id)
        waiting_key = f"waiting_queue:{vehicle_type.value}"

        # Get highest priority waiting requests
        waiting_trips = self.location_service.redis.zrevrange(
            waiting_key, 0, 10, withscores=True
        )

        for trip_data in waiting_trips:
            trip_id = trip_data[0].decode('utf-8')
            trip = await self._get_trip(trip_id)

            if trip:
                # Check if driver is close enough
                distance = geodesic(
                    (location.latitude, location.longitude),
                    (trip.pickup_location.latitude, trip.pickup_location.longitude)
                ).kilometers

                if distance <= 10:  # Within 10km
                    if await self._try_assign_driver(driver_id, trip_id):
                        # Remove from waiting queue
                        self.location_service.redis.zrem(waiting_key, trip_id)
                        break

    async def cancel_trip(self, trip_id: str, cancelled_by: str) -> bool:
        """Cancel a trip"""
        trip = await self._get_trip(trip_id)
        if not trip:
            return False

        # Handle cancellation based on trip status
        if trip.status == TripStatus.REQUESTED:
            # Remove from waiting queue if present
            waiting_key = f"waiting_queue:{trip.vehicle_type.value}"
            self.location_service.redis.zrem(waiting_key, trip_id)

        elif trip.status == TripStatus.DRIVER_ASSIGNED and trip.driver_id:
            # Free up the driver
            del self.driver_assignments[trip.driver_id]
            self.location_service.redis.delete(f"driver_assignment:{trip.driver_id}")

            # Apply cancellation penalty if needed
            await self._apply_cancellation_penalty(trip, cancelled_by)

        # Update trip status
        trip.status = TripStatus.CANCELLED
        await self._save_trip(trip)

        # Send notifications
        await self._notify_cancellation(trip, cancelled_by)

        return True

    # Helper methods (simplified implementations)
    async def _get_driver_rating(self, driver_id: str) -> float:
        """Get driver rating from cache or database"""
        # Implementation would fetch from database
        return 4.5

    async def _get_driver_acceptance_rate(self, driver_id: str) -> float:
        """Get driver acceptance rate"""
        # Implementation would calculate from historical data
        return 0.85

    async def _notify_assignment(self, trip: Trip):
        """Notify rider and driver about assignment"""
        # Implementation would use notification service
        pass

    async def _notify_driver_assignment(self, driver_id: str, trip_id: str):
        """Send assignment notification to driver"""
        pass

    async def _confirm_assignment(self, driver_id: str, trip_id: str):
        """Confirm driver assignment"""
        pass

    async def _get_trip(self, trip_id: str) -> Optional[Trip]:
        """Get trip from database"""
        # Implementation would fetch from database
        pass

    async def _save_trip(self, trip: Trip):
        """Save trip to database"""
        # Implementation would save to database
        pass
```

### 3. Pricing Service

```python
import math
from typing import Dict, List
from datetime import datetime, time
from geopy.distance import geodesic

class PricingService:
    def __init__(self):
        # Base pricing configuration
        self.base_fare = {
            VehicleType.ECONOMY: 2.50,
            VehicleType.PREMIUM: 3.50,
            VehicleType.LUXURY: 5.00,
            VehicleType.SUV: 4.00
        }

        self.per_km_rate = {
            VehicleType.ECONOMY: 1.20,
            VehicleType.PREMIUM: 1.80,
            VehicleType.LUXURY: 2.50,
            VehicleType.SUV: 2.00
        }

        self.per_minute_rate = {
            VehicleType.ECONOMY: 0.30,
            VehicleType.PREMIUM: 0.45,
            VehicleType.LUXURY: 0.60,
            VehicleType.SUV: 0.50
        }

        # Surge pricing thresholds
        self.surge_thresholds = {
            'low_demand': 1.0,
            'medium_demand': 1.5,
            'high_demand': 2.0,
            'peak_demand': 3.0
        }

    async def calculate_estimated_price(self, pickup: Location, destination: Location,
                                      vehicle_type: VehicleType,
                                      requested_at: datetime = None) -> float:
        """Calculate estimated trip price"""
        if requested_at is None:
            requested_at = datetime.now()

        # Calculate base price
        base_price = await self._calculate_base_price(pickup, destination, vehicle_type)

        # Apply surge pricing
        surge_multiplier = await self._calculate_surge_multiplier(
            pickup, vehicle_type, requested_at
        )

        # Apply time-based pricing
        time_multiplier = self._calculate_time_multiplier(requested_at)

        # Apply special event pricing
        event_multiplier = await self._calculate_event_multiplier(pickup, requested_at)

        # Calculate final price
        final_price = base_price * surge_multiplier * time_multiplier * event_multiplier

        # Apply minimum fare
        minimum_fare = self._get_minimum_fare(vehicle_type)
        final_price = max(final_price, minimum_fare)

        return round(final_price, 2)

    async def _calculate_base_price(self, pickup: Location, destination: Location,
                                  vehicle_type: VehicleType) -> float:
        """Calculate base price without surge"""
        # Calculate distance
        distance_km = geodesic(
            (pickup.latitude, pickup.longitude),
            (destination.latitude, destination.longitude)
        ).kilometers

        # Estimate time (using average speed)
        average_speed_kmh = await self._get_average_speed(pickup, destination)
        estimated_time_minutes = (distance_km / average_speed_kmh) * 60

        # Calculate price components
        base_fare = self.base_fare[vehicle_type]
        distance_cost = distance_km * self.per_km_rate[vehicle_type]
        time_cost = estimated_time_minutes * self.per_minute_rate[vehicle_type]

        return base_fare + distance_cost + time_cost

    async def _calculate_surge_multiplier(self, location: Location,
                                        vehicle_type: VehicleType,
                                        requested_at: datetime) -> float:
        """Calculate surge pricing multiplier based on supply/demand"""
        # Get current demand in the area
        demand_level = await self._get_demand_level(location, vehicle_type, requested_at)

        # Get available supply
        supply_level = await self._get_supply_level(location, vehicle_type)

        # Calculate demand/supply ratio
        if supply_level == 0:
            return self.surge_thresholds['peak_demand']

        demand_supply_ratio = demand_level / supply_level

        # Apply surge based on ratio
        if demand_supply_ratio <= 1.0:
            return 1.0  # No surge
        elif demand_supply_ratio <= 2.0:
            return self.surge_thresholds['medium_demand']
        elif demand_supply_ratio <= 3.0:
            return self.surge_thresholds['high_demand']
        else:
            return self.surge_thresholds['peak_demand']

    def _calculate_time_multiplier(self, requested_at: datetime) -> float:
        """Apply time-based pricing (peak hours, weekends)"""
        hour = requested_at.hour
        weekday = requested_at.weekday()

        # Peak hours: 7-9 AM, 5-7 PM on weekdays
        is_morning_peak = weekday < 5 and 7 <= hour <= 9
        is_evening_peak = weekday < 5 and 17 <= hour <= 19

        # Weekend nights: Friday/Saturday 10 PM - 2 AM
        is_weekend_night = (
            (weekday == 4 and hour >= 22) or  # Friday night
            (weekday == 5) or  # Saturday
            (weekday == 6 and hour <= 2)  # Sunday early morning
        )

        if is_morning_peak or is_evening_peak:
            return 1.2  # 20% increase during peak hours
        elif is_weekend_night:
            return 1.3  # 30% increase during weekend nights
        else:
            return 1.0

    async def _calculate_event_multiplier(self, location: Location,
                                        requested_at: datetime) -> float:
        """Apply special event pricing"""
        # Check for special events in the area
        events = await self._get_nearby_events(location, requested_at)

        if not events:
            return 1.0

        # Apply highest event multiplier
        max_multiplier = 1.0
        for event in events:
            if event['impact_level'] == 'high':
                max_multiplier = max(max_multiplier, 1.5)
            elif event['impact_level'] == 'medium':
                max_multiplier = max(max_multiplier, 1.25)

        return max_multiplier

    async def _get_demand_level(self, location: Location, vehicle_type: VehicleType,
                              requested_at: datetime) -> int:
        """Get current demand level in the area"""
        # Implementation would analyze:
        # - Number of trip requests in last 15 minutes
        # - Historical demand patterns
        # - Weather conditions
        # - Local events

        # Simplified implementation
        hour = requested_at.hour
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            return 50  # High demand during peak hours
        elif 22 <= hour <= 2:
            return 30  # Medium demand during night hours
        else:
            return 20  # Normal demand

    async def _get_supply_level(self, location: Location, vehicle_type: VehicleType) -> int:
        """Get available supply in the area"""
        # Implementation would count available drivers in the area
        # For now, simulate based on vehicle type
        base_supply = {
            VehicleType.ECONOMY: 25,
            VehicleType.PREMIUM: 15,
            VehicleType.LUXURY: 5,
            VehicleType.SUV: 10
        }
        return base_supply.get(vehicle_type, 20)

    async def _get_average_speed(self, pickup: Location, destination: Location) -> float:
        """Get average speed for route considering traffic"""
        # Implementation would use traffic data APIs
        # Simplified: return different speeds based on time and area
        current_hour = datetime.now().hour

        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:
            return 25  # Slower during peak hours
        elif 22 <= current_hour <= 6:
            return 45  # Faster during night hours
        else:
            return 35  # Normal speed

    def _get_minimum_fare(self, vehicle_type: VehicleType) -> float:
        """Get minimum fare for vehicle type"""
        minimum_fares = {
            VehicleType.ECONOMY: 5.00,
            VehicleType.PREMIUM: 8.00,
            VehicleType.LUXURY: 12.00,
            VehicleType.SUV: 10.00
        }
        return minimum_fares.get(vehicle_type, 5.00)

    async def _get_nearby_events(self, location: Location, requested_at: datetime) -> List[Dict]:
        """Get special events near the location"""
        # Implementation would query events database
        # Consider: concerts, sports events, festivals, etc.
        return []

    async def calculate_actual_price(self, trip: Trip) -> float:
        """Calculate actual price after trip completion"""
        if not trip.distance_km or not trip.duration_minutes:
            return trip.estimated_price

        # Recalculate based on actual distance and time
        base_fare = self.base_fare[trip.vehicle_type]
        distance_cost = trip.distance_km * self.per_km_rate[trip.vehicle_type]
        time_cost = trip.duration_minutes * self.per_minute_rate[trip.vehicle_type]

        actual_price = base_fare + distance_cost + time_cost

        # Apply any surge pricing that was in effect
        # (stored with the trip when it was created)
        surge_multiplier = getattr(trip, 'surge_multiplier', 1.0)
        actual_price *= surge_multiplier

        # Ensure price doesn't vary too much from estimate
        max_variance = trip.estimated_price * 0.2  # 20% variance allowed
        if abs(actual_price - trip.estimated_price) > max_variance:
            actual_price = trip.estimated_price

        return round(actual_price, 2)

    async def apply_discount(self, user_id: str, trip_price: float) -> float:
        """Apply any applicable discounts"""
        # Check for:
        # - Promo codes
        # - First-time user discount
        # - Loyalty program benefits
        # - Corporate discounts

        discount_amount = 0.0

        # Example: First-time user discount
        is_first_time = await self._is_first_time_user(user_id)
        if is_first_time:
            discount_amount += min(trip_price * 0.2, 10.0)  # 20% up to $10

        # Example: Promo code
        active_promo = await self._get_active_promo(user_id)
        if active_promo:
            if active_promo['type'] == 'percentage':
                discount_amount += trip_price * (active_promo['value'] / 100)
            elif active_promo['type'] == 'fixed':
                discount_amount += active_promo['value']

        return max(0, trip_price - discount_amount)

    async def _is_first_time_user(self, user_id: str) -> bool:
        """Check if user is taking their first trip"""
        # Implementation would check user's trip history
        return False

    async def _get_active_promo(self, user_id: str) -> Optional[Dict]:
        """Get active promotional offer for user"""
        # Implementation would check for active promos
        return None
```

### 4. Trip Service

```python
class TripService:
    def __init__(self, matching_service: MatchingService,
                 pricing_service: PricingService,
                 payment_service,
                 notification_service):
        self.matching_service = matching_service
        self.pricing_service = pricing_service
        self.payment_service = payment_service
        self.notification_service = notification_service

    async def start_trip(self, trip_id: str, driver_id: str) -> bool:
        """Start a trip when driver arrives at pickup"""
        trip = await self._get_trip(trip_id)
        if not trip or trip.status != TripStatus.DRIVER_ASSIGNED:
            return False

        if trip.driver_id != driver_id:
            return False

        # Update trip status
        trip.status = TripStatus.IN_PROGRESS
        trip.started_at = datetime.now()

        await self._save_trip(trip)

        # Start location tracking
        await self._start_location_tracking(trip_id, driver_id)

        # Notify rider
        await self.notification_service.notify_trip_started(trip)

        return True

    async def complete_trip(self, trip_id: str, driver_id: str,
                          final_location: Location) -> bool:
        """Complete a trip"""
        trip = await self._get_trip(trip_id)
        if not trip or trip.status != TripStatus.IN_PROGRESS:
            return False

        if trip.driver_id != driver_id:
            return False

        # Calculate trip metrics
        trip_metrics = await self._calculate_trip_metrics(trip_id)
        trip.distance_km = trip_metrics['distance']
        trip.duration_minutes = trip_metrics['duration']

        # Calculate actual price
        trip.actual_price = await self.pricing_service.calculate_actual_price(trip)

        # Apply discounts
        final_price = await self.pricing_service.apply_discount(
            trip.rider_id, trip.actual_price
        )

        # Update trip
        trip.status = TripStatus.COMPLETED
        trip.completed_at = datetime.now()
        trip.final_price = final_price

        await self._save_trip(trip)

        # Process payment
        payment_success = await self.payment_service.process_payment(
            trip.rider_id, final_price, trip_id
        )

        if payment_success:
            # Release driver
            await self._release_driver(driver_id)

            # Send notifications
            await self.notification_service.notify_trip_completed(trip)

            # Request ratings
            await self._request_ratings(trip)

            return True
        else:
            # Handle payment failure
            await self._handle_payment_failure(trip)
            return False

    async def update_trip_status(self, trip_id: str, driver_id: str,
                               new_status: TripStatus) -> bool:
        """Update trip status (driver arrived, etc.)"""
        trip = await self._get_trip(trip_id)
        if not trip or trip.driver_id != driver_id:
            return False

        # Validate status transition
        if not self._is_valid_status_transition(trip.status, new_status):
            return False

        trip.status = new_status

        # Update timestamps
        if new_status == TripStatus.DRIVER_ARRIVED:
            trip.driver_arrived_at = datetime.now()

        await self._save_trip(trip)

        # Send notifications
        await self.notification_service.notify_status_update(trip)

        return True

    async def _calculate_trip_metrics(self, trip_id: str) -> Dict:
        """Calculate distance and duration from location history"""
        # Get location history from Redis
        location_history = self.matching_service.location_service.redis.lrange(
            f"trip_history:{trip_id}", 0, -1
        )

        if len(location_history) < 2:
            return {'distance': 0, 'duration': 0}

        total_distance = 0
        start_time = None
        end_time = None

        previous_location = None
        for location_data in reversed(location_history):  # Oldest to newest
            location_info = json.loads(location_data)
            current_location = Location(
                latitude=location_info['latitude'],
                longitude=location_info['longitude'],
                timestamp=datetime.fromisoformat(location_info['timestamp'])
            )

            if start_time is None:
                start_time = current_location.timestamp

            end_time = current_location.timestamp

            if previous_location:
                segment_distance = geodesic(
                    (previous_location.latitude, previous_location.longitude),
                    (current_location.latitude, current_location.longitude)
                ).kilometers
                total_distance += segment_distance

            previous_location = current_location

        duration_minutes = 0
        if start_time and end_time:
            duration_minutes = (end_time - start_time).total_seconds() / 60

        return {
            'distance': round(total_distance, 2),
            'duration': round(duration_minutes)
        }

    async def _start_location_tracking(self, trip_id: str, driver_id: str):
        """Start tracking driver location for the trip"""
        # Set trip tracking flag
        self.matching_service.location_service.redis.set(
            f"driver_current_trip:{driver_id}", trip_id
        )

    async def _release_driver(self, driver_id: str):
        """Release driver after trip completion"""
        # Remove trip tracking
        self.matching_service.location_service.redis.delete(
            f"driver_current_trip:{driver_id}"
        )

        # Check for waiting requests
        driver_location = self.matching_service.location_service.get_driver_location(driver_id)
        if driver_location:
            await self.matching_service.driver_became_available(driver_id, driver_location)

    def _is_valid_status_transition(self, current: TripStatus, new: TripStatus) -> bool:
        """Validate if status transition is allowed"""
        valid_transitions = {
            TripStatus.REQUESTED: [TripStatus.DRIVER_ASSIGNED, TripStatus.CANCELLED],
            TripStatus.DRIVER_ASSIGNED: [TripStatus.DRIVER_ARRIVED, TripStatus.CANCELLED],
            TripStatus.DRIVER_ARRIVED: [TripStatus.IN_PROGRESS, TripStatus.CANCELLED],
            TripStatus.IN_PROGRESS: [TripStatus.COMPLETED, TripStatus.CANCELLED],
            TripStatus.COMPLETED: [],
            TripStatus.CANCELLED: []
        }

        return new in valid_transitions.get(current, [])

    async def _request_ratings(self, trip: Trip):
        """Request ratings from both rider and driver"""
        # Send rating requests
        await self.notification_service.request_rider_rating(trip)
        await self.notification_service.request_driver_rating(trip)

    async def _handle_payment_failure(self, trip: Trip):
        """Handle payment failure scenarios"""
        # Retry payment
        # Send notification to user
        # Handle based on business rules
        pass

    async def _get_trip(self, trip_id: str) -> Optional[Trip]:
        """Get trip from database"""
        # Implementation would fetch from database
        pass

    async def _save_trip(self, trip: Trip):
        """Save trip to database"""
        # Implementation would save to database
        pass
```

## 🗄️ Database Design

### SQL Schema (for ACID transactions)

```sql
-- Users table
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    user_type ENUM('rider', 'driver') NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('active', 'suspended', 'deleted') DEFAULT 'active',
    rating DECIMAL(3,2) DEFAULT 5.00,
    total_trips INT DEFAULT 0
);

-- Drivers table (additional driver-specific info)
CREATE TABLE drivers (
    driver_id VARCHAR(36) PRIMARY KEY,
    license_number VARCHAR(50) NOT NULL,
    vehicle_type ENUM('economy', 'premium', 'luxury', 'suv') NOT NULL,
    vehicle_make VARCHAR(100),
    vehicle_model VARCHAR(100),
    vehicle_year YEAR,
    vehicle_plate VARCHAR(20),
    is_online BOOLEAN DEFAULT FALSE,
    total_earnings DECIMAL(10,2) DEFAULT 0.00,
    acceptance_rate DECIMAL(3,2) DEFAULT 1.00,
    FOREIGN KEY (driver_id) REFERENCES users(user_id)
);

-- Trips table
CREATE TABLE trips (
    trip_id VARCHAR(36) PRIMARY KEY,
    rider_id VARCHAR(36) NOT NULL,
    driver_id VARCHAR(36),
    pickup_latitude DECIMAL(10, 8) NOT NULL,
    pickup_longitude DECIMAL(11, 8) NOT NULL,
    destination_latitude DECIMAL(10, 8) NOT NULL,
    destination_longitude DECIMAL(11, 8) NOT NULL,
    vehicle_type ENUM('economy', 'premium', 'luxury', 'suv') NOT NULL,
    status ENUM('requested', 'driver_assigned', 'driver_arrived', 'in_progress', 'completed', 'cancelled') NOT NULL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    driver_assigned_at TIMESTAMP NULL,
    driver_arrived_at TIMESTAMP NULL,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    estimated_price DECIMAL(8,2) NOT NULL,
    actual_price DECIMAL(8,2),
    final_price DECIMAL(8,2),
    distance_km DECIMAL(8,3),
    duration_minutes INT,
    surge_multiplier DECIMAL(3,2) DEFAULT 1.00,
    cancellation_reason TEXT,
    cancelled_by VARCHAR(36),
    FOREIGN KEY (rider_id) REFERENCES users(user_id),
    FOREIGN KEY (driver_id) REFERENCES users(user_id),
    INDEX idx_rider_trips (rider_id, requested_at),
    INDEX idx_driver_trips (driver_id, requested_at),
    INDEX idx_status_time (status, requested_at)
);

-- Trip locations (for route tracking)
CREATE TABLE trip_locations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    trip_id VARCHAR(36) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    speed_kmh DECIMAL(5,2),
    heading DECIMAL(5,2),
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    INDEX idx_trip_time (trip_id, timestamp)
);

-- Payments table
CREATE TABLE payments (
    payment_id VARCHAR(36) PRIMARY KEY,
    trip_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    amount DECIMAL(8,2) NOT NULL,
    payment_method ENUM('credit_card', 'debit_card', 'wallet', 'cash') NOT NULL,
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') NOT NULL,
    transaction_id VARCHAR(100),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Ratings table
CREATE TABLE ratings (
    rating_id VARCHAR(36) PRIMARY KEY,
    trip_id VARCHAR(36) NOT NULL,
    rater_id VARCHAR(36) NOT NULL,
    rated_user_id VARCHAR(36) NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    FOREIGN KEY (rater_id) REFERENCES users(user_id),
    FOREIGN KEY (rated_user_id) REFERENCES users(user_id)
);
```

### NoSQL Schema (MongoDB for analytics)

```javascript
// Trip analytics collection
{
  "_id": ObjectId(),
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "rider_id": "rider_123",
  "driver_id": "driver_456",
  "pickup_location": {
    "type": "Point",
    "coordinates": [-122.4194, 37.7749],
    "address": "San Francisco, CA"
  },
  "destination_location": {
    "type": "Point",
    "coordinates": [-122.4089, 37.7849],
    "address": "San Francisco, CA"
  },
  "route": {
    "type": "LineString",
    "coordinates": [
      [-122.4194, 37.7749],
      [-122.4150, 37.7780],
      [-122.4089, 37.7849]
    ]
  },
  "vehicle_type": "economy",
  "requested_at": ISODate("2024-01-15T10:30:00Z"),
  "completed_at": ISODate("2024-01-15T11:00:00Z"),
  "duration_minutes": 30,
  "distance_km": 15.2,
  "pricing": {
    "estimated_price": 18.50,
    "actual_price": 19.25,
    "surge_multiplier": 1.2,
    "base_fare": 2.50,
    "distance_cost": 12.40,
    "time_cost": 4.35
  },
  "city": "san_francisco",
  "hour_of_day": 10,
  "day_of_week": 1,
  "weather_conditions": "clear"
}

// Create geospatial indexes
db.trip_analytics.createIndex({ "pickup_location": "2dsphere" })
db.trip_analytics.createIndex({ "destination_location": "2dsphere" })
db.trip_analytics.createIndex({ "requested_at": 1 })
db.trip_analytics.createIndex({ "city": 1, "requested_at": 1 })
```

## 🔄 API Design

### REST API Endpoints

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# Request/Response models
class RideRequest(BaseModel):
    pickup_latitude: float
    pickup_longitude: float
    destination_latitude: float
    destination_longitude: float
    vehicle_type: str

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
    heading: Optional[float] = None
    speed: Optional[float] = None

class TripResponse(BaseModel):
    trip_id: str
    status: str
    driver_id: Optional[str]
    estimated_price: float
    estimated_arrival_time: Optional[int]

# Rider APIs
@app.post("/api/v1/rides/request")
async def request_ride(request: RideRequest, user_id: str = Depends(get_current_user)):
    """Request a ride"""
    pickup_location = Location(request.pickup_latitude, request.pickup_longitude, datetime.now())
    destination_location = Location(request.destination_latitude, request.destination_longitude, datetime.now())

    trip = await matching_service.request_ride(
        user_id, pickup_location, destination_location, VehicleType(request.vehicle_type)
    )

    if trip:
        return TripResponse(
            trip_id=trip.trip_id,
            status=trip.status.value,
            driver_id=trip.driver_id,
            estimated_price=trip.estimated_price
        )
    else:
        raise HTTPException(status_code=400, detail="Unable to find a driver")

@app.get("/api/v1/rides/{trip_id}")
async def get_trip_status(trip_id: str, user_id: str = Depends(get_current_user)):
    """Get trip status and details"""
    trip = await trip_service._get_trip(trip_id)
    if not trip or trip.rider_id != user_id:
        raise HTTPException(status_code=404, detail="Trip not found")

    return {
        "trip_id": trip.trip_id,
        "status": trip.status.value,
        "driver_id": trip.driver_id,
        "estimated_price": trip.estimated_price,
        "actual_price": trip.actual_price
    }

@app.post("/api/v1/rides/{trip_id}/cancel")
async def cancel_ride(trip_id: str, user_id: str = Depends(get_current_user)):
    """Cancel a ride"""
    success = await matching_service.cancel_trip(trip_id, user_id)
    if success:
        return {"message": "Trip cancelled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Unable to cancel trip")

# Driver APIs
@app.post("/api/v1/drivers/online")
async def go_online(vehicle_type: str, driver_id: str = Depends(get_current_driver)):
    """Set driver status to online"""
    location_service.set_driver_online_status(driver_id, True, VehicleType(vehicle_type))
    return {"message": "Driver is now online"}

@app.post("/api/v1/drivers/offline")
async def go_offline(driver_id: str = Depends(get_current_driver)):
    """Set driver status to offline"""
    location_service.set_driver_online_status(driver_id, False)
    return {"message": "Driver is now offline"}

@app.post("/api/v1/drivers/location")
async def update_location(location: LocationUpdate, driver_id: str = Depends(get_current_driver)):
    """Update driver location"""
    driver_location = Location(location.latitude, location.longitude, datetime.now())
    location_service.update_driver_location(driver_id, driver_location)
    return {"message": "Location updated"}

@app.post("/api/v1/drivers/trips/{trip_id}/accept")
async def accept_trip(trip_id: str, driver_id: str = Depends(get_current_driver)):
    """Accept a trip assignment"""
    success = await matching_service.driver_response(driver_id, trip_id, True)
    if success:
        return {"message": "Trip accepted"}
    else:
        raise HTTPException(status_code=400, detail="Unable to accept trip")

@app.post("/api/v1/drivers/trips/{trip_id}/start")
async def start_trip(trip_id: str, driver_id: str = Depends(get_current_driver)):
    """Start a trip"""
    success = await trip_service.start_trip(trip_id, driver_id)
    if success:
        return {"message": "Trip started"}
    else:
        raise HTTPException(status_code=400, detail="Unable to start trip")

@app.post("/api/v1/drivers/trips/{trip_id}/complete")
async def complete_trip(trip_id: str, location: LocationUpdate,
                       driver_id: str = Depends(get_current_driver)):
    """Complete a trip"""
    final_location = Location(location.latitude, location.longitude, datetime.now())
    success = await trip_service.complete_trip(trip_id, driver_id, final_location)
    if success:
        return {"message": "Trip completed"}
    else:
        raise HTTPException(status_code=400, detail="Unable to complete trip")
```

## 📈 Performance Optimizations

### 1. Geospatial Indexing

```python
class OptimizedLocationService(LocationService):
    def __init__(self, redis_client: redis.Redis):
        super().__init__(redis_client)
        # Use geohashing for faster proximity searches
        self.precision = 7  # ~150m accuracy

    def find_nearby_drivers_optimized(self, location: Location, radius_km: float = 5,
                                    vehicle_type: VehicleType = None, limit: int = 10):
        """Optimized driver search using geohashing"""
        # Use multiple geohash prefixes to cover the search area
        geohashes = self._get_covering_geohashes(location, radius_km)

        candidates = set()
        for geohash in geohashes:
            # Get drivers in this geohash
            driver_keys = self.redis.smembers(f"drivers_geohash:{geohash}")
            candidates.update(driver_keys)

        # Filter and sort candidates
        nearby_drivers = []
        for driver_key in candidates:
            driver_id = driver_key.decode('utf-8').split(':')[1]
            driver_location = self.get_driver_location(driver_id)

            if driver_location:
                distance = geodesic(
                    (location.latitude, location.longitude),
                    (driver_location.latitude, driver_location.longitude)
                ).kilometers

                if distance <= radius_km and self._is_driver_available(driver_id, vehicle_type):
                    nearby_drivers.append((driver_id, distance))

        # Sort by distance and return top results
        nearby_drivers.sort(key=lambda x: x[1])
        return nearby_drivers[:limit]

    def _get_covering_geohashes(self, location: Location, radius_km: float) -> List[str]:
        """Get geohash prefixes that cover the search area"""
        import geohash

        center_hash = geohash.encode(location.latitude, location.longitude, precision=self.precision)

        # Get neighboring geohashes to ensure complete coverage
        neighbors = geohash.neighbors(center_hash)
        covering_hashes = [center_hash] + list(neighbors.values())

        return covering_hashes
```

### 2. Caching Strategy

```python
class CachedMatchingService(MatchingService):
    def __init__(self, location_service: LocationService, pricing_service, cache_client):
        super().__init__(location_service, pricing_service)
        self.cache = cache_client

    async def request_ride_cached(self, rider_id: str, pickup_location: Location,
                                destination_location: Location, vehicle_type: VehicleType):
        """Request ride with caching for pricing and driver data"""

        # Cache estimated price for similar routes
        route_key = self._generate_route_key(pickup_location, destination_location, vehicle_type)
        cached_price = await self.cache.get(f"price_estimate:{route_key}")

        if cached_price:
            estimated_price = float(cached_price)
        else:
            estimated_price = await self.pricing_service.calculate_estimated_price(
                pickup_location, destination_location, vehicle_type
            )
            # Cache for 5 minutes
            await self.cache.setex(f"price_estimate:{route_key}", 300, str(estimated_price))

        # Use cached driver data
        nearby_drivers = await self._get_cached_nearby_drivers(pickup_location, vehicle_type)

        # Rest of the ride request logic...
        return await super().request_ride(rider_id, pickup_location, destination_location, vehicle_type)

    def _generate_route_key(self, pickup: Location, destination: Location,
                          vehicle_type: VehicleType) -> str:
        """Generate cache key for route pricing"""
        # Round coordinates to reduce key space
        pickup_rounded = f"{pickup.latitude:.3f},{pickup.longitude:.3f}"
        dest_rounded = f"{destination.latitude:.3f},{destination.longitude:.3f}"
        return f"{pickup_rounded}:{dest_rounded}:{vehicle_type.value}"

    async def _get_cached_nearby_drivers(self, location: Location,
                                       vehicle_type: VehicleType) -> List[Tuple[str, float]]:
        """Get nearby drivers with caching"""
        location_key = f"{location.latitude:.4f},{location.longitude:.4f}"
        cache_key = f"nearby_drivers:{location_key}:{vehicle_type.value}"

        cached_drivers = await self.cache.get(cache_key)
        if cached_drivers:
            return json.loads(cached_drivers)

        # Fetch from location service
        drivers = self.location_service.find_nearby_drivers(location, vehicle_type=vehicle_type)

        # Cache for 30 seconds
        await self.cache.setex(cache_key, 30, json.dumps(drivers))

        return drivers
```

## 🔒 Security Considerations

### Authentication and Authorization

```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

class SecurityService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            user_type: str = payload.get("user_type")

            if user_id is None:
                raise JWTError("Invalid token")

            return {"user_id": user_id, "user_type": user_type}
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def hash_password(self, password: str) -> str:
        """Hash password"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return self.pwd_context.verify(plain_password, hashed_password)

# Rate limiting
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def is_allowed(self, key: str, limit: int, window_seconds: int) -> bool:
        """Check if request is allowed under rate limit"""
        current_time = int(time.time())
        window_start = current_time - window_seconds

        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start)

        # Count current requests
        current_count = await self.redis.zcard(key)

        if current_count < limit:
            # Add current request
            await self.redis.zadd(key, {str(current_time): current_time})
            await self.redis.expire(key, window_seconds)
            return True

        return False

# Input validation and sanitization
class RequestValidator:
    @staticmethod
    def validate_location(latitude: float, longitude: float) -> bool:
        """Validate location coordinates"""
        if not (-90 <= latitude <= 90):
            return False
        if not (-180 <= longitude <= 180):
            return False
        return True

    @staticmethod
    def validate_trip_request(request: RideRequest) -> List[str]:
        """Validate ride request"""
        errors = []

        if not RequestValidator.validate_location(request.pickup_latitude, request.pickup_longitude):
            errors.append("Invalid pickup location")

        if not RequestValidator.validate_location(request.destination_latitude, request.destination_longitude):
            errors.append("Invalid destination location")

        # Check if pickup and destination are different
        distance = geodesic(
            (request.pickup_latitude, request.pickup_longitude),
            (request.destination_latitude, request.destination_longitude)
        ).meters

        if distance < 100:  # Less than 100 meters
            errors.append("Pickup and destination are too close")

        if distance > 100000:  # More than 100km
            errors.append("Trip distance exceeds maximum allowed")

        return errors
```

## ✅ Knowledge Check

After studying this design, you should understand:

- [ ] Microservices architecture for ride-sharing platforms
- [ ] Real-time location tracking and matching algorithms
- [ ] Dynamic pricing implementation
- [ ] Geospatial data handling and optimization
- [ ] Database design for high-scale transactions
- [ ] Caching strategies for performance
- [ ] Security considerations for mobile applications

## 🔄 Next Steps

- Study [WhatsApp Messaging](../whatsapp-messaging/) for real-time communication
- Learn [YouTube Video Streaming](../youtube-video-streaming/) for content delivery
- Explore [Netflix Architecture](../netflix-architecture/) for global scale
- Practice implementing geospatial features
- Design payment processing systems
- Study real-time analytics and monitoring