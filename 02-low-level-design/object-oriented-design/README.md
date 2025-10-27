# Object-Oriented Design Principles 🟢

## 🎯 Learning Objectives
- Master the four pillars of OOP
- Apply SOLID principles in real-world scenarios
- Design clean, maintainable class hierarchies
- Understand composition vs inheritance trade-offs

## 🏛️ The Four Pillars of OOP

### 1. Encapsulation

**Definition:** Bundling data and methods that operate on that data within a single unit, while restricting access to internal details.

```python
class BankAccount:
    def __init__(self, account_number, initial_balance=0):
        self._account_number = account_number  # Protected
        self.__balance = initial_balance       # Private
        self.__transaction_history = []        # Private

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self.__balance += amount
        self.__transaction_history.append(f"Deposited: ${amount}")
        return self.__balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.__balance:
            raise ValueError("Insufficient funds")

        self.__balance -= amount
        self.__transaction_history.append(f"Withdrew: ${amount}")
        return self.__balance

    def get_balance(self):
        return self.__balance

    def get_account_number(self):
        return self._account_number

    def get_transaction_history(self):
        return self.__transaction_history.copy()  # Return copy, not original

# Usage
account = BankAccount("123456789", 1000)
account.deposit(500)
print(f"Balance: ${account.get_balance()}")  # Balance: $1500

# These would raise AttributeError:
# print(account.__balance)  # Can't access private attribute
# account.__balance = 999999  # Can't modify private attribute
```

**Benefits:**
- Data protection and validation
- Controlled access to object state
- Easier maintenance and debugging
- Reduces coupling between components

### 2. Inheritance

**Definition:** A mechanism where a new class inherits properties and methods from an existing class.

```python
from abc import ABC, abstractmethod

class Animal(ABC):
    def __init__(self, name, species):
        self.name = name
        self.species = species
        self.energy = 100

    @abstractmethod
    def make_sound(self):
        pass

    @abstractmethod
    def move(self):
        pass

    def eat(self, food_energy):
        self.energy += food_energy
        print(f"{self.name} ate and gained {food_energy} energy")

    def sleep(self):
        self.energy = 100
        print(f"{self.name} slept and restored energy")

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name, "Canine")
        self.breed = breed
        self.loyalty = 100

    def make_sound(self):
        return "Woof! Woof!"

    def move(self):
        self.energy -= 10
        return f"{self.name} runs around energetically"

    def fetch(self, item):
        self.energy -= 5
        self.loyalty += 10
        return f"{self.name} fetched the {item}"

class Cat(Animal):
    def __init__(self, name, indoor=True):
        super().__init__(name, "Feline")
        self.indoor = indoor
        self.independence = 80

    def make_sound(self):
        return "Meow"

    def move(self):
        self.energy -= 5
        return f"{self.name} gracefully stalks around"

    def hunt(self):
        if not self.indoor:
            self.energy -= 15
            return f"{self.name} caught a mouse"
        return f"{self.name} hunts a toy mouse"

# Usage
dog = Dog("Buddy", "Golden Retriever")
cat = Cat("Whiskers", indoor=True)

print(dog.make_sound())  # Woof! Woof!
print(cat.make_sound())  # Meow
print(dog.fetch("ball"))  # Buddy fetched the ball
```

**Types of Inheritance:**

```python
# Single Inheritance
class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

class Car(Vehicle):
    def __init__(self, brand, model, doors):
        super().__init__(brand, model)
        self.doors = doors

# Multiple Inheritance
class Flyable:
    def fly(self):
        return "Flying through the air"

class Swimmable:
    def swim(self):
        return "Swimming in water"

class Duck(Animal, Flyable, Swimmable):
    def __init__(self, name):
        Animal.__init__(self, name, "Bird")

    def make_sound(self):
        return "Quack"

    def move(self):
        return "Waddles on land"

# Method Resolution Order (MRO)
duck = Duck("Donald")
print(Duck.__mro__)  # Shows inheritance chain
```

### 3. Polymorphism

**Definition:** The ability of objects of different types to be treated as instances of the same type through a common interface.

