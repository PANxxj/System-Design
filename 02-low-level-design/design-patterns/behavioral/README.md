# Behavioral Design Patterns 🔴

## 🎯 Learning Objectives
- Master behavioral patterns for object interaction
- Understand communication between objects and classes
- Learn to define algorithms and assign responsibilities
- Implement patterns that make complex behavior manageable

## 📖 Overview

Behavioral patterns focus on communication between objects and the assignment of responsibilities. They help define how objects interact and communicate with each other.

## 👁️ Observer Pattern

### Problem
Need to notify multiple objects about state changes without tight coupling.

### Solution
Define a subscription mechanism to notify multiple objects about events.

```python
from abc import ABC, abstractmethod
from typing import List
import threading

# Subject interface
class Subject(ABC):
    @abstractmethod
    def attach(self, observer):
        pass

    @abstractmethod
    def detach(self, observer):
        pass

    @abstractmethod
    def notify(self):
        pass

# Observer interface
class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass

# Concrete subject
class WeatherStation(Subject):
    def __init__(self):
        self._observers: List[Observer] = []
        self._temperature = 0
        self._humidity = 0
        self._pressure = 0
        self._lock = threading.Lock()

    def attach(self, observer: Observer):
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
                print(f"WeatherStation: Attached observer {observer.__class__.__name__}")

    def detach(self, observer: Observer):
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
                print(f"WeatherStation: Detached observer {observer.__class__.__name__}")

    def notify(self):
        with self._lock:
            observers_copy = self._observers.copy()

        print("WeatherStation: Notifying observers...")
        for observer in observers_copy:
            observer.update(self)

    def set_measurements(self, temperature, humidity, pressure):
        print(f"WeatherStation: New measurements - T:{temperature}°C, H:{humidity}%, P:{pressure}hPa")
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        self.notify()

    @property
    def temperature(self):
        return self._temperature

    @property
    def humidity(self):
        return self._humidity

    @property
    def pressure(self):
        return self._pressure

# Concrete observers
class CurrentConditionsDisplay(Observer):
    def update(self, subject: WeatherStation):
        temperature = subject.temperature
        humidity = subject.humidity
        print(f"Current Conditions: {temperature}°C and {humidity}% humidity")

class StatisticsDisplay(Observer):
    def __init__(self):
        self.temperatures = []

    def update(self, subject: WeatherStation):
        self.temperatures.append(subject.temperature)
        avg_temp = sum(self.temperatures) / len(self.temperatures)
        max_temp = max(self.temperatures)
        min_temp = min(self.temperatures)
        print(f"Statistics: Avg/Max/Min temperature: {avg_temp:.1f}°C/{max_temp}°C/{min_temp}°C")

class ForecastDisplay(Observer):
    def update(self, subject: WeatherStation):
        pressure = subject.pressure
        if pressure > 1020:
            forecast = "Improving weather on the way!"
        elif pressure > 1000:
            forecast = "More of the same"
        else:
            forecast = "Watch out for cooler, rainy weather"
        print(f"Forecast: {forecast}")

# Event-driven approach with Python
class EventManager:
    def __init__(self):
        self._listeners = {}

    def subscribe(self, event_type, listener):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def unsubscribe(self, event_type, listener):
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)

    def notify(self, event_type, data):
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                listener(data)

# Usage
print("=== Observer Pattern Example ===")
weather_station = WeatherStation()

current_display = CurrentConditionsDisplay()
statistics_display = StatisticsDisplay()
forecast_display = ForecastDisplay()

weather_station.attach(current_display)
weather_station.attach(statistics_display)
weather_station.attach(forecast_display)

weather_station.set_measurements(25, 65, 1013)
print()
weather_station.set_measurements(27, 70, 1015)
print()
weather_station.set_measurements(22, 90, 985)

print("\n=== Event Manager Example ===")
event_manager = EventManager()

def on_user_login(data):
    print(f"Logging: User {data['username']} logged in")

def on_user_login_email(data):
    print(f"Email: Welcome back, {data['username']}!")

event_manager.subscribe("user_login", on_user_login)
event_manager.subscribe("user_login", on_user_login_email)

event_manager.notify("user_login", {"username": "john_doe", "timestamp": "2023-10-01 10:00:00"})
```

### When to Use Observer Pattern
- ✅ Changes to one object require updating multiple objects
- ✅ Objects should be loosely coupled
- ✅ Need to broadcast communication
- ✅ Don't know in advance which objects need updates

