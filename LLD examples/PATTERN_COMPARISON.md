# Design Patterns Comparison Guide

## Quick Reference: When to Use Which Pattern

### 📊 Pattern Categories

```
Creational Patterns (How to CREATE objects)
├── Singleton - ONE instance only
├── Factory - CREATE different types
├── Builder - CREATE complex objects step-by-step
└── Prototype - CREATE by CLONING

Structural Patterns (How to COMPOSE objects)
├── Adapter - CONVERT interfaces
├── Decorator - ADD features dynamically
├── Facade - SIMPLIFY complex systems
└── Proxy - CONTROL access

Behavioral Patterns (How objects INTERACT)
├── Strategy - SWAP algorithms
├── Observer - EVENT notifications
├── Command - ENCAPSULATE requests
└── State - CHANGE behavior based on state

Architectural Patterns (How to ORGANIZE systems)
└── Repository - ABSTRACT data access
```

---

## 1️⃣ Repository Pattern (Architectural)

### What It Does
Separates data access logic from business logic by providing an abstraction layer over data storage.

### Original Practice.py Example
```python
class TodoRepo:
    def __init__(self):
        self._todos: Dict[str, TodoItem] = {}

    def save(self, todo: TodoItem):
        self._todos[todo.id] = todo
```

**Problem**: Tightly coupled to in-memory storage. Can't switch to database.

### New Pattern Example
```python
# Interface (abstraction)
class ITodoRepository(ABC):
    @abstractmethod
    def save(self, todo: TodoEntity) -> TodoEntity:
        pass

# Implementation 1: In-Memory
class InMemoryTodoRepository(ITodoRepository):
    def save(self, todo: TodoEntity) -> TodoEntity:
        self._storage[todo.id] = todo
        return todo

# Implementation 2: Database
class DatabaseTodoRepository(ITodoRepository):
    def save(self, todo: TodoEntity) -> TodoEntity:
        print(f"[DB] Saving to database")
        self._db[todo.id] = todo
        return todo
```

### Todo App Comparison

| Aspect | Without Repository | With Repository |
|--------|-------------------|-----------------|
| Storage | `_todos = {}` hardcoded | Interface-based abstraction |
| Switching | Can't switch to DB | Just inject different repo |
| Testing | Hard to mock | Easy to mock interface |
| Flexibility | Low | High |

**When to Use**:
- ✅ Need to switch between storage mechanisms (memory, DB, file, cache)
- ✅ Want to test business logic without actual database
- ✅ Multiple data sources for same entity

---

## 2️⃣ Singleton Pattern (Creational)

### What It Does
Ensures only ONE instance of a class exists throughout the application.

### Original Practice.py Example
```python
# NOT using Singleton - can create multiple instances
repo1 = TodoRepo()
repo2 = TodoRepo()
# repo1 and repo2 are DIFFERENT objects with separate data
```

### New Pattern Example
```python
class TodoConfigManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

# Usage
config1 = TodoConfigManager()
config2 = TodoConfigManager()
# config1 is config2 → True (SAME object)
```

### Todo App Comparison

| Scenario | Without Singleton | With Singleton |
|----------|------------------|----------------|
| Config Manager | Multiple configs, inconsistent settings | One source of truth |
| Logger | Separate log instances | Centralized logging |
| Cache | Multiple caches, wasted memory | Shared cache |
| Counter | Separate counters | Global counter |

**When to Use**:
- ✅ Configuration management
- ✅ Logging systems
- ✅ Connection pools
- ✅ Cache managers
- ❌ Avoid overuse - makes testing harder

---

## 3️⃣ Factory Pattern (Creational)

### What It Does
Creates objects without exposing creation logic. Provides common interface for creating different types.

### Original Practice.py Example
```python
# Direct instantiation - client knows concrete class
todo = TodoItem(id, title)
```

**Problem**: If we need different types of todos (urgent, recurring), we'd need many if-else statements.

### New Pattern Example
```python
# Factory creates appropriate type based on input
class TodoFactory:
    @staticmethod
    def create_todo(todo_type: str, todo_id: str, title: str, **kwargs):
        if todo_type == "simple":
            return SimpleTodo(todo_id, title)
        elif todo_type == "urgent":
            return UrgentTodo(todo_id, title, kwargs['deadline'])
        elif todo_type == "recurring":
            return RecurringTodo(todo_id, title, kwargs['frequency'])

# Usage
simple = TodoFactory.create_todo("simple", "T001", "Buy groceries")
urgent = TodoFactory.create_todo("urgent", "T002", "Fix bug", deadline=tomorrow)
```