```python
from typing import List

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass

    @abstractmethod
    def draw(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def draw(self):
        return f"Drawing rectangle: {self.width}x{self.height}"

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius

    def draw(self):
        return f"Drawing circle with radius: {self.radius}"

class Triangle(Shape):
    def __init__(self, base, height, side1, side2, side3):
        self.base = base
        self.height = height
        self.side1 = side1
        self.side2 = side2
        self.side3 = side3

    def area(self):
        return 0.5 * self.base * self.height

    def perimeter(self):
        return self.side1 + self.side2 + self.side3

    def draw(self):
        return f"Drawing triangle with base: {self.base}"

# Polymorphic function
def calculate_total_area(shapes: List[Shape]) -> float:
    total = 0
    for shape in shapes:
        total += shape.area()  # Polymorphic call
        print(shape.draw())     # Polymorphic call
    return total

# Usage
shapes = [
    Rectangle(5, 10),
    Circle(7),
    Triangle(6, 8, 6, 8, 10),
    Rectangle(3, 4)
]

total_area = calculate_total_area(shapes)
print(f"Total area: {total_area}")
```

**Duck Typing in Python:**

```python
class Duck:
    def speak(self):
        return "Quack"

    def walk(self):
        return "Waddle waddle"

class Dog:
    def speak(self):
        return "Woof"

    def walk(self):
        return "Walk walk"

class Robot:
    def speak(self):
        return "Beep boop"

    def walk(self):
        return "Mechanical walking"

def animal_sounds(creatures):
    for creature in creatures:
        # If it walks like a duck and talks like a duck...
        print(f"Sound: {creature.speak()}")
        print(f"Movement: {creature.walk()}")

# Duck typing in action
creatures = [Duck(), Dog(), Robot()]
animal_sounds(creatures)  # Works for all objects with speak() and walk() methods
```

### 4. Abstraction

**Definition:** Hiding complex implementation details while exposing only essential features and functionalities.

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount, payment_details):
        pass

    @abstractmethod
    def refund_payment(self, transaction_id, amount):
        pass

    @abstractmethod
    def get_transaction_status(self, transaction_id):
        pass

class CreditCardProcessor(PaymentProcessor):
    def __init__(self, merchant_id, api_key):
        self.merchant_id = merchant_id
        self.api_key = api_key

    def process_payment(self, amount, payment_details):
        # Complex credit card processing logic
        card_number = payment_details['card_number']
        expiry = payment_details['expiry']
        cvv = payment_details['cvv']

        # Validate card details
        if not self._validate_card(card_number, expiry, cvv):
            return {"status": "failed", "message": "Invalid card details"}

        # Process with payment gateway
        transaction_id = self._call_payment_gateway(amount, payment_details)

        return {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": amount
        }

    def refund_payment(self, transaction_id, amount):
        # Refund logic
        return self._call_refund_api(transaction_id, amount)

    def get_transaction_status(self, transaction_id):
        # Status check logic
        return self._call_status_api(transaction_id)

    def _validate_card(self, card_number, expiry, cvv):
        # Private validation logic
        return len(card_number) == 16 and len(cvv) == 3

    def _call_payment_gateway(self, amount, details):
        # Simulate API call
        import uuid
        return str(uuid.uuid4())

    def _call_refund_api(self, transaction_id, amount):
        # Simulate refund API
        return {"status": "refunded", "amount": amount}

    def _call_status_api(self, transaction_id):
        # Simulate status API
        return {"status": "completed"}

class PayPalProcessor(PaymentProcessor):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def process_payment(self, amount, payment_details):
        # PayPal-specific processing
        email = payment_details['email']

        if not self._validate_paypal_account(email):
            return {"status": "failed", "message": "Invalid PayPal account"}

        transaction_id = self._paypal_api_call(amount, payment_details)

        return {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": amount
        }

    def refund_payment(self, transaction_id, amount):
        return self._paypal_refund(transaction_id, amount)

    def get_transaction_status(self, transaction_id):
        return self._paypal_status_check(transaction_id)

    def _validate_paypal_account(self, email):
        return "@" in email

    def _paypal_api_call(self, amount, details):
        import uuid
        return str(uuid.uuid4())

    def _paypal_refund(self, transaction_id, amount):
        return {"status": "refunded", "amount": amount}

    def _paypal_status_check(self, transaction_id):
        return {"status": "completed"}

# Client code using abstraction
class ECommerceSystem:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor

    def checkout(self, cart_total, payment_details):
        # Client doesn't need to know payment processing details
        result = self.payment_processor.process_payment(cart_total, payment_details)

        if result["status"] == "success":
            return f"Payment successful! Transaction ID: {result['transaction_id']}"
        else:
            return f"Payment failed: {result['message']}"

# Usage - abstraction in action
credit_card_processor = CreditCardProcessor("merchant123", "api_key_456")
paypal_processor = PayPalProcessor("client_id_789", "secret_abc")

ecommerce_cc = ECommerceSystem(credit_card_processor)
ecommerce_pp = ECommerceSystem(paypal_processor)

# Same interface, different implementations
cc_result = ecommerce_cc.checkout(99.99, {
    "card_number": "1234567890123456",
    "expiry": "12/25",
    "cvv": "123"
})