## 🔧 Strategy Pattern

### Problem
Need to use different algorithms interchangeably.

### Solution
Define a family of algorithms and make them interchangeable.

```python
from abc import ABC, abstractmethod
import time

# Strategy interface
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data):
        pass

# Concrete strategies
class BubbleSort(SortStrategy):
    def sort(self, data):
        print("Using Bubble Sort")
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr

class QuickSort(SortStrategy):
    def sort(self, data):
        print("Using Quick Sort")
        arr = data.copy()
        self._quick_sort(arr, 0, len(arr) - 1)
        return arr

    def _quick_sort(self, arr, low, high):
        if low < high:
            pi = self._partition(arr, low, high)
            self._quick_sort(arr, low, pi - 1)
            self._quick_sort(arr, pi + 1, high)

    def _partition(self, arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

class MergeSort(SortStrategy):
    def sort(self, data):
        print("Using Merge Sort")
        arr = data.copy()
        self._merge_sort(arr, 0, len(arr) - 1)
        return arr

    def _merge_sort(self, arr, left, right):
        if left < right:
            mid = (left + right) // 2
            self._merge_sort(arr, left, mid)
            self._merge_sort(arr, mid + 1, right)
            self._merge(arr, left, mid, right)

    def _merge(self, arr, left, mid, right):
        left_part = arr[left:mid + 1]
        right_part = arr[mid + 1:right + 1]

        i = j = 0
        k = left

        while i < len(left_part) and j < len(right_part):
            if left_part[i] <= right_part[j]:
                arr[k] = left_part[i]
                i += 1
            else:
                arr[k] = right_part[j]
                j += 1
            k += 1

        while i < len(left_part):
            arr[k] = left_part[i]
            i += 1
            k += 1

        while j < len(right_part):
            arr[k] = right_part[j]
            j += 1
            k += 1

# Context
class DataSorter:
    def __init__(self, strategy: SortStrategy = None):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy):
        self._strategy = strategy

    def sort_data(self, data):
        if not self._strategy:
            raise ValueError("Sort strategy not set")

        start_time = time.time()
        result = self._strategy.sort(data)
        end_time = time.time()

        print(f"Sorting completed in {end_time - start_time:.4f} seconds")
        return result

# Advanced example: Payment processing
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number, cvv):
        self.card_number = card_number
        self.cvv = cvv

    def pay(self, amount):
        return f"Paid ${amount} using Credit Card ending in {self.card_number[-4:]}"

class PayPalPayment(PaymentStrategy):
    def __init__(self, email):
        self.email = email

    def pay(self, amount):
        return f"Paid ${amount} using PayPal account {self.email}"

class BankTransferPayment(PaymentStrategy):
    def __init__(self, account_number):
        self.account_number = account_number

    def pay(self, amount):
        return f"Paid ${amount} using Bank Transfer from account {self.account_number}"

class ShoppingCart:
    def __init__(self):
        self.items = []
        self.payment_strategy = None

    def add_item(self, item, price):
        self.items.append((item, price))

    def calculate_total(self):
        return sum(price for _, price in self.items)

    def set_payment_strategy(self, strategy: PaymentStrategy):
        self.payment_strategy = strategy

    def checkout(self):
        if not self.payment_strategy:
            return "Please select a payment method"

        total = self.calculate_total()
        return self.payment_strategy.pay(total)

# Usage
print("=== Sorting Strategy Example ===")
data = [64, 34, 25, 12, 22, 11, 90]
print(f"Original data: {data}")

sorter = DataSorter()

# Use different strategies
sorter.set_strategy(BubbleSort())
result1 = sorter.sort_data(data)
print(f"Bubble sort result: {result1}\n")

sorter.set_strategy(QuickSort())
result2 = sorter.sort_data(data)
print(f"Quick sort result: {result2}\n")

sorter.set_strategy(MergeSort())
result3 = sorter.sort_data(data)
print(f"Merge sort result: {result3}\n")

print("=== Payment Strategy Example ===")
cart = ShoppingCart()
cart.add_item("Laptop", 999.99)
cart.add_item("Mouse", 29.99)
cart.add_item("Keyboard", 79.99)

print(f"Total: ${cart.calculate_total()}")

# Try different payment methods
cart.set_payment_strategy(CreditCardPayment("1234567890123456", "123"))
print(cart.checkout())

cart.set_payment_strategy(PayPalPayment("user@example.com"))
print(cart.checkout())

cart.set_payment_strategy(BankTransferPayment("ACC123456"))
print(cart.checkout())
```