### Todo App Comparison

| Aspect | Direct Creation | Factory Pattern |
|--------|----------------|-----------------|
| Code | `todo = SimpleTodo(...)` | `factory.create_todo("simple", ...)` |
| Adding Types | Modify all creation sites | Modify only factory |
| Logic | Scattered | Centralized |
| Flexibility | Low | High |

**When to Use**:
- ✅ Need different types of similar objects
- ✅ Creation logic is complex
- ✅ Want to hide implementation details

---

## 4️⃣ Builder Pattern (Creational)

### What It Does
Constructs complex objects step-by-step with a fluent interface.

### Original Practice.py Example
```python
# Simple constructor - works for simple objects
todo = TodoItem(todo_id, todo_title)
todo.is_completed = False
```

**Problem**: If TodoItem has 10+ optional parameters, constructor becomes unwieldy.

### New Pattern Example
```python
# Fluent interface for complex construction
todo = (TodoBuilder()
       .with_id("T004")
       .with_title("Implement Authentication")
       .with_description("Build OAuth2")
       .with_priority(TodoPriority.URGENT)
       .add_tags(["backend", "security"])
       .assign_to("john@example.com")
       .with_due_date(datetime(2026, 1, 15))
       .with_estimated_hours(16.5)
       .add_subtask("Research OAuth2")
       .add_subtask("Implement login")
       .build())
```

### Todo App Comparison

| Aspect | Constructor | Builder Pattern |
|--------|------------|-----------------|
| Readability | `Todo(id, title, desc, priority, tags, assignee, due, hours)` | Fluent chain |
| Optional Params | All in constructor | Set only what you need |
| Validation | At end | During building |
| Immutability | Hard to achieve | Easy to make immutable |

**When to Use**:
- ✅ Object has many (5+) optional parameters
- ✅ Need readable, self-documenting code
- ✅ Want to create immutable objects

---

## 5️⃣ Strategy Pattern (Behavioral)

### What It Does
Defines family of algorithms and makes them interchangeable at runtime.

### Original Practice.py Example
```python
# No sorting capability - fixed behavior
def get_all(self):
    return self.repo.get_list()
```

**Problem**: If we want different sorting options, we'd need multiple methods or if-else.

### New Pattern Example
```python
# Define strategies
class SortByPriorityStrategy(ISortStrategy):
    def sort(self, todos: List[TodoTask]) -> List[TodoTask]:
        return sorted(todos, key=lambda t: t.priority.value, reverse=True)

class SortByDueDateStrategy(ISortStrategy):
    def sort(self, todos: List[TodoTask]) -> List[TodoTask]:
        return sorted(todos, key=lambda t: t.due_date)

# Use strategy
sorter = TodoSorter(SortByPriorityStrategy())
sorted_todos = sorter.sort_todos(todos)

# Change strategy at runtime
sorter.set_strategy(SortByDueDateStrategy())
sorted_todos = sorter.sort_todos(todos)
```

### Todo App Comparison

| Approach | Without Strategy | With Strategy |
|----------|-----------------|---------------|
| Sort by priority | `sort_by_priority()` method | `sorter.set_strategy(PriorityStrategy())` |
| Sort by date | `sort_by_date()` method | `sorter.set_strategy(DateStrategy())` |
| Sort by title | `sort_by_title()` method | `sorter.set_strategy(TitleStrategy())` |
| Adding new sort | Add new method | Add new strategy class |
| Runtime change | Can't change | Can change dynamically |

**When to Use**:
- ✅ Multiple ways to do the same thing
- ✅ Need to switch algorithms at runtime
- ✅ Want to avoid if-else chains

---

## 6️⃣ Observer Pattern (Behavioral)

### What It Does
One-to-many dependency - when one object changes, all dependents are notified.

### Original Practice.py Example
```python
def add(self, title):
    todo = self.service.add(title)
    print(f"TODO Added ID : {todo.id} title : {todo.title}")
```

**Problem**: Only prints. What if we want to send email, log to file, update analytics?

