# 02. Low-Level Design (LLD)

## 🎯 Learning Objectives

Master the art of designing clean, maintainable, and extensible code:
- Apply SOLID principles and design patterns effectively
- Design object-oriented systems that are easy to understand and modify
- Implement scalable data structures and algorithms
- Create robust APIs and interfaces

## 📋 Prerequisites
- Strong programming fundamentals in at least one OOP language
- Understanding of basic data structures and algorithms
- Experience with software development projects
- **Estimated Time**: 2-4 weeks

## 🗂️ Section Contents

### Object-Oriented Design Principles
- **[SOLID Principles](object-oriented-design/solid-principles.md)** 🟢
  - Single Responsibility, Open/Closed, Liskov Substitution
  - Interface Segregation, Dependency Inversion
  - Real-world examples and violations

- **[Design Principles](object-oriented-design/design-principles.md)** 🟢
  - DRY, KISS, YAGNI
  - Composition over Inheritance
  - Encapsulation and Abstraction

### Design Patterns
- **[Creational Patterns](design-patterns/creational/)** 🟡
  - Singleton, Factory, Builder, Prototype
  - When and how to use each pattern

- **[Structural Patterns](design-patterns/structural/)** 🟡
  - Adapter, Decorator, Facade, Proxy
  - Pattern combinations and real-world usage

- **[Behavioral Patterns](design-patterns/behavioral/)** 🟡
  - Observer, Strategy, Command, State
  - Communication between objects

### Advanced Implementation Concepts
- **[Thread-Safe Data Structures](data-structures-implementation/)** 🔴
  - Concurrent collections
  - Lock-free programming
  - Performance considerations

### Real-World Case Studies
- **[Parking Lot System](case-studies/parking-lot/)** 🟢
- **[Elevator Control System](case-studies/elevator-system/)** 🟡
- **[Chess Game Engine](case-studies/chess-game/)** 🟡
- **[Library Management System](case-studies/library-management/)** 🔴

## 📖 Study Guide

### Week 1: Foundations (🟢 Beginner)
**Day 1-3**: SOLID Principles
- Study each principle with examples
- Identify violations in existing code
- **Exercise**: Refactor code to follow SOLID principles

**Day 4-5**: Design Principles
- Learn DRY, KISS, YAGNI
- Practice composition over inheritance
- **Exercise**: Design a simple media player class hierarchy

**Day 6-7**: Introduction to Design Patterns
- Understand the purpose of design patterns
- Study 2-3 basic patterns (Singleton, Factory, Observer)
- **Exercise**: Implement a simple notification system

### Week 2: Design Patterns (🟡 Intermediate)
**Day 1-3**: Creational Patterns
- Master Factory, Builder, Singleton patterns
- Understand when to use each
- **Exercise**: Build a game character creation system

**Day 4-5**: Structural Patterns
- Learn Adapter, Decorator, Facade patterns
- Practice pattern combinations
- **Exercise**: Create a logging framework with decorators

**Day 6-7**: Behavioral Patterns
- Study Observer, Strategy, State patterns
- Understand object communication
- **Exercise**: Implement a simple state machine

### Week 3: Case Studies (🟡 Intermediate)
**Day 1-3**: Parking Lot System
- Analyze requirements thoroughly
- Design class hierarchy and relationships
- **Exercise**: Complete implementation with all features

**Day 4-7**: Elevator System
- Handle complex state management
- Design for extensibility and safety
- **Exercise**: Add monitoring and analytics features

### Week 4: Advanced Topics (🔴 Advanced)
**Day 1-3**: Thread-Safe Implementations
- Learn about concurrent programming challenges
- Study lock-free data structures
- **Exercise**: Implement a thread-safe cache

**Day 4-7**: Library Management System
- Design for complex business rules
- Handle multiple user types and permissions
- **Exercise**: Add advanced features like reservations and renewals

## ✅ Progress Checklist

### Design Principles Mastery
- [ ] Can identify and fix SOLID principle violations
- [ ] Consistently apply DRY, KISS, YAGNI in code
- [ ] Choose composition over inheritance appropriately
- [ ] Design clean interfaces and abstractions

### Design Pattern Knowledge
- [ ] Know when to apply each of the 23 GoF patterns
- [ ] Can implement patterns without looking up syntax
- [ ] Understand pattern trade-offs and alternatives
- [ ] Can combine patterns effectively

### System Design Skills
- [ ] Can design extensible class hierarchies
- [ ] Handle complex business logic cleanly
- [ ] Design for testability and maintainability
- [ ] Consider performance and scalability in designs