pp_result = ecommerce_pp.checkout(99.99, {
    "email": "user@example.com"
})
```

## 🔧 SOLID Principles

### 1. Single Responsibility Principle (SRP)

**"A class should have only one reason to change."**

❌ **Bad Example:**
```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def save_to_database(self):
        # Database logic
        pass

    def send_email(self, message):
        # Email logic
        pass

    def validate_email(self):
        # Validation logic
        pass

    def generate_report(self):
        # Reporting logic
        pass
```

✅ **Good Example:**
```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

class UserRepository:
    def save(self, user):
        # Database logic
        print(f"Saving user {user.name} to database")

    def find_by_email(self, email):
        # Database query logic
        pass

class EmailService:
    def send_email(self, user, message):
        # Email logic
        print(f"Sending email to {user.email}: {message}")

class EmailValidator:
    @staticmethod
    def is_valid(email):
        return "@" in email and "." in email

class UserReportGenerator:
    def generate_report(self, users):
        # Reporting logic
        return f"Report for {len(users)} users"

# Usage
user = User("John Doe", "john@example.com")
repository = UserRepository()
email_service = EmailService()
validator = EmailValidator()

if validator.is_valid(user.email):
    repository.save(user)
    email_service.send_email(user, "Welcome!")
```

### 2. Open/Closed Principle (OCP)

**"Software entities should be open for extension, but closed for modification."**

❌ **Bad Example:**
```python
class AreaCalculator:
    def calculate_area(self, shapes):
        total_area = 0
        for shape in shapes:
            if shape.type == "rectangle":
                total_area += shape.width * shape.height
            elif shape.type == "circle":
                total_area += 3.14159 * shape.radius ** 2
            # Need to modify this method for each new shape
        return total_area
```

✅ **Good Example:**
```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

class Triangle(Shape):  # New shape - no modification needed to AreaCalculator
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height

class AreaCalculator:
    def calculate_area(self, shapes):
        return sum(shape.area() for shape in shapes)

# Usage
shapes = [
    Rectangle(5, 10),
    Circle(7),
    Triangle(6, 8)  # Works without modifying AreaCalculator
]

calculator = AreaCalculator()
total_area = calculator.calculate_area(shapes)
```

### 3. Liskov Substitution Principle (LSP)

**"Objects of a superclass should be replaceable with objects of its subclasses without breaking the application."**

❌ **Bad Example:**
```python
class Bird:
    def fly(self):
        return "Flying"

class Penguin(Bird):
    def fly(self):
        raise Exception("Penguins can't fly!")  # Violates LSP

def make_bird_fly(bird: Bird):
    return bird.fly()  # This will fail with Penguin

# This breaks:
# penguin = Penguin()
# make_bird_fly(penguin)  # Exception!
```

✅ **Good Example:**
```python
from abc import ABC, abstractmethod

class Bird(ABC):
    @abstractmethod
    def move(self):
        pass

class FlyingBird(Bird):
    @abstractmethod
    def fly(self):
        pass

    def move(self):
        return self.fly()

class SwimmingBird(Bird):
    @abstractmethod
    def swim(self):
        pass

    def move(self):
        return self.swim()

class Eagle(FlyingBird):
    def fly(self):
        return "Eagle soaring high"

class Penguin(SwimmingBird):
    def swim(self):
        return "Penguin swimming gracefully"

class Duck(FlyingBird, SwimmingBird):
    def fly(self):
        return "Duck flying"

    def swim(self):
        return "Duck swimming"

    def move(self):
        return f"{self.fly()} and {self.swim()}"

def make_bird_move(bird: Bird):
    return bird.move()

# All work correctly
eagle = Eagle()
penguin = Penguin()
duck = Duck()

print(make_bird_move(eagle))    # Eagle soaring high
print(make_bird_move(penguin))  # Penguin swimming gracefully
print(make_bird_move(duck))     # Duck flying and Duck swimming
```

### 4. Interface Segregation Principle (ISP)

**"Many client-specific interfaces are better than one general-purpose interface."**

❌ **Bad Example:**
```python
class Worker:
    def work(self):
        pass

    def eat(self):
        pass

    def sleep(self):
        pass

class Human(Worker):
    def work(self):
        return "Human working"

    def eat(self):
        return "Human eating"

    def sleep(self):
        return "Human sleeping"

class Robot(Worker):
    def work(self):
        return "Robot working"

    def eat(self):
        # Robots don't eat! But forced to implement
        raise NotImplementedError("Robots don't eat")

    def sleep(self):
        # Robots don't sleep! But forced to implement
        raise NotImplementedError("Robots don't sleep")