### When to Use Strategy Pattern
- ✅ Multiple ways to perform a task
- ✅ Want to switch algorithms at runtime
- ✅ Avoid conditional statements for algorithm selection
- ✅ Different variants of algorithms

## 📋 Command Pattern

### Problem
Need to parameterize objects with operations, queue operations, or support undo.

### Solution
Encapsulate requests as objects with all necessary information.

```python
from abc import ABC, abstractmethod
from typing import List
import time
import json

# Command interface
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

# Receiver classes
class Light:
    def __init__(self, location):
        self.location = location
        self.is_on = False
        self.brightness = 50

    def turn_on(self):
        self.is_on = True
        return f"Light in {self.location} is ON"

    def turn_off(self):
        self.is_on = False
        return f"Light in {self.location} is OFF"

    def set_brightness(self, level):
        old_brightness = self.brightness
        self.brightness = max(0, min(100, level))
        return f"Light in {self.location} brightness set to {self.brightness}%", old_brightness

class Fan:
    def __init__(self, location):
        self.location = location
        self.is_on = False
        self.speed = 0

    def turn_on(self):
        self.is_on = True
        self.speed = 1
        return f"Fan in {self.location} is ON at speed {self.speed}"

    def turn_off(self):
        self.is_on = False
        old_speed = self.speed
        self.speed = 0
        return f"Fan in {self.location} is OFF", old_speed

    def set_speed(self, speed):
        old_speed = self.speed
        self.speed = max(0, min(5, speed))
        if self.speed > 0:
            self.is_on = True
        return f"Fan in {self.location} speed set to {self.speed}", old_speed

# Concrete commands
class LightOnCommand(Command):
    def __init__(self, light: Light):
        self.light = light
        self.previous_state = None

    def execute(self):
        self.previous_state = self.light.is_on
        return self.light.turn_on()

    def undo(self):
        if self.previous_state:
            return self.light.turn_on()
        else:
            return self.light.turn_off()

class LightOffCommand(Command):
    def __init__(self, light: Light):
        self.light = light
        self.previous_state = None

    def execute(self):
        self.previous_state = self.light.is_on
        return self.light.turn_off()

    def undo(self):
        if self.previous_state:
            return self.light.turn_on()
        else:
            return self.light.turn_off()

class SetBrightnessCommand(Command):
    def __init__(self, light: Light, brightness):
        self.light = light
        self.brightness = brightness
        self.previous_brightness = None

    def execute(self):
        result, self.previous_brightness = self.light.set_brightness(self.brightness)
        return result

    def undo(self):
        result, _ = self.light.set_brightness(self.previous_brightness)
        return f"Brightness restored to {self.previous_brightness}%"

class FanOnCommand(Command):
    def __init__(self, fan: Fan):
        self.fan = fan
        self.previous_state = None

    def execute(self):
        self.previous_state = (self.fan.is_on, self.fan.speed)
        return self.fan.turn_on()

    def undo(self):
        if self.previous_state[0]:
            return self.fan.turn_on()
        else:
            return self.fan.turn_off()[0]

class SetFanSpeedCommand(Command):
    def __init__(self, fan: Fan, speed):
        self.fan = fan
        self.speed = speed
        self.previous_speed = None

    def execute(self):
        result, self.previous_speed = self.fan.set_speed(self.speed)
        return result

    def undo(self):
        result, _ = self.fan.set_speed(self.previous_speed)
        return f"Fan speed restored to {self.previous_speed}"

# Macro command
class MacroCommand(Command):
    def __init__(self, commands: List[Command]):
        self.commands = commands

    def execute(self):
        results = []
        for command in self.commands:
            results.append(command.execute())
        return "Macro executed: " + "; ".join(results)

    def undo(self):
        results = []
        # Undo in reverse order
        for command in reversed(self.commands):
            results.append(command.undo())
        return "Macro undone: " + "; ".join(results)

# Null object pattern for empty slots
class NoCommand(Command):
    def execute(self):
        return "No command assigned"

    def undo(self):
        return "Nothing to undo"

# Invoker
class RemoteControl:
    def __init__(self, slots=7):
        self.on_commands = [NoCommand()] * slots
        self.off_commands = [NoCommand()] * slots
        self.undo_command = NoCommand()
        self.command_history = []

    def set_command(self, slot, on_command: Command, off_command: Command):
        self.on_commands[slot] = on_command
        self.off_commands[slot] = off_command

    def on_button_pressed(self, slot):
        result = self.on_commands[slot].execute()
        self.undo_command = self.on_commands[slot]
        self.command_history.append(self.on_commands[slot])
        return result

    def off_button_pressed(self, slot):
        result = self.off_commands[slot].execute()
        self.undo_command = self.off_commands[slot]
        self.command_history.append(self.off_commands[slot])
        return result

    def undo_button_pressed(self):
        result = self.undo_command.undo()
        return result

    def get_status(self):
        status = "Remote Control Status:\n"
        for i in range(len(self.on_commands)):
            status += f"Slot {i}: {self.on_commands[i].__class__.__name__} | {self.off_commands[i].__class__.__name__}\n"
        return status

# Advanced: Command with queuing and logging
class CommandQueue:
    def __init__(self):
        self.queue = []
        self.executed_commands = []

    def add_command(self, command: Command):
        self.queue.append(command)

    def execute_all(self):
        results = []
        while self.queue:
            command = self.queue.pop(0)
            result = command.execute()
            self.executed_commands.append(command)
            results.append(result)
        return results

    def undo_last(self):
        if self.executed_commands:
            command = self.executed_commands.pop()
            return command.undo()
        return "Nothing to undo"

# Usage
print("=== Remote Control Example ===")
# Create devices
living_room_light = Light("Living Room")
bedroom_light = Light("Bedroom")
ceiling_fan = Fan("Living Room")

# Create commands
living_room_light_on = LightOnCommand(living_room_light)
living_room_light_off = LightOffCommand(living_room_light)
bedroom_light_on = LightOnCommand(bedroom_light)
bedroom_light_off = LightOffCommand(bedroom_light)
fan_on = FanOnCommand(ceiling_fan)
fan_speed_3 = SetFanSpeedCommand(ceiling_fan, 3)

# Set up remote
remote = RemoteControl()
remote.set_command(0, living_room_light_on, living_room_light_off)
remote.set_command(1, bedroom_light_on, bedroom_light_off)
remote.set_command(2, fan_on, NoCommand())

print(remote.get_status())

# Use remote
print(remote.on_button_pressed(0))   # Living room light on
print(remote.on_button_pressed(1))   # Bedroom light on
print(remote.on_button_pressed(2))   # Fan on
print(remote.undo_button_pressed())  # Undo last command

print("\n=== Macro Command Example ===")
# Create a party mode macro
party_commands = [
    LightOnCommand(living_room_light),
    LightOnCommand(bedroom_light),
    SetBrightnessCommand(living_room_light, 80),
    SetFanSpeedCommand(ceiling_fan, 2)
]

party_macro = MacroCommand(party_commands)
print(party_macro.execute())
print(party_macro.undo())

print("\n=== Command Queue Example ===")
queue = CommandQueue()
queue.add_command(LightOnCommand(living_room_light))
queue.add_command(SetBrightnessCommand(living_room_light, 60))
queue.add_command(FanOnCommand(ceiling_fan))

results = queue.execute_all()
for result in results:
    print(result)

print(queue.undo_last())
```

