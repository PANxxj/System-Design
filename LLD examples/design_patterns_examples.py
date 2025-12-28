"""
Low Level Design Patterns - Comprehensive Examples
==================================================
This file demonstrates various design patterns with practical examples.
Each pattern is explained with Todo application examples for easy understanding.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import threading
import copy


# =============================================================================
# 1. REPOSITORY PATTERN
# =============================================================================
"""
Repository Pattern:
- Separates data access logic from business logic
- Provides abstraction over data storage
- Makes it easy to switch between different storage mechanisms
- Centralizes data access code

Benefits:
- Single source of truth for data operations
- Easy to mock for testing
- Can switch from in-memory to database without changing business logic
"""

class TodoEntity:
    """Domain entity representing a Todo item"""
    def __init__(self, todo_id: str, title: str, description: str = ""):
        self.id = todo_id
        self.title = title
        self.description = description
        self.is_completed = False
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class ITodoRepository(ABC):
    """Repository interface - abstraction over data storage"""
    @abstractmethod
    def save(self, todo: TodoEntity) -> TodoEntity:
        pass

    @abstractmethod
    def find_by_id(self, todo_id: str) -> Optional[TodoEntity]:
        pass

    @abstractmethod
    def find_all(self) -> List[TodoEntity]:
        pass

    @abstractmethod
    def delete(self, todo_id: str) -> bool:
        pass


class InMemoryTodoRepository(ITodoRepository):
    """Concrete implementation using in-memory storage"""
    def __init__(self):
        self._storage: Dict[str, TodoEntity] = {}

    def save(self, todo: TodoEntity) -> TodoEntity:
        todo.updated_at = datetime.now()
        self._storage[todo.id] = todo
        return todo

    def find_by_id(self, todo_id: str) -> Optional[TodoEntity]:
        return self._storage.get(todo_id)

    def find_all(self) -> List[TodoEntity]:
        return list(self._storage.values())

    def delete(self, todo_id: str) -> bool:
        if todo_id in self._storage:
            del self._storage[todo_id]
            return True
        return False


class DatabaseTodoRepository(ITodoRepository):
    """Concrete implementation using database (simulated)"""
    def __init__(self, connection_string: str):
        self.connection = connection_string
        self._db: Dict[str, TodoEntity] = {}  # Simulated DB

    def save(self, todo: TodoEntity) -> TodoEntity:
        print(f"[DB] Saving to database: {self.connection}")
        todo.updated_at = datetime.now()
        self._db[todo.id] = todo
        return todo

    def find_by_id(self, todo_id: str) -> Optional[TodoEntity]:
        print(f"[DB] Querying database: {self.connection}")
        return self._db.get(todo_id)

    def find_all(self) -> List[TodoEntity]:
        print(f"[DB] Fetching all from database")
        return list(self._db.values())

    def delete(self, todo_id: str) -> bool:
        print(f"[DB] Deleting from database")
        if todo_id in self._db:
            del self._db[todo_id]
            return True
        return False


# =============================================================================
# 2. SINGLETON PATTERN
# =============================================================================
"""
Singleton Pattern:
- Ensures only one instance of a class exists
- Provides global access point to that instance
- Useful for: configuration, logging, connection pools, caches

Use Cases:
- Database connections
- Configuration managers
- Logger instances
- Cache managers
"""

class TodoConfigManager:
    """Singleton for managing application configuration"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not self._initialized:
            self.config = {
                "max_todos": 100,
                "auto_save": True,
                "default_priority": "medium",
                "app_name": "Todo Manager"
            }
            self._initialized = True

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value


class TodoLogger:
    """Singleton logger for Todo application"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logs = []
        return cls._instance

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def get_logs(self) -> List[str]:
        return self.logs


# =============================================================================
# 3. FACTORY PATTERN
# =============================================================================
"""
Factory Pattern:
- Creates objects without exposing creation logic
- Refers to newly created object through common interface
- Centralizes object creation logic