### New Pattern Example
```python
# Subject notifies all observers
class TodoSubject:
    def notify(self, event_type: str, todo: TodoTask):
        for observer in self._observers:
            observer.update(event_type, todo)

# Multiple observers react
notification_observer = TodoNotificationObserver("EmailService")
analytics_observer = TodoAnalyticsObserver()
audit_observer = TodoAuditObserver()

subject.attach(notification_observer)
subject.attach(analytics_observer)
subject.attach(audit_observer)

# One event → three reactions
subject.notify("created", new_todo)
# → Email sent
# → Analytics updated
# → Audit log created
```

### Todo App Comparison

| Aspect | Without Observer | With Observer |
|--------|-----------------|---------------|
| Coupling | Controller knows all actions | Subject doesn't know observers |
| Adding feature | Modify controller | Add new observer |
| Flexibility | Low | High |
| Separation | Poor | Excellent |

**When to Use**:
- ✅ Event-driven systems
- ✅ Notifications (email, SMS, push)
- ✅ Logging and auditing
- ✅ Analytics tracking

---

## 7️⃣ Decorator Pattern (Structural)

### What It Does
Adds new functionality to objects dynamically without modifying their structure.

### Original Practice.py Example
```python
class TodoItem:
    def __init__(self, todo_id, todo_title):
        self.id = todo_id
        self.title = todo_title
        self.is_completed = False
```

**Problem**: What if some todos need priority, some need reminders, some need both?

### Solutions Comparison

| Approach | Inheritance | Decorator Pattern |
|----------|------------|-------------------|
| Classes needed | TodoWithPriority, TodoWithReminder, TodoWithBoth | 3 decorator classes |
| Combinations | 2^n classes (explosion!) | Mix and match decorators |
| Runtime addition | Can't add features | Can add/remove dynamically |

### New Pattern Example
```python
# Start basic
todo = BasicTodoComponent("Complete report")

# Add features dynamically
todo = PriorityDecorator(todo, "High")
todo = ReminderDecorator(todo, "Tomorrow 9AM")
todo = CollaborationDecorator(todo, ["Alice", "Bob"])

# Result: Todo with all features
print(todo.get_details())
# → "Todo: Complete report [Priority: High] [Reminder: Tomorrow 9AM] [Collaborators: Alice, Bob]"
```

**When to Use**:
- ✅ Need to add features at runtime
- ✅ Want to avoid class explosion
- ✅ Features can be combined in various ways

---

## 8️⃣ Adapter Pattern (Structural)

### What It Does
Converts one interface to another to make incompatible interfaces work together.

### Original Practice.py Example
```python
# Modern interface
class TodoRepo:
    def save(self, todo: TodoItem):
        self._todos[todo.id] = todo
```

**Problem**: What if we have a legacy system with different interface?

### New Pattern Example
```python
# Legacy system uses different method names
class LegacyTodoSystem:
    def add_task(self, task_data: dict):  # Different method name
        self.tasks.append(task_data)

# Adapter makes it compatible
class LegacyTodoAdapter(ModernTodoInterface):
    def create_todo(self, todo: TodoEntity) -> bool:
        # Convert modern call to legacy call
        task_data = {"name": todo.title, "description": todo.description}
        self.legacy_system.add_task(task_data)
```

### Todo App Comparison

| Scenario | Without Adapter | With Adapter |
|----------|----------------|--------------|
| Legacy integration | Rewrite legacy system | Wrap with adapter |
| Different APIs | Modify all code | Create adapter |
| Third-party libs | Can't use | Adapt interface |

**When to Use**:
- ✅ Integrating with legacy systems
- ✅ Using third-party libraries with different interfaces
- ✅ Making incompatible classes work together

---

## 9️⃣ Prototype Pattern (Creational)

### What It Does
Creates new objects by cloning existing objects instead of creating from scratch.

### Original Practice.py Example
```python
# Creating todos from scratch every time
def add(self, title):
    id = self.generate_id()
    todo = TodoItem(id, title)  # Create new
    self.repo.save(todo)
```

**Problem**: What if todos have complex setup? What about templates?

