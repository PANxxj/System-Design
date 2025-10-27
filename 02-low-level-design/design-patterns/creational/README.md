# Creational Design Patterns 🟡

## 🎯 Learning Objectives
- Master creational patterns for object instantiation
- Understand when and how to apply each pattern
- Implement patterns with practical examples
- Avoid common anti-patterns and pitfalls

## 📖 Overview

Creational patterns deal with object creation mechanisms, trying to create objects in a manner suitable to the situation. They help make systems independent of how objects are created, composed, and represented.

## 🏭 Factory Pattern

### Problem
Creating objects directly couples code to specific classes, making it hard to change or extend.

### Solution
Use a factory to create objects, hiding the creation logic.

```python
from abc import ABC, abstractmethod

# Product interface
class Vehicle(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

# Concrete products
class Car(Vehicle):
    def start(self):
        return "Car engine started"

    def stop(self):
        return "Car engine stopped"

class Motorcycle(Vehicle):
    def start(self):
        return "Motorcycle engine started"

    def stop(self):
        return "Motorcycle engine stopped"

class Truck(Vehicle):
    def start(self):
        return "Truck engine started"

    def stop(self):
        return "Truck engine stopped"

# Factory
class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type: str) -> Vehicle:
        if vehicle_type.lower() == "car":
            return Car()
        elif vehicle_type.lower() == "motorcycle":
            return Motorcycle()
        elif vehicle_type.lower() == "truck":
            return Truck()
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")

# Usage
factory = VehicleFactory()
car = factory.create_vehicle("car")
print(car.start())  # "Car engine started"

motorcycle = factory.create_vehicle("motorcycle")
print(motorcycle.start())  # "Motorcycle engine started"
```

### When to Use Factory Pattern
- ✅ When you have multiple similar classes
- ✅ When object creation is complex
- ✅ When you need to decouple creation from usage
- ✅ When you want to centralize object creation logic

## 🏗️ Builder Pattern

### Problem
Creating complex objects with many optional parameters leads to constructor telescoping.

### Solution
Use a builder to construct objects step by step.

```python
class Pizza:
    def __init__(self):
        self.size = None
        self.crust = None
        self.toppings = []
        self.cheese = None
        self.sauce = None

    def __str__(self):
        return f"Pizza(size={self.size}, crust={self.crust}, toppings={self.toppings}, cheese={self.cheese}, sauce={self.sauce})"

class PizzaBuilder:
    def __init__(self):
        self.pizza = Pizza()

    def set_size(self, size):
        self.pizza.size = size
        return self

    def set_crust(self, crust):
        self.pizza.crust = crust
        return self

    def add_topping(self, topping):
        self.pizza.toppings.append(topping)
        return self

    def set_cheese(self, cheese):
        self.pizza.cheese = cheese
        return self

    def set_sauce(self, sauce):
        self.pizza.sauce = sauce
        return self

    def build(self):
        # Validation can be done here
        if not self.pizza.size:
            raise ValueError("Pizza size must be specified")
        if not self.pizza.crust:
            raise ValueError("Pizza crust must be specified")
        return self.pizza

# Director (optional)
class PizzaDirector:
    def __init__(self, builder):
        self.builder = builder

    def make_margherita(self):
        return (self.builder
                .set_size("medium")
                .set_crust("thin")
                .set_sauce("tomato")
                .set_cheese("mozzarella")
                .add_topping("basil")
                .build())

    def make_pepperoni(self):
        return (self.builder
                .set_size("large")
                .set_crust("thick")
                .set_sauce("tomato")
                .set_cheese("mozzarella")
                .add_topping("pepperoni")
                .build())

# Usage
builder = PizzaBuilder()
director = PizzaDirector(builder)

# Using director
margherita = director.make_margherita()
print(margherita)

# Using builder directly
custom_pizza = (PizzaBuilder()
                .set_size("small")
                .set_crust("thin")
                .add_topping("mushrooms")
                .add_topping("olives")
                .set_cheese("parmesan")
                .build())
print(custom_pizza)
```