Benefits:
- Loose coupling between creator and concrete products
- Easy to add new types without modifying existing code
- Encapsulates complex creation logic
"""

class TodoPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class BaseTodo(ABC):
    """Base class for different types of todos"""
    def __init__(self, todo_id: str, title: str):
        self.id = todo_id
        self.title = title
        self.created_at = datetime.now()

    @abstractmethod
    def get_priority_level(self) -> TodoPriority:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass


class SimpleTodo(BaseTodo):
    """Simple todo with low priority"""
    def get_priority_level(self) -> TodoPriority:
        return TodoPriority.LOW

    def get_description(self) -> str:
        return f"Simple task: {self.title}"


class UrgentTodo(BaseTodo):
    """Urgent todo with deadline"""
    def __init__(self, todo_id: str, title: str, deadline: datetime):
        super().__init__(todo_id, title)
        self.deadline = deadline

    def get_priority_level(self) -> TodoPriority:
        return TodoPriority.URGENT

    def get_description(self) -> str:
        return f"URGENT: {self.title} (Due: {self.deadline.strftime('%Y-%m-%d')})"


class RecurringTodo(BaseTodo):
    """Recurring todo with frequency"""
    def __init__(self, todo_id: str, title: str, frequency: str):
        super().__init__(todo_id, title)
        self.frequency = frequency  # daily, weekly, monthly

    def get_priority_level(self) -> TodoPriority:
        return TodoPriority.MEDIUM

    def get_description(self) -> str:
        return f"Recurring ({self.frequency}): {self.title}"


class TodoFactory:
    """Factory class to create different types of todos"""

    @staticmethod
    def create_todo(todo_type: str, todo_id: str, title: str, **kwargs) -> BaseTodo:
        """
        Factory method to create todos based on type

        Args:
            todo_type: Type of todo (simple, urgent, recurring)
            todo_id: Unique identifier
            title: Todo title
            **kwargs: Additional parameters based on type
        """
        if todo_type == "simple":
            return SimpleTodo(todo_id, title)
        elif todo_type == "urgent":
            deadline = kwargs.get("deadline", datetime.now())
            return UrgentTodo(todo_id, title, deadline)
        elif todo_type == "recurring":
            frequency = kwargs.get("frequency", "daily")
            return RecurringTodo(todo_id, title, frequency)
        else:
            raise ValueError(f"Unknown todo type: {todo_type}")


# =============================================================================
# 4. BUILDER PATTERN
# =============================================================================
"""
Builder Pattern:
- Separates construction of complex object from its representation
- Allows step-by-step construction of complex objects
- Same construction process can create different representations

Benefits:
- Fluent interface for object creation
- Creates immutable objects easily
- Complex construction logic is isolated
- Different builders can produce different representations
"""

class TodoTask:
    """Complex Todo object with many optional fields"""
    def __init__(self):
        self.id: Optional[str] = None
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.priority: TodoPriority = TodoPriority.MEDIUM
        self.tags: List[str] = []
        self.assignee: Optional[str] = None
        self.due_date: Optional[datetime] = None
        self.estimated_hours: Optional[float] = None
        self.subtasks: List[str] = []

    def __str__(self):
        return f"Todo: {self.title} (Priority: {self.priority.name}, Tags: {self.tags})"


class TodoBuilder:
    """Builder for constructing Todo objects step by step"""

    def __init__(self):
        self._todo = TodoTask()

    def with_id(self, todo_id: str):
        """Set the todo ID"""
        self._todo.id = todo_id
        return self

    def with_title(self, title: str):
        """Set the todo title"""
        self._todo.title = title
        return self

    def with_description(self, description: str):
        """Set the todo description"""
        self._todo.description = description
        return self

    def with_priority(self, priority: TodoPriority):
        """Set the priority level"""
        self._todo.priority = priority
        return self

    def add_tag(self, tag: str):
        """Add a tag"""
        self._todo.tags.append(tag)
        return self

    def add_tags(self, tags: List[str]):
        """Add multiple tags"""
        self._todo.tags.extend(tags)
        return self

    def assign_to(self, assignee: str):
        """Assign to a person"""
        self._todo.assignee = assignee
        return self

    def with_due_date(self, due_date: datetime):
        """Set due date"""
        self._todo.due_date = due_date
        return self

    def with_estimated_hours(self, hours: float):
        """Set estimated hours"""
        self._todo.estimated_hours = hours
        return self

    def add_subtask(self, subtask: str):
        """Add a subtask"""
        self._todo.subtasks.append(subtask)
        return self

    def build(self) -> TodoTask:
        """Build and return the final todo object"""
        if not self._todo.id or not self._todo.title:
            raise ValueError("Todo must have ID and title")
        return self._todo


# =============================================================================
# 5. STRATEGY PATTERN
# =============================================================================
"""
Strategy Pattern:
- Defines family of algorithms, encapsulates each one
- Makes algorithms interchangeable
- Strategy lets algorithm vary independently from clients