### When to Use Command Pattern
- ✅ Parameterize objects with operations
- ✅ Queue, schedule, or log requests
- ✅ Support undo operations
- ✅ Decouple invoker from receiver

## 🔗 Chain of Responsibility Pattern

### Problem
Need to process requests through a chain of handlers without coupling sender to receiver.

### Solution
Pass requests along a chain of potential handlers until one handles it.

```python
from abc import ABC, abstractmethod
from enum import Enum
import logging

# Request types
class RequestType(Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    GENERAL = "general"
    ESCALATION = "escalation"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

# Request class
class SupportRequest:
    def __init__(self, request_type: RequestType, priority: Priority, description: str, customer_id: str):
        self.request_type = request_type
        self.priority = priority
        self.description = description
        self.customer_id = customer_id
        self.handled_by = None
        self.resolution = None

    def __str__(self):
        return f"Request({self.request_type.value}, {self.priority.name}, '{self.description}', {self.customer_id})"

# Handler interface
class SupportHandler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    @abstractmethod
    def can_handle(self, request: SupportRequest) -> bool:
        pass

    @abstractmethod
    def handle_request(self, request: SupportRequest) -> str:
        pass

    def handle(self, request: SupportRequest) -> str:
        if self.can_handle(request):
            result = self.handle_request(request)
            request.handled_by = self.__class__.__name__
            return result
        elif self._next_handler:
            return self._next_handler.handle(request)
        else:
            return f"Request could not be handled: {request}"

# Concrete handlers
class Level1SupportHandler(SupportHandler):
    def can_handle(self, request: SupportRequest) -> bool:
        return (request.request_type == RequestType.GENERAL and
                request.priority in [Priority.LOW, Priority.MEDIUM])

    def handle_request(self, request: SupportRequest) -> str:
        request.resolution = "Provided general information and basic troubleshooting"
        return f"Level 1 Support handled: {request.description}"

class TechnicalSupportHandler(SupportHandler):
    def can_handle(self, request: SupportRequest) -> bool:
        return (request.request_type == RequestType.TECHNICAL and
                request.priority != Priority.CRITICAL)

    def handle_request(self, request: SupportRequest) -> str:
        request.resolution = "Provided technical solution and configuration help"
        return f"Technical Support handled: {request.description}"

class BillingSupportHandler(SupportHandler):
    def can_handle(self, request: SupportRequest) -> bool:
        return request.request_type == RequestType.BILLING

    def handle_request(self, request: SupportRequest) -> str:
        request.resolution = "Resolved billing inquiry and updated account"
        return f"Billing Support handled: {request.description}"

class ManagerHandler(SupportHandler):
    def can_handle(self, request: SupportRequest) -> bool:
        return (request.priority == Priority.HIGH or
                request.request_type == RequestType.ESCALATION)

    def handle_request(self, request: SupportRequest) -> str:
        request.resolution = "Manager reviewed case and provided escalated support"
        return f"Manager handled: {request.description}"

class DirectorHandler(SupportHandler):
    def can_handle(self, request: SupportRequest) -> bool:
        return request.priority == Priority.CRITICAL

    def handle_request(self, request: SupportRequest) -> str:
        request.resolution = "Director personally addressed critical issue"
        return f"Director handled: {request.description}"

# Advanced example: Middleware chain for web requests
class WebRequest:
    def __init__(self, path: str, method: str, headers: dict, body: str = ""):
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body
        self.user = None
        self.authenticated = False
        self.authorized = False
        self.rate_limited = False

class Middleware(ABC):
    def __init__(self):
        self._next = None

    def set_next(self, middleware):
        self._next = middleware
        return middleware

    @abstractmethod
    def process(self, request: WebRequest) -> tuple[bool, str]:
        """Returns (continue_processing, message)"""
        pass

    def handle(self, request: WebRequest) -> tuple[bool, str]:
        can_continue, message = self.process(request)
        if can_continue and self._next:
            return self._next.handle(request)
        return can_continue, message

class AuthenticationMiddleware(Middleware):
    def __init__(self):
        super().__init__()
        self.valid_tokens = {"token123": "user1", "token456": "user2"}

    def process(self, request: WebRequest) -> tuple[bool, str]:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False, "Missing or invalid authorization header"

        token = auth_header[7:]  # Remove "Bearer " prefix
        if token in self.valid_tokens:
            request.user = self.valid_tokens[token]
            request.authenticated = True
            return True, "Authentication successful"

        return False, "Invalid token"

class AuthorizationMiddleware(Middleware):
    def __init__(self):
        super().__init__()
        self.user_permissions = {
            "user1": ["/api/read", "/api/write"],
            "user2": ["/api/read"]
        }

    def process(self, request: WebRequest) -> tuple[bool, str]:
        if not request.authenticated:
            return False, "User not authenticated"

        user_perms = self.user_permissions.get(request.user, [])
        if request.path in user_perms:
            request.authorized = True
            return True, "Authorization successful"

        return False, f"User {request.user} not authorized for {request.path}"

class RateLimitMiddleware(Middleware):
    def __init__(self, max_requests_per_minute=60):
        super().__init__()
        self.max_requests = max_requests_per_minute
        self.request_counts = {}

    def process(self, request: WebRequest) -> tuple[bool, str]:
        if not request.authenticated:
            return True, "Rate limiting skipped for unauthenticated requests"

        user = request.user
        current_count = self.request_counts.get(user, 0)

        if current_count >= self.max_requests:
            request.rate_limited = True
            return False, f"Rate limit exceeded for user {user}"

        self.request_counts[user] = current_count + 1
        return True, "Rate limit check passed"

class LoggingMiddleware(Middleware):
    def process(self, request: WebRequest) -> tuple[bool, str]:
        log_message = f"Request: {request.method} {request.path} from user {request.user or 'anonymous'}"
        print(f"LOG: {log_message}")
        return True, "Request logged"

# Usage
print("=== Support Chain Example ===")

# Create the chain
level1 = Level1SupportHandler()
technical = TechnicalSupportHandler()
billing = BillingSupportHandler()
manager = ManagerHandler()
director = DirectorHandler()

# Build the chain
level1.set_next(technical).set_next(billing).set_next(manager).set_next(director)

# Create requests
requests = [
    SupportRequest(RequestType.GENERAL, Priority.LOW, "How do I reset my password?", "CUST001"),
    SupportRequest(RequestType.TECHNICAL, Priority.MEDIUM, "API returning 500 errors", "CUST002"),
    SupportRequest(RequestType.BILLING, Priority.HIGH, "Incorrect charges on invoice", "CUST003"),
    SupportRequest(RequestType.ESCALATION, Priority.HIGH, "Unsatisfied with previous resolution", "CUST004"),
    SupportRequest(RequestType.TECHNICAL, Priority.CRITICAL, "Production system down", "CUST005"),
]

# Process requests
for request in requests:
    print(f"\nProcessing: {request}")
    result = level1.handle(request)
    print(f"Result: {result}")
    print(f"Handled by: {request.handled_by}")
    print(f"Resolution: {request.resolution}")

print("\n=== Middleware Chain Example ===")

# Create middleware chain
auth = AuthenticationMiddleware()
authz = AuthorizationMiddleware()
rate_limit = RateLimitMiddleware(max_requests_per_minute=2)
logging_mw = LoggingMiddleware()

# Build the chain
logging_mw.set_next(auth).set_next(authz).set_next(rate_limit)

# Create requests
web_requests = [
    WebRequest("/api/read", "GET", {"Authorization": "Bearer token123"}),
    WebRequest("/api/write", "POST", {"Authorization": "Bearer token456"}),
    WebRequest("/api/read", "GET", {"Authorization": "Bearer token123"}),
    WebRequest("/api/read", "GET", {"Authorization": "Bearer invalid"}),
    WebRequest("/api/read", "GET", {"Authorization": "Bearer token123"}),  # Should be rate limited
]

# Process requests
for i, req in enumerate(web_requests, 1):
    print(f"\n--- Processing Request {i} ---")
    print(f"Request: {req.method} {req.path}")
    success, message = logging_mw.handle(req)
    print(f"Success: {success}")
    print(f"Message: {message}")
    if success:
        print("Request would be processed by application")
```