### When to Use Builder Pattern
- ✅ Complex object construction with many parameters
- ✅ Want to create different representations of the same object
- ✅ Construction process must allow different representations
- ✅ Want to isolate complex construction code

## 🔒 Singleton Pattern

### Problem
Need exactly one instance of a class (database connection, logger, config).

### Solution
Ensure only one instance exists and provide global access.

```python
import threading

class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.connection_string = "database://localhost:5432"
            self.initialized = True

    def connect(self):
        return f"Connected to {self.connection_string}"

    def execute_query(self, query):
        return f"Executing: {query}"

# Thread-safe Singleton with metaclass
class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

class Logger(metaclass=SingletonMeta):
    def __init__(self):
        self.log_level = "INFO"

    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")

# Usage
db1 = DatabaseConnection()
db2 = DatabaseConnection()
print(db1 is db2)  # True - same instance

logger1 = Logger()
logger2 = Logger()
print(logger1 is logger2)  # True - same instance
```

### Singleton Alternatives (Recommended)

```python
# Option 1: Module-level instance (Pythonic)
class _DatabaseConnection:
    def __init__(self):
        self.connection_string = "database://localhost:5432"

    def connect(self):
        return f"Connected to {self.connection_string}"

# Create single instance at module level
database_connection = _DatabaseConnection()

# Option 2: Dependency injection
class UserService:
    def __init__(self, db_connection, logger):
        self.db = db_connection
        self.logger = logger

    def create_user(self, user_data):
        self.logger.log("Creating user")
        return self.db.execute_query(f"INSERT INTO users VALUES {user_data}")

# Usage with dependency injection
db = DatabaseConnection()
logger = Logger()
user_service = UserService(db, logger)
```

### When to Use Singleton Pattern
- ✅ Need exactly one instance (rare)
- ✅ Global access point required
- ⚠️ **Warning**: Often considered an anti-pattern
- ⚠️ **Better alternatives**: Dependency injection, module-level instances

## 🖨️ Prototype Pattern

### Problem
Creating objects is expensive, or you want to create objects based on existing instances.

### Solution
Clone existing objects instead of creating new ones.

```python
import copy
from abc import ABC, abstractmethod

class Prototype(ABC):
    @abstractmethod
    def clone(self):
        pass

class Character(Prototype):
    def __init__(self, name, character_class, level=1):
        self.name = name
        self.character_class = character_class
        self.level = level
        self.equipment = []
        self.skills = {}

    def clone(self):
        # Deep copy to avoid shared references
        return copy.deepcopy(self)

    def add_equipment(self, item):
        self.equipment.append(item)

    def add_skill(self, skill_name, level):
        self.skills[skill_name] = level

    def __str__(self):
        return f"Character(name={self.name}, class={self.character_class}, level={self.level}, equipment={self.equipment})"

# Character templates
class CharacterTemplates:
    def __init__(self):
        self.templates = {}

    def register_template(self, name, character):
        self.templates[name] = character

    def create_character(self, template_name, character_name):
        if template_name not in self.templates:
            raise ValueError(f"Template {template_name} not found")

        # Clone the template and customize
        new_character = self.templates[template_name].clone()
        new_character.name = character_name
        return new_character

# Usage
templates = CharacterTemplates()

# Create base templates
warrior_template = Character("Template", "Warrior", level=10)
warrior_template.add_equipment("sword")
warrior_template.add_equipment("shield")
warrior_template.add_skill("combat", 8)

mage_template = Character("Template", "Mage", level=10)
mage_template.add_equipment("staff")
mage_template.add_equipment("robe")
mage_template.add_skill("magic", 9)

# Register templates
templates.register_template("warrior", warrior_template)
templates.register_template("mage", mage_template)

# Create new characters from templates
player1 = templates.create_character("warrior", "Conan")
player2 = templates.create_character("mage", "Gandalf")

print(player1)
print(player2)

# Verify they're independent objects
player1.add_equipment("helmet")
print(f"Player1 equipment: {player1.equipment}")
print(f"Player2 equipment: {player2.equipment}")  # Unchanged
```