Benefits:
- Eliminates conditional statements
- Easy to add new strategies
- Follows Open/Closed Principle
"""

class ISortStrategy(ABC):
    """Strategy interface for sorting todos"""
    @abstractmethod
    def sort(self, todos: List[TodoTask]) -> List[TodoTask]:
        pass


class SortByPriorityStrategy(ISortStrategy):
    """Sort todos by priority (high to low)"""
    def sort(self, todos: List[TodoTask]) -> List[TodoTask]:
        return sorted(todos, key=lambda t: t.priority.value, reverse=True)


class SortByDueDateStrategy(ISortStrategy):
    """Sort todos by due date (earliest first)"""
    def sort(self, todos: List[TodoTask]) -> List[TodoTask]:
        # Todos without due dates go to the end
        with_dates = [t for t in todos if t.due_date]
        without_dates = [t for t in todos if not t.due_date]
        return sorted(with_dates, key=lambda t: t.due_date) + without_dates


class SortByTitleStrategy(ISortStrategy):
    """Sort todos alphabetically by title"""
    def sort(self, todos: List[TodoTask]) -> List[TodoTask]:
        return sorted(todos, key=lambda t: t.title.lower())


class TodoSorter:
    """Context class that uses sorting strategy"""
    def __init__(self, strategy: ISortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ISortStrategy):
        """Change sorting strategy at runtime"""
        self._strategy = strategy

    def sort_todos(self, todos: List[TodoTask]) -> List[TodoTask]:
        """Sort todos using current strategy"""
        return self._strategy.sort(todos)


# =============================================================================
# 6. OBSERVER PATTERN
# =============================================================================
"""
Observer Pattern:
- Defines one-to-many dependency between objects
- When one object changes state, all dependents are notified
- Implements event handling systems

Benefits:
- Loose coupling between subject and observers
- Dynamic subscription/unsubscription
- Broadcast communication
"""

class ITodoObserver(ABC):
    """Observer interface"""
    @abstractmethod
    def update(self, event_type: str, todo: TodoTask):
        pass


class TodoNotificationObserver(ITodoObserver):
    """Observer that sends notifications"""
    def __init__(self, name: str):
        self.name = name

    def update(self, event_type: str, todo: TodoTask):
        print(f"[{self.name}] Notification: Todo '{todo.title}' was {event_type}")


class TodoAnalyticsObserver(ITodoObserver):
    """Observer that tracks analytics"""
    def __init__(self):
        self.events: Dict[str, int] = {}

    def update(self, event_type: str, todo: TodoTask):
        self.events[event_type] = self.events.get(event_type, 0) + 1
        print(f"[Analytics] Event count - {event_type}: {self.events[event_type]}")


class TodoAuditObserver(ITodoObserver):
    """Observer that maintains audit log"""
    def __init__(self):
        self.audit_log: List[str] = []

    def update(self, event_type: str, todo: TodoTask):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {event_type}: {todo.id} - {todo.title}"
        self.audit_log.append(log_entry)
        print(f"[Audit] {log_entry}")


class TodoSubject:
    """Subject that maintains list of observers and notifies them"""
    def __init__(self):
        self._observers: List[ITodoObserver] = []

    def attach(self, observer: ITodoObserver):
        """Subscribe an observer"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: ITodoObserver):
        """Unsubscribe an observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event_type: str, todo: TodoTask):
        """Notify all observers about an event"""
        for observer in self._observers:
            observer.update(event_type, todo)


# =============================================================================
# 7. DECORATOR PATTERN
# =============================================================================
"""
Decorator Pattern:
- Adds new functionality to objects dynamically
- Alternative to subclassing for extending functionality
- Wraps original object