```

✅ **Good Example:**
```python
from abc import ABC, abstractmethod

class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat(self):
        pass

class Sleepable(ABC):
    @abstractmethod
    def sleep(self):
        pass

class Human(Workable, Eatable, Sleepable):
    def work(self):
        return "Human working"

    def eat(self):
        return "Human eating"

    def sleep(self):
        return "Human sleeping"

class Robot(Workable):  # Only implements what it needs
    def work(self):
        return "Robot working"

class Manager:
    def manage_workers(self, workers: list[Workable]):
        for worker in workers:
            print(worker.work())

    def manage_lunch(self, eaters: list[Eatable]):
        for eater in eaters:
            print(eater.eat())

# Usage
human = Human()
robot = Robot()

manager = Manager()
manager.manage_workers([human, robot])  # Both can work
manager.manage_lunch([human])           # Only human can eat
```

### 5. Dependency Inversion Principle (DIP)

**"Depend upon abstractions, not concretions."**

❌ **Bad Example:**
```python
class MySQLDatabase:
    def save(self, data):
        print(f"Saving {data} to MySQL")

class UserService:
    def __init__(self):
        self.database = MySQLDatabase()  # Tight coupling

    def create_user(self, user_data):
        # Business logic
        processed_data = self.process_user_data(user_data)
        self.database.save(processed_data)

    def process_user_data(self, user_data):
        return f"Processed: {user_data}"
```

✅ **Good Example:**
```python
from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def find(self, id):
        pass

class MySQLDatabase(DatabaseInterface):
    def save(self, data):
        print(f"Saving {data} to MySQL")

    def find(self, id):
        return f"Found user {id} in MySQL"

class PostgreSQLDatabase(DatabaseInterface):
    def save(self, data):
        print(f"Saving {data} to PostgreSQL")

    def find(self, id):
        return f"Found user {id} in PostgreSQL"

class MongoDatabase(DatabaseInterface):
    def save(self, data):
        print(f"Saving {data} to MongoDB")

    def find(self, id):
        return f"Found user {id} in MongoDB"

class UserService:
    def __init__(self, database: DatabaseInterface):
        self.database = database  # Depends on abstraction

    def create_user(self, user_data):
        processed_data = self.process_user_data(user_data)
        self.database.save(processed_data)

    def get_user(self, user_id):
        return self.database.find(user_id)

    def process_user_data(self, user_data):
        return f"Processed: {user_data}"

# Dependency Injection
mysql_db = MySQLDatabase()
postgres_db = PostgreSQLDatabase()
mongo_db = MongoDatabase()

# Same service, different databases
user_service_mysql = UserService(mysql_db)
user_service_postgres = UserService(postgres_db)
user_service_mongo = UserService(mongo_db)

# All work the same way
user_service_mysql.create_user("John Doe")
user_service_postgres.create_user("Jane Smith")
user_service_mongo.create_user("Bob Johnson")
```

## 🏗️ Design Patterns Integration

### Factory Pattern with OOP

```python
class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type, **kwargs):
        if vehicle_type == "car":
            return Car(**kwargs)
        elif vehicle_type == "motorcycle":
            return Motorcycle(**kwargs)
        elif vehicle_type == "truck":
            return Truck(**kwargs)
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")

class Vehicle(ABC):
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    @abstractmethod
    def start_engine(self):
        pass

class Car(Vehicle):
    def __init__(self, brand, model, doors):
        super().__init__(brand, model)
        self.doors = doors

    def start_engine(self):
        return f"Car {self.brand} {self.model} engine started"

class Motorcycle(Vehicle):
    def __init__(self, brand, model, engine_size):
        super().__init__(brand, model)
        self.engine_size = engine_size

    def start_engine(self):
        return f"Motorcycle {self.brand} {self.model} engine started"

# Usage
car = VehicleFactory.create_vehicle("car", brand="Toyota", model="Camry", doors=4)
motorcycle = VehicleFactory.create_vehicle("motorcycle", brand="Honda", model="CBR", engine_size="600cc")
```

## ✅ Knowledge Check

After studying this section, you should be able to:

- [ ] Explain and implement the four pillars of OOP
- [ ] Apply all five SOLID principles
- [ ] Design proper class hierarchies
- [ ] Choose between composition and inheritance
- [ ] Create maintainable and extensible code

## 🔄 Next Steps

- Practice implementing SOLID principles in real projects
- Study [Design Patterns](../design-patterns/) that leverage OOP concepts
- Learn [Case Studies](../case-studies/) that demonstrate OOP in action
- Explore [Data Structures Implementation](../data-structures-implementation/) using OOP principles