### Implementation Quality
- [ ] Write thread-safe code when needed
- [ ] Handle edge cases and error conditions
- [ ] Create comprehensive unit tests
- [ ] Document design decisions clearly

## 🎯 Case Study Deep Dive: Parking Lot System

### Requirements Analysis
**Functional Requirements:**
- Multiple vehicle types (car, truck, motorcycle)
- Different parking spot sizes
- Track occupancy and availability
- Calculate parking fees
- Generate reports

**Non-Functional Requirements:**
- System should handle 1000+ concurrent operations
- Response time < 100ms for basic operations
- 99.9% availability
- Easy to add new vehicle types

### Design Approach
1. **Identify main entities**: Vehicle, ParkingSpot, ParkingLot, Ticket
2. **Define relationships**: One-to-many, inheritance hierarchies
3. **Apply patterns**: Factory for vehicle creation, Strategy for pricing
4. **Handle concurrency**: Thread-safe spot allocation
5. **Plan for extension**: Plugin architecture for new features

### Implementation Highlights
```python
# Example of good OOP design
class ParkingLot:
    def __init__(self, capacity_config):
        self.spots = self._create_spots(capacity_config)
        self.pricing_strategy = PricingStrategyFactory.create()
        self.availability_tracker = AvailabilityTracker()

    def park_vehicle(self, vehicle):
        spot = self._find_available_spot(vehicle.get_type())
        if spot:
            ticket = self._issue_ticket(vehicle, spot)
            self.availability_tracker.occupy_spot(spot)
            return ticket
        raise NoAvailableSpotException()
```

## 🛠️ Practical Exercises

### Exercise 1: SOLID Principles
Refactor this code to follow SOLID principles:
```python
class EmailService:
    def send_email(self, user, subject, body):
        # Validates email
        if not self.is_valid_email(user.email):
            raise ValueError("Invalid email")

        # Formats email
        formatted_body = self.format_html(body)

        # Sends via SMTP
        smtp_client = SMTPClient()
        smtp_client.send(user.email, subject, formatted_body)

        # Logs the action
        logger = FileLogger()
        logger.log(f"Email sent to {user.email}")
```

### Exercise 2: Design Pattern Application
Design a text editor that supports:
- Multiple file formats (TXT, HTML, Markdown)
- Undo/Redo functionality
- Plugin architecture for new features
- Real-time collaboration

Which patterns would you use and why?

### Exercise 3: Performance Optimization
Given a thread-safe cache implementation:
```python
import threading

class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            return self._cache.get(key)

    def put(self, key, value):
        with self._lock:
            self._cache[key] = value
```

How would you optimize this for better concurrent performance?

## 🔍 Code Review Checklist

When reviewing LLD implementations, check for:

**Design Quality:**
- [ ] Classes have single, clear responsibilities
- [ ] Interfaces are well-defined and minimal
- [ ] Dependencies are injected, not hard-coded
- [ ] Code follows established patterns appropriately

**Implementation Quality:**
- [ ] Proper error handling and edge cases
- [ ] Thread safety where required
- [ ] Performance considerations addressed
- [ ] Code is testable and well-documented

**Extensibility:**
- [ ] Easy to add new features without modifying existing code
- [ ] Configuration is externalized
- [ ] Plugin architecture where appropriate
- [ ] Clear extension points defined

## 🚀 Advanced Topics

### Design for Testability
- Dependency injection for mock objects
- Interface segregation for focused testing
- Test doubles and testing strategies

### Performance Considerations
- Object pooling for expensive objects
- Lazy initialization patterns
- Memory-efficient data structures

### Scalability Patterns
- Immutable objects for thread safety
- Copy-on-write collections
- Lock-free programming techniques

## 📚 Recommended Reading

### Essential Books
- "Design Patterns" by Gang of Four
- "Clean Code" by Robert Martin
- "Effective Java" by Joshua Bloch
- "Head First Design Patterns"

### Online Resources
- Refactoring.guru for pattern examples
- SourceMaking.com for design principles
- Martin Fowler's blog on design topics

## 🚀 Next Steps

After mastering LLD:
1. **For system design**: Move to [03-high-level-design](../03-high-level-design/)
2. **For interviews**: Practice [case studies](case-studies/) and [interview questions](../05-interview-preparation/)
3. **For specialization**: Explore [advanced topics](../07-advanced-topics/)

---

**Remember**: Good low-level design is the foundation of all great software. Take time to practice and internalize these principles!