Benefits:
- More flexible than inheritance
- Responsibilities can be added/removed at runtime
- Avoids class explosion
"""

class ITodoComponent(ABC):
    """Component interface"""
    @abstractmethod
    def get_details(self) -> str:
        pass

    @abstractmethod
    def get_cost(self) -> float:
        pass


class BasicTodoComponent(ITodoComponent):
    """Concrete component - basic todo"""
    def __init__(self, title: str):
        self.title = title

    def get_details(self) -> str:
        return f"Todo: {self.title}"

    def get_cost(self) -> float:
        return 0.0


class TodoDecorator(ITodoComponent):
    """Base decorator class"""
    def __init__(self, component: ITodoComponent):
        self._component = component

    def get_details(self) -> str:
        return self._component.get_details()

    def get_cost(self) -> float:
        return self._component.get_cost()


class PriorityDecorator(TodoDecorator):
    """Adds priority feature"""
    def __init__(self, component: ITodoComponent, priority: str):
        super().__init__(component)
        self.priority = priority

    def get_details(self) -> str:
        return f"{self._component.get_details()} [Priority: {self.priority}]"

    def get_cost(self) -> float:
        return self._component.get_cost() + 1.0


class ReminderDecorator(TodoDecorator):
    """Adds reminder feature"""
    def __init__(self, component: ITodoComponent, reminder_time: str):
        super().__init__(component)
        self.reminder_time = reminder_time

    def get_details(self) -> str:
        return f"{self._component.get_details()} [Reminder: {self.reminder_time}]"

    def get_cost(self) -> float:
        return self._component.get_cost() + 2.0


class CollaborationDecorator(TodoDecorator):
    """Adds collaboration feature"""
    def __init__(self, component: ITodoComponent, collaborators: List[str]):
        super().__init__(component)
        self.collaborators = collaborators

    def get_details(self) -> str:
        collab_str = ", ".join(self.collaborators)
        return f"{self._component.get_details()} [Collaborators: {collab_str}]"

    def get_cost(self) -> float:
        return self._component.get_cost() + 5.0


# =============================================================================
# 8. ADAPTER PATTERN
# =============================================================================
"""
Adapter Pattern:
- Converts interface of a class into another interface
- Allows incompatible interfaces to work together
- Acts as a bridge between two incompatible interfaces

Benefits:
- Reuses existing code
- Increases transparency
- Enables integration with legacy systems
"""

class LegacyTodoSystem:
    """Legacy system with different interface"""
    def __init__(self):
        self.tasks = []

    def add_task(self, task_data: dict):
        """Legacy method to add task"""
        self.tasks.append(task_data)
        print(f"[Legacy] Added task: {task_data['name']}")

    def get_task(self, index: int):
        """Legacy method to get task by index"""
        return self.tasks[index] if index < len(self.tasks) else None

    def list_all_tasks(self):
        """Legacy method to list tasks"""
        return self.tasks


class ModernTodoInterface(ABC):
    """Modern interface that our application expects"""
    @abstractmethod
    def create_todo(self, todo: TodoEntity) -> bool:
        pass

    @abstractmethod
    def get_todo_by_id(self, todo_id: str) -> Optional[TodoEntity]:
        pass

    @abstractmethod
    def get_all_todos(self) -> List[TodoEntity]:
        pass


class LegacyTodoAdapter(ModernTodoInterface):
    """Adapter that makes legacy system compatible with modern interface"""
    def __init__(self, legacy_system: LegacyTodoSystem):
        self.legacy_system = legacy_system
        self.id_to_index: Dict[str, int] = {}

    def create_todo(self, todo: TodoEntity) -> bool:
        """Adapt modern create to legacy add"""
        task_data = {
            "name": todo.title,
            "description": todo.description,
            "done": todo.is_completed
        }
        index = len(self.legacy_system.tasks)
        self.id_to_index[todo.id] = index
        self.legacy_system.add_task(task_data)
        return True

    def get_todo_by_id(self, todo_id: str) -> Optional[TodoEntity]:
        """Adapt modern get by ID to legacy get by index"""
        index = self.id_to_index.get(todo_id)
        if index is not None:
            legacy_task = self.legacy_system.get_task(index)
            if legacy_task:
                todo = TodoEntity(todo_id, legacy_task["name"], legacy_task["description"])
                todo.is_completed = legacy_task["done"]
                return todo
        return None

    def get_all_todos(self) -> List[TodoEntity]:
        """Adapt modern get all to legacy list all"""
        todos = []
        legacy_tasks = self.legacy_system.list_all_tasks()
        for todo_id, index in self.id_to_index.items():
            if index < len(legacy_tasks):
                task = legacy_tasks[index]
                todo = TodoEntity(todo_id, task["name"], task["description"])
                todo.is_completed = task["done"]
                todos.append(todo)
        return todos


# =============================================================================
# 9. PROTOTYPE PATTERN
# =============================================================================
"""
Prototype Pattern:
- Creates new objects by copying existing objects (prototypes)
- Avoids expensive creation operations
- Hides complexity of creating new instances