### When to Use Prototype Pattern
- ✅ Object creation is expensive
- ✅ Want to avoid subclassing
- ✅ Creating objects from templates
- ✅ Runtime object configuration

## 🎯 Abstract Factory Pattern

### Problem
Need to create families of related objects without specifying their concrete classes.

### Solution
Provide interface for creating families of related objects.

```python
from abc import ABC, abstractmethod

# Abstract products
class Button(ABC):
    @abstractmethod
    def render(self):
        pass

class Checkbox(ABC):
    @abstractmethod
    def render(self):
        pass

# Concrete products for Windows
class WindowsButton(Button):
    def render(self):
        return "Rendering Windows-style button"

class WindowsCheckbox(Checkbox):
    def render(self):
        return "Rendering Windows-style checkbox"

# Concrete products for Mac
class MacButton(Button):
    def render(self):
        return "Rendering Mac-style button"

class MacCheckbox(Checkbox):
    def render(self):
        return "Rendering Mac-style checkbox"

# Abstract factory
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button:
        pass

    @abstractmethod
    def create_checkbox(self) -> Checkbox:
        pass

# Concrete factories
class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()

    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

# Client code
class Application:
    def __init__(self, factory: GUIFactory):
        self.factory = factory
        self.button = self.factory.create_button()
        self.checkbox = self.factory.create_checkbox()

    def render_ui(self):
        return f"{self.button.render()}, {self.checkbox.render()}"

# Factory selection
def get_factory(platform: str) -> GUIFactory:
    if platform.lower() == "windows":
        return WindowsFactory()
    elif platform.lower() == "mac":
        return MacFactory()
    else:
        raise ValueError(f"Unknown platform: {platform}")

# Usage
platform = "windows"  # Could come from environment
factory = get_factory(platform)
app = Application(factory)
print(app.render_ui())
```

### When to Use Abstract Factory Pattern
- ✅ Need to create families of related objects
- ✅ Want to ensure objects work together
- ✅ Need to support multiple product lines
- ✅ Want to decouple from concrete implementations

## ⚖️ Pattern Comparison

| Pattern | Purpose | When to Use | Complexity |
|---------|---------|-------------|------------|
| **Factory** | Create single objects | Simple object creation | Low |
| **Abstract Factory** | Create families of objects | Multiple related products | Medium |
| **Builder** | Construct complex objects | Many parameters/configurations | Medium |
| **Singleton** | Ensure single instance | Global state (use sparingly) | Low |
| **Prototype** | Clone existing objects | Expensive creation/templates | Low |

## 🛠️ Practical Exercise

Create a document processing system using multiple creational patterns:

```python
# Your task: Implement a document processing system that:
# 1. Uses Factory pattern to create different document types (PDF, Word, Excel)
# 2. Uses Builder pattern to construct documents with various formatting options
# 3. Uses Prototype pattern for document templates
# 4. Avoids Singleton but manages shared resources properly

class Document:
    def __init__(self):
        self.title = ""
        self.content = ""
        self.format_options = {}

    def __str__(self):
        return f"Document(title={self.title}, format={self.format_options})"

# Implement the patterns here...
```

## ✅ Knowledge Check

- [ ] Can implement Factory pattern for object creation
- [ ] Understand when Builder pattern is better than constructors
- [ ] Know the problems with Singleton and better alternatives
- [ ] Can use Prototype for object cloning
- [ ] Understand Abstract Factory for product families

## 🚀 Next Steps

- Study [Structural Patterns](../structural/) for object composition
- Practice [Behavioral Patterns](../behavioral/) for object interaction
- Apply patterns in [Case Studies](../../case-studies/)