### When to Use Chain of Responsibility Pattern
- ✅ Multiple objects can handle a request
- ✅ Don't know which object should handle request in advance
- ✅ Want to decouple sender from receivers
- ✅ Need to process requests in a sequence

## ⚖️ Pattern Comparison

| Pattern | Purpose | When to Use | Complexity |
|---------|---------|-------------|------------|
| **Observer** | Notify multiple objects of changes | Loose coupling for updates | Medium |
| **Strategy** | Interchangeable algorithms | Multiple ways to do something | Low |
| **Command** | Encapsulate requests as objects | Undo, queue, parameterize | Medium |
| **Chain of Responsibility** | Pass requests through handlers | Multiple potential handlers | Medium |

## 🛠️ Practical Exercise

Create a document processing system using multiple behavioral patterns:

```python
# Your task: Implement a document processing system that:
# 1. Uses Observer for progress notifications during processing
# 2. Uses Strategy for different document formats (PDF, Word, Excel)
# 3. Uses Command for document operations (convert, compress, email)
# 4. Uses Chain of Responsibility for validation steps

class Document:
    def __init__(self, name, content, format_type):
        self.name = name
        self.content = content
        self.format_type = format_type

# Implement the patterns here...
```

## ✅ Knowledge Check

- [ ] Can implement Observer for loose coupling
- [ ] Understand Strategy for algorithm variations
- [ ] Know Command pattern for operations encapsulation
- [ ] Can build Chain of Responsibility for request processing
- [ ] Understand when to use each behavioral pattern

## 🚀 Next Steps

- Apply patterns in [Case Studies](../../case-studies/)
- Study [Real-World Examples](../../../04-real-world-examples/)
- Practice [Interview Questions](../../../05-interview-preparation/)