Benefits:
- Reduces need for subclassing
- Adds/removes objects at runtime
- Specifies new objects by varying values/structure
"""

class TodoPrototype(ABC):
    """Prototype interface"""
    @abstractmethod
    def clone(self):
        pass


class TodoTemplate(TodoPrototype):
    """Concrete prototype - reusable todo template"""
    def __init__(self, title: str, description: str, tags: List[str], priority: TodoPriority):
        self.title = title
        self.description = description
        self.tags = tags
        self.priority = priority
        self.subtasks: List[str] = []

    def add_subtask(self, subtask: str):
        self.subtasks.append(subtask)

    def clone(self):
        """Create a deep copy of this template"""
        cloned = TodoTemplate(
            self.title,
            self.description,
            self.tags.copy(),
            self.priority
        )
        cloned.subtasks = self.subtasks.copy()
        return cloned

    def __str__(self):
        return f"Template: {self.title} (Tags: {self.tags}, Subtasks: {len(self.subtasks)})"


class TodoTemplateRegistry:
    """Registry to manage todo templates"""
    def __init__(self):
        self._templates: Dict[str, TodoTemplate] = {}

    def register_template(self, name: str, template: TodoTemplate):
        """Register a new template"""
        self._templates[name] = template

    def create_from_template(self, name: str) -> Optional[TodoTemplate]:
        """Create a new todo by cloning a template"""
        template = self._templates.get(name)
        if template:
            return template.clone()
        return None

    def list_templates(self) -> List[str]:
        """List all available templates"""
        return list(self._templates.keys())


# =============================================================================
# DEMONSTRATION AND TESTING
# =============================================================================

def demonstrate_patterns():
    """Demonstrate all design patterns with examples"""

    print("=" * 80)
    print("DESIGN PATTERNS DEMONSTRATION - TODO APPLICATION")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. REPOSITORY PATTERN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("1. REPOSITORY PATTERN - Data Access Abstraction")
    print("=" * 80)

    # Using in-memory repository
    print("\n--- Using In-Memory Repository ---")
    in_memory_repo = InMemoryTodoRepository()
    todo1 = TodoEntity("001", "Learn Repository Pattern", "Study data access patterns")
    in_memory_repo.save(todo1)
    retrieved = in_memory_repo.find_by_id("001")
    print(f"Retrieved: {retrieved.title}")

    # Using database repository (can switch easily!)
    print("\n--- Switching to Database Repository ---")
    db_repo = DatabaseTodoRepository("postgresql://localhost/todos")
    todo2 = TodoEntity("002", "Learn Singleton Pattern", "Study creational patterns")
    db_repo.save(todo2)
    retrieved_db = db_repo.find_by_id("002")
    print(f"Retrieved from DB: {retrieved_db.title}")

    print("\n✓ Repository Pattern Benefits:")
    print("  - Switched storage mechanism without changing business logic")
    print("  - Abstracted data access details")
    print("  - Easy to test with mock repositories")

    # -------------------------------------------------------------------------
    # 2. SINGLETON PATTERN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("2. SINGLETON PATTERN - Single Instance Guarantee")
    print("=" * 80)

    config1 = TodoConfigManager()
    config2 = TodoConfigManager()

    print(f"\nconfig1 is config2: {config1 is config2}")
    print(f"App Name: {config1.get('app_name')}")

    config1.set("max_todos", 200)
    print(f"Max todos (via config2): {config2.get('max_todos')}")

    logger1 = TodoLogger()
    logger2 = TodoLogger()
    logger1.log("First log entry")
    logger2.log("Second log entry")
    print(f"\nLogger1 is Logger2: {logger1 is logger2}")
    print(f"Total logs: {len(logger1.get_logs())}")

    print("\n✓ Singleton Pattern Benefits:")
    print("  - Only one instance exists across entire application")
    print("  - Global access point")
    print("  - Shared state (config changes reflected everywhere)")

    # -------------------------------------------------------------------------
    # 3. FACTORY PATTERN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("3. FACTORY PATTERN - Object Creation Abstraction")
    print("=" * 80)

    # Create different types of todos using factory
    simple = TodoFactory.create_todo("simple", "T001", "Buy groceries")
    urgent = TodoFactory.create_todo("urgent", "T002", "Fix production bug",
                                    deadline=datetime(2025, 12, 30))
    recurring = TodoFactory.create_todo("recurring", "T003", "Daily standup",
                                       frequency="daily")

    print(f"\n{simple.get_description()}")
    print(f"Priority: {simple.get_priority_level().name}")

    print(f"\n{urgent.get_description()}")
    print(f"Priority: {urgent.get_priority_level().name}")

    print(f"\n{recurring.get_description()}")
    print(f"Priority: {recurring.get_priority_level().name}")

    print("\n✓ Factory Pattern Benefits:")
    print("  - Centralized object creation logic")
    print("  - Easy to add new todo types without modifying client code")
    print("  - Encapsulates complex initialization")

    # -------------------------------------------------------------------------
    # 4. BUILDER PATTERN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("4. BUILDER PATTERN - Step-by-Step Object Construction")
    print("=" * 80)

    # Build a complex todo with fluent interface
    complex_todo = (TodoBuilder()
                   .with_id("T004")
                   .with_title("Implement Authentication System")
                   .with_description("Build OAuth2 authentication")
                   .with_priority(TodoPriority.URGENT)
                   .add_tags(["backend", "security", "sprint-1"])
                   .assign_to("john@example.com")
                   .with_due_date(datetime(2026, 1, 15))
                   .with_estimated_hours(16.5)
                   .add_subtask("Research OAuth2 providers")
                   .add_subtask("Implement login endpoint")
                   .add_subtask("Add JWT token generation")
                   .build())

    print(f"\n{complex_todo}")
    print(f"Assignee: {complex_todo.assignee}")
    print(f"Due Date: {complex_todo.due_date.strftime('%Y-%m-%d')}")
    print(f"Estimated Hours: {complex_todo.estimated_hours}")
    print(f"Subtasks: {len(complex_todo.subtasks)}")

    print("\n✓ Builder Pattern Benefits:")
    print("  - Fluent, readable object construction")
    print("  - Handles objects with many optional parameters")
    print("  - Separates construction from representation")

    # -------------------------------------------------------------------------
    # 5. STRATEGY PATTERN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("5. STRATEGY PATTERN - Interchangeable Algorithms")
    print("=" * 80)

    # Create multiple todos
    todos = [
        (TodoBuilder().with_id("S1").with_title("Write tests")
         .with_priority(TodoPriority.MEDIUM).build()),
        (TodoBuilder().with_id("S2").with_title("Fix critical bug")
         .with_priority(TodoPriority.URGENT).with_due_date(datetime(2025, 12, 29)).build()),
        (TodoBuilder().with_id("S3").with_title("Update documentation")
         .with_priority(TodoPriority.LOW).with_due_date(datetime(2026, 1, 5)).build()),
        (TodoBuilder().with_id("S4").with_title("Code review")
         .with_priority(TodoPriority.HIGH).build()),
    ]

    # Sort using different strategies
    sorter = TodoSorter(SortByPriorityStrategy())

    print("\n--- Sorted by Priority ---")
    sorted_todos = sorter.sort_todos(todos)
    for todo in sorted_todos:
        print(f"{todo.title} - Priority: {todo.priority.name}")

    print("\n--- Sorted by Due Date ---")
    sorter.set_strategy(SortByDueDateStrategy())
    sorted_todos = sorter.sort_todos(todos)
    for todo in sorted_todos:
        due = todo.due_date.strftime('%Y-%m-%d') if todo.due_date else "No due date"
        print(f"{todo.title} - Due: {due}")

    print("\n--- Sorted by Title ---")
    sorter.set_strategy(SortByTitleStrategy())
    sorted_todos = sorter.sort_todos(todos)
    for todo in sorted_todos:
        print(f"{todo.title}")

    print("\n✓ Strategy Pattern Benefits:")
    print("  - Algorithm can be changed at runtime")
    print("  - Eliminates conditional statements")
    print("  - Easy to add new sorting strategies")

    # -------------------------------------------------------------------------
    # 6. OBSERVER PATTERN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("6. OBSERVER PATTERN - Event Notification System")
    print("=" * 80)

    # Create subject and observers
    todo_subject = TodoSubject()

    notification_observer = TodoNotificationObserver("EmailService")
    analytics_observer = TodoAnalyticsObserver()
    audit_observer = TodoAuditObserver()

    # Attach observers
    todo_subject.attach(notification_observer)
    todo_subject.attach(analytics_observer)
    todo_subject.attach(audit_observer)

    # Trigger events
    print("\n--- Creating Todo ---")
    new_todo = (TodoBuilder().with_id("O1").with_title("Deploy to production").build())
    todo_subject.notify("created", new_todo)

    print("\n--- Updating Todo ---")
    todo_subject.notify("updated", new_todo)

    print("\n--- Completing Todo ---")
    todo_subject.notify("completed", new_todo)

    print("\n✓ Observer Pattern Benefits:")
    print("  - Loose coupling between subject and observers")
    print("  - Multiple observers can react to same event")
    print("  - Dynamic subscription/unsubscription")

    # -------------------------------------------------------------------------
    # 7. DECORATOR PATTERN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("7. DECORATOR PATTERN - Dynamic Feature Addition")
    print("=" * 80)

    # Start with basic todo
    basic_todo = BasicTodoComponent("Complete project report")
    print(f"\nBasic Todo: {basic_todo.get_details()}")
    print(f"Cost: ${basic_todo.get_cost()}")

    # Add priority feature
    priority_todo = PriorityDecorator(basic_todo, "High")
    print(f"\nWith Priority: {priority_todo.get_details()}")
    print(f"Cost: ${priority_todo.get_cost()}")

    # Add reminder feature
    reminder_todo = ReminderDecorator(priority_todo, "Tomorrow 9AM")
    print(f"\nWith Reminder: {reminder_todo.get_details()}")
    print(f"Cost: ${reminder_todo.get_cost()}")

    # Add collaboration feature
    collab_todo = CollaborationDecorator(reminder_todo, ["Alice", "Bob"])
    print(f"\nWith Collaboration: {collab_todo.get_details()}")
    print(f"Cost: ${collab_todo.get_cost()}")

    print("\n✓ Decorator Pattern Benefits:")
    print("  - Features can be added/removed at runtime")
    print("  - More flexible than inheritance")
    print("  - Avoids class explosion")

    # -------------------------------------------------------------------------
    # 8. ADAPTER PATTERN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("8. ADAPTER PATTERN - Interface Compatibility")
    print("=" * 80)

    # Legacy system
    legacy_system = LegacyTodoSystem()

    # Adapter makes it compatible with modern interface
    adapter = LegacyTodoAdapter(legacy_system)

    # Use modern interface with legacy system
    modern_todo1 = TodoEntity("A001", "Migrate legacy system", "Phase 1 migration")
    modern_todo2 = TodoEntity("A002", "Test adapter pattern", "Integration testing")

    print("\n--- Creating todos via adapter ---")
    adapter.create_todo(modern_todo1)
    adapter.create_todo(modern_todo2)

    print("\n--- Retrieving todo via adapter ---")
    retrieved = adapter.get_todo_by_id("A001")
    if retrieved:
        print(f"Retrieved: {retrieved.title}")

    print("\n--- Getting all todos via adapter ---")
    all_todos = adapter.get_all_todos()
    print(f"Total todos: {len(all_todos)}")
    for todo in all_todos:
        print(f"  - {todo.title}")

    print("\n✓ Adapter Pattern Benefits:")
    print("  - Integrates with legacy systems without modifying them")
    print("  - Converts incompatible interfaces")
    print("  - Promotes code reuse")

    # -------------------------------------------------------------------------
    # 9. PROTOTYPE PATTERN
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("9. PROTOTYPE PATTERN - Object Cloning")
    print("=" * 80)

    # Create template registry
    registry = TodoTemplateRegistry()

    # Create templates
    bug_template = TodoTemplate(
        "Bug Fix Template",
        "Standard bug fix workflow",
        ["bug", "fix"],
        TodoPriority.HIGH
    )
    bug_template.add_subtask("Reproduce the issue")
    bug_template.add_subtask("Identify root cause")
    bug_template.add_subtask("Implement fix")
    bug_template.add_subtask("Write tests")
    bug_template.add_subtask("Code review")

    feature_template = TodoTemplate(
        "Feature Development Template",
        "Standard feature development workflow",
        ["feature", "development"],
        TodoPriority.MEDIUM
    )
    feature_template.add_subtask("Design feature")
    feature_template.add_subtask("Implement feature")
    feature_template.add_subtask("Write tests")
    feature_template.add_subtask("Documentation")

    # Register templates
    registry.register_template("bug_fix", bug_template)
    registry.register_template("feature", feature_template)

    print("\n--- Available Templates ---")
    for template_name in registry.list_templates():
        print(f"  - {template_name}")

    # Clone templates to create new todos
    print("\n--- Creating todos from templates ---")
    bug_todo1 = registry.create_from_template("bug_fix")
    bug_todo2 = registry.create_from_template("bug_fix")
    feature_todo = registry.create_from_template("feature")

    print(f"\nCloned Bug Fix 1: {bug_todo1}")
    print(f"Cloned Bug Fix 2: {bug_todo2}")
    print(f"Are they the same object? {bug_todo1 is bug_todo2}")
    print(f"Do they have same content? {bug_todo1.title == bug_todo2.title}")

    print(f"\nCloned Feature: {feature_todo}")

    print("\n✓ Prototype Pattern Benefits:")
    print("  - Avoids expensive object creation")
    print("  - Creates new objects by copying existing ones")
    print("  - Useful for creating similar objects with variations")

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PATTERN COMPARISON SUMMARY")
    print("=" * 80)

    print("""