### New Pattern Example
```python
# Create template once
bug_template = TodoTemplate(
    "Bug Fix Template",
    "Standard bug fix workflow",
    ["bug", "fix"],
    TodoPriority.HIGH
)
bug_template.add_subtask("Reproduce issue")
bug_template.add_subtask("Identify root cause")
bug_template.add_subtask("Implement fix")

# Clone for each new bug
bug1 = bug_template.clone()
bug2 = bug_template.clone()
# Both have the same subtasks, tags, etc.
```

### Todo App Comparison

| Scenario | From Scratch | Prototype Pattern |
|----------|-------------|-------------------|
| Bug report | Create 5 subtasks each time | Clone template |
| Performance | Slow if complex | Fast cloning |
| Consistency | Manual, error-prone | Guaranteed consistency |

**When to Use**:
- ✅ Object creation is expensive
- ✅ Need templates or blueprints
- ✅ Objects are similar with minor variations

---

## 🆚 Side-by-Side Pattern Comparison

### Scenario: Adding a New Todo

```python
# 1. ORIGINAL practice.py (Simple but limited)
service = TodoService(repo)
todo = service.add("Fix bug")

# 2. WITH FACTORY (Different types)
todo = TodoFactory.create_todo("urgent", "T001", "Fix bug", deadline=tomorrow)

# 3. WITH BUILDER (Complex object)
todo = (TodoBuilder()
       .with_id("T001")
       .with_title("Fix bug")
       .with_priority(TodoPriority.URGENT)
       .add_tags(["bug", "urgent"])
       .assign_to("dev@example.com")
       .build())

# 4. WITH PROTOTYPE (From template)
todo = bug_template.clone()
todo.title = "Fix specific bug"

# 5. WITH OBSERVER (Event notifications)
subject.notify("created", todo)  # → Email, analytics, audit log

# 6. WITH DECORATOR (Add features)
todo = BasicTodoComponent("Fix bug")
todo = PriorityDecorator(todo, "High")
todo = ReminderDecorator(todo, "In 2 hours")
```

---

## 📋 Decision Tree: Which Pattern to Use?

```
Need to CREATE objects?
├── Only ONE instance needed? → Singleton
├── Different types of objects? → Factory
├── Complex object with many parameters? → Builder
└── Clone existing objects? → Prototype

Need to STRUCTURE/ORGANIZE objects?
├── Make incompatible interfaces work? → Adapter
├── Add features dynamically? → Decorator
└── Abstract data access? → Repository

Need to handle BEHAVIOR/INTERACTION?
├── Swap algorithms at runtime? → Strategy
├── Notify multiple objects of changes? → Observer
└── Encapsulate requests as objects? → Command
```

---

## 🎯 Practice.py vs Pattern Examples

| File | Purpose | Patterns Used |
|------|---------|---------------|
| **practice.py** | Simple todo app | Basic Repository, Service Layer |
| **design_patterns_examples.py** | Learning all patterns | 9 design patterns with comparisons |

### Evolution Path

```
Level 1: practice.py
└── Basic CRUD operations
    └── Simple repository
        └── Direct instantiation

Level 2: design_patterns_examples.py
└── Advanced patterns
    ├── Repository with abstraction
    ├── Multiple creation patterns (Factory, Builder, Prototype)
    ├── Behavioral patterns (Strategy, Observer)
    ├── Structural patterns (Decorator, Adapter)
    └── Singleton for shared state
```

---

## 💡 Key Takeaways

1. **Repository Pattern**: Use when you want to abstract data access from business logic
2. **Singleton Pattern**: Use sparingly for truly global state (config, logger)
3. **Factory Pattern**: Use when you need to create different types of related objects
4. **Builder Pattern**: Use when constructing complex objects with many optional parameters
5. **Strategy Pattern**: Use when you have multiple interchangeable algorithms
6. **Observer Pattern**: Use for event-driven systems and notifications
7. **Decorator Pattern**: Use to add features dynamically without inheritance
8. **Adapter Pattern**: Use to integrate with legacy or incompatible systems
9. **Prototype Pattern**: Use to clone objects instead of creating from scratch

---

## 🚀 Next Steps

1. **Run the examples**: `python design_patterns_examples.py`
2. **Compare outputs**: See how each pattern solves different problems
3. **Modify practice.py**: Try adding patterns to your simple todo app
4. **Experiment**: Mix and match patterns to solve complex problems

Remember: **Patterns are tools, not rules**. Use them when they solve a real problem, not just for the sake of using them.