┌─────────────────┬──────────────────────┬────────────────────────────────────┐
│ Pattern         │ Category             │ Use Case in Todo App               │
├─────────────────┼──────────────────────┼────────────────────────────────────┤
│ Repository      │ Architectural        │ Abstract data storage mechanism    │
│ Singleton       │ Creational           │ Config manager, Logger instance    │
│ Factory         │ Creational           │ Create different types of todos    │
│ Builder         │ Creational           │ Construct complex todo objects     │
│ Strategy        │ Behavioral           │ Different sorting algorithms       │
│ Observer        │ Behavioral           │ Event notifications, audit logs    │
│ Decorator       │ Structural           │ Add features dynamically           │
│ Adapter         │ Structural           │ Integrate with legacy systems      │
│ Prototype       │ Creational           │ Clone todo templates               │
└─────────────────┴──────────────────────┴────────────────────────────────────┘

Key Takeaways:
==============
1. Repository Pattern - Best for data access abstraction
2. Singleton Pattern - Use sparingly, only for truly global state
3. Factory Pattern - Centralizes object creation logic
4. Builder Pattern - Perfect for objects with many parameters
5. Strategy Pattern - Swap algorithms at runtime
6. Observer Pattern - Event-driven architecture
7. Decorator Pattern - Add features without inheritance
8. Adapter Pattern - Make incompatible interfaces work together
9. Prototype Pattern - Clone objects instead of creating new ones
    """)


if __name__ == "__main__":
    demonstrate_patterns()
