# Structural Design Patterns 🟡

## 🎯 Learning Objectives
- Master structural patterns for object composition
- Understand how to combine objects and classes
- Learn to create flexible and efficient structures
- Implement patterns that simplify complex relationships

## 📖 Overview

Structural patterns deal with object composition and typically identify simple ways to realize relationships between entities. They help ensure that when one part changes, the entire structure doesn't need to change.

## 🔌 Adapter Pattern

### Problem
Need to make incompatible interfaces work together.

### Solution
Create an adapter that translates one interface to another.

```python
# Target interface (what client expects)
class MediaPlayer:
    def play(self, audio_type, filename):
        pass

# Adaptee (existing interface that needs adaptation)
class Mp3Player:
    def play_mp3(self, filename):
        return f"Playing MP3 file: {filename}"

class Mp4Player:
    def play_mp4(self, filename):
        return f"Playing MP4 file: {filename}"

class FlacPlayer:
    def play_flac(self, filename):
        return f"Playing FLAC file: {filename}"

# Adapter
class MediaAdapter:
    def __init__(self, audio_type):
        self.audio_type = audio_type
        if audio_type == "mp4":
            self.player = Mp4Player()
        elif audio_type == "flac":
            self.player = FlacPlayer()

    def play(self, audio_type, filename):
        if audio_type == "mp4":
            return self.player.play_mp4(filename)
        elif audio_type == "flac":
            return self.player.play_flac(filename)

# Client
class AudioPlayer(MediaPlayer):
    def play(self, audio_type, filename):
        if audio_type == "mp3":
            mp3_player = Mp3Player()
            return mp3_player.play_mp3(filename)
        elif audio_type in ["mp4", "flac"]:
            adapter = MediaAdapter(audio_type)
            return adapter.play(audio_type, filename)
        else:
            return f"Invalid media. {audio_type} format not supported"

# Usage
player = AudioPlayer()
print(player.play("mp3", "song.mp3"))
print(player.play("mp4", "video.mp4"))
print(player.play("flac", "audio.flac"))
```

### When to Use Adapter Pattern
- ✅ Legacy code integration
- ✅ Third-party library compatibility
- ✅ Interface mismatch resolution
- ✅ Making incompatible classes work together

## 🌉 Bridge Pattern

### Problem
Want to separate abstraction from implementation so both can vary independently.

### Solution
Create a bridge between abstraction and implementation.

```python
from abc import ABC, abstractmethod

# Implementation interface
class DrawingAPI(ABC):
    @abstractmethod
    def draw_circle(self, x, y, radius):
        pass

    @abstractmethod
    def draw_rectangle(self, x1, y1, x2, y2):
        pass

# Concrete implementations
class DrawingAPI1(DrawingAPI):
    def draw_circle(self, x, y, radius):
        return f"API1: Drawing circle at ({x}, {y}) with radius {radius}"

    def draw_rectangle(self, x1, y1, x2, y2):
        return f"API1: Drawing rectangle from ({x1}, {y1}) to ({x2}, {y2})"

class DrawingAPI2(DrawingAPI):
    def draw_circle(self, x, y, radius):
        return f"API2: Circle({x}, {y}, {radius})"

    def draw_rectangle(self, x1, y1, x2, y2):
        return f"API2: Rectangle[{x1}, {y1}, {x2}, {y2}]"

# Abstraction
class Shape(ABC):
    def __init__(self, drawing_api: DrawingAPI):
        self.drawing_api = drawing_api

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def resize(self, factor):
        pass

# Refined abstractions
class Circle(Shape):
    def __init__(self, x, y, radius, drawing_api):
        super().__init__(drawing_api)
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self):
        return self.drawing_api.draw_circle(self.x, self.y, self.radius)

    def resize(self, factor):
        self.radius *= factor

class Rectangle(Shape):
    def __init__(self, x1, y1, x2, y2, drawing_api):
        super().__init__(drawing_api)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def draw(self):
        return self.drawing_api.draw_rectangle(self.x1, self.y1, self.x2, self.y2)

    def resize(self, factor):
        self.x2 = self.x1 + (self.x2 - self.x1) * factor
        self.y2 = self.y1 + (self.y2 - self.y1) * factor

# Usage
shapes = [
    Circle(1, 2, 3, DrawingAPI1()),
    Circle(5, 7, 11, DrawingAPI2()),
    Rectangle(1, 2, 3, 4, DrawingAPI1()),
    Rectangle(5, 6, 7, 8, DrawingAPI2())
]

for shape in shapes:
    print(shape.draw())
    shape.resize(2)
    print(f"After resize: {shape.draw()}")
```

### When to Use Bridge Pattern
- ✅ Want to avoid permanent binding between abstraction and implementation
- ✅ Need to share implementation among multiple objects
- ✅ Changes in implementation shouldn't affect clients
- ✅ Want to extend abstractions and implementations independently

## 🎭 Decorator Pattern

### Problem
Want to add behavior to objects dynamically without altering their structure.

### Solution
Wrap objects with decorator classes that add new functionality.

```python
from abc import ABC, abstractmethod
import functools

# Component interface
class Coffee(ABC):
    @abstractmethod
    def cost(self):
        pass

    @abstractmethod
    def description(self):
        pass

# Concrete component
class SimpleCoffee(Coffee):
    def cost(self):
        return 5.0

    def description(self):
        return "Simple coffee"

# Base decorator
class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self._coffee = coffee

    def cost(self):
        return self._coffee.cost()

    def description(self):
        return self._coffee.description()

# Concrete decorators
class MilkDecorator(CoffeeDecorator):
    def cost(self):
        return self._coffee.cost() + 1.5

    def description(self):
        return self._coffee.description() + ", milk"

class SugarDecorator(CoffeeDecorator):
    def cost(self):
        return self._coffee.cost() + 0.5

    def description(self):
        return self._coffee.description() + ", sugar"

class WhipDecorator(CoffeeDecorator):
    def cost(self):
        return self._coffee.cost() + 2.0

    def description(self):
        return self._coffee.description() + ", whip"

# Python decorator approach (alternative)
def add_milk(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return {
            'cost': result['cost'] + 1.5,
            'description': result['description'] + ', milk'
        }
    return wrapper

def add_sugar(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return {
            'cost': result['cost'] + 0.5,
            'description': result['description'] + ', sugar'
        }
    return wrapper

@add_milk
@add_sugar
def make_coffee():
    return {'cost': 5.0, 'description': 'Simple coffee'}

# Usage
coffee = SimpleCoffee()
print(f"{coffee.description()}: ${coffee.cost()}")

# Add milk
coffee = MilkDecorator(coffee)
print(f"{coffee.description()}: ${coffee.cost()}")

# Add sugar
coffee = SugarDecorator(coffee)
print(f"{coffee.description()}: ${coffee.cost()}")

# Add whip
coffee = WhipDecorator(coffee)
print(f"{coffee.description()}: ${coffee.cost()}")

# Python decorator approach
coffee_result = make_coffee()
print(f"{coffee_result['description']}: ${coffee_result['cost']}")
```

### When to Use Decorator Pattern
- ✅ Add responsibilities to objects dynamically
- ✅ Extend functionality without subclassing
- ✅ Compose behaviors in different combinations
- ✅ Remove responsibilities from objects

## 🏢 Facade Pattern

### Problem
Complex subsystem with many classes makes it difficult for clients to use.

### Solution
Provide a simplified interface to a complex subsystem.

```python
# Complex subsystem classes
class CPU:
    def freeze(self):
        return "CPU: Freezing processor"

    def jump(self, position):
        return f"CPU: Jumping to position {position}"

    def execute(self):
        return "CPU: Executing instructions"

class Memory:
    def load(self, position, data):
        return f"Memory: Loading data '{data}' at position {position}"

class HardDrive:
    def read(self, lba, size):
        return f"HardDrive: Reading {size} bytes from LBA {lba}"

class GPU:
    def render(self, data):
        return f"GPU: Rendering {data}"

class NetworkInterface:
    def connect(self, address):
        return f"Network: Connecting to {address}"

    def send(self, data):
        return f"Network: Sending {data}"

# Facade
class ComputerFacade:
    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hard_drive = HardDrive()
        self.gpu = GPU()
        self.network = NetworkInterface()

    def start_computer(self):
        results = []
        results.append(self.cpu.freeze())
        results.append(self.memory.load(0, "boot_data"))
        results.append(self.hard_drive.read(100, 1024))
        results.append(self.cpu.jump(0))
        results.append(self.cpu.execute())
        results.append("Computer started successfully!")
        return results

    def shutdown_computer(self):
        results = []
        results.append("Saving state...")
        results.append(self.memory.load(0, "shutdown_data"))
        results.append(self.cpu.freeze())
        results.append("Computer shut down successfully!")
        return results

    def play_video(self, video_file):
        results = []
        results.append(self.hard_drive.read(200, 2048))
        results.append(self.gpu.render(video_file))
        results.append(f"Playing video: {video_file}")
        return results

    def browse_internet(self, url):
        results = []
        results.append(self.network.connect("internet"))
        results.append(self.network.send(f"GET {url}"))
        results.append(f"Browsing: {url}")
        return results

# Usage
computer = ComputerFacade()

print("=== Starting Computer ===")
for result in computer.start_computer():
    print(result)

print("\n=== Playing Video ===")
for result in computer.play_video("movie.mp4"):
    print(result)

print("\n=== Browsing Internet ===")
for result in computer.browse_internet("https://example.com"):
    print(result)

print("\n=== Shutting Down ===")
for result in computer.shutdown_computer():
    print(result)
```

### When to Use Facade Pattern
- ✅ Simplify complex subsystem interfaces
- ✅ Decouple clients from subsystem components
- ✅ Layer subsystems with facades
- ✅ Provide single entry point to subsystem

## 🪶 Flyweight Pattern

### Problem
Need to support large numbers of fine-grained objects efficiently.

### Solution
Share common state externally and pass context as parameters.

```python
import weakref

class TreeType:
    """Flyweight class containing intrinsic state"""
    def __init__(self, name, color, sprite):
        self.name = name
        self.color = color
        self.sprite = sprite

    def render(self, canvas, x, y, size):
        """Operation that uses both intrinsic and extrinsic state"""
        return f"Rendering {self.color} {self.name} tree at ({x}, {y}) size={size} sprite={self.sprite}"

class TreeTypeFactory:
    """Flyweight factory"""
    _tree_types = {}

    @classmethod
    def get_tree_type(cls, name, color, sprite):
        key = (name, color, sprite)
        if key not in cls._tree_types:
            cls._tree_types[key] = TreeType(name, color, sprite)
            print(f"Created new TreeType: {name} {color}")
        return cls._tree_types[key]

    @classmethod
    def get_created_flyweights(cls):
        return len(cls._tree_types)

class Tree:
    """Context class containing extrinsic state"""
    def __init__(self, x, y, size, tree_type):
        self.x = x
        self.y = y
        self.size = size
        self.tree_type = tree_type  # Reference to flyweight

    def render(self, canvas):
        return self.tree_type.render(canvas, self.x, self.y, self.size)

class Forest:
    """Client that manages flyweights"""
    def __init__(self):
        self.trees = []

    def plant_tree(self, x, y, size, name, color, sprite):
        tree_type = TreeTypeFactory.get_tree_type(name, color, sprite)
        tree = Tree(x, y, size, tree_type)
        self.trees.append(tree)

    def render(self, canvas):
        results = []
        for tree in self.trees:
            results.append(tree.render(canvas))
        return results

    def get_tree_count(self):
        return len(self.trees)

# Advanced flyweight with method-level sharing
class Character:
    """Flyweight for text formatting"""
    def __init__(self, letter, font, size):
        self.letter = letter
        self.font = font
        self.size = size

    def display(self, x, y, color):
        return f"'{self.letter}' at ({x}, {y}) font={self.font} size={self.size} color={color}"

class CharacterFactory:
    _characters = {}

    @classmethod
    def get_character(cls, letter, font, size):
        key = (letter, font, size)
        if key not in cls._characters:
            cls._characters[key] = Character(letter, font, size)
        return cls._characters[key]

    @classmethod
    def pool_size(cls):
        return len(cls._characters)

class Document:
    def __init__(self):
        self.characters = []

    def add_character(self, letter, font, size, x, y, color):
        char = CharacterFactory.get_character(letter, font, size)
        self.characters.append({
            'char': char,
            'x': x,
            'y': y,
            'color': color
        })

    def render(self):
        results = []
        for char_info in self.characters:
            result = char_info['char'].display(
                char_info['x'],
                char_info['y'],
                char_info['color']
            )
            results.append(result)
        return results

# Usage
print("=== Forest Example ===")
forest = Forest()

# Plant many trees
forest.plant_tree(10, 20, 5, "Oak", "Green", "oak_sprite.png")
forest.plant_tree(15, 25, 6, "Oak", "Green", "oak_sprite.png")  # Reuses flyweight
forest.plant_tree(30, 40, 4, "Pine", "Dark Green", "pine_sprite.png")
forest.plant_tree(35, 45, 3, "Pine", "Dark Green", "pine_sprite.png")  # Reuses flyweight
forest.plant_tree(50, 60, 7, "Oak", "Brown", "oak_sprite.png")  # New flyweight

print(f"Total trees: {forest.get_tree_count()}")
print(f"TreeTypes created: {TreeTypeFactory.get_created_flyweights()}")

canvas = "MainCanvas"
for render_result in forest.render(canvas):
    print(render_result)

print("\n=== Document Example ===")
doc = Document()

# Add characters to document
text = "Hello World!"
for i, letter in enumerate(text):
    doc.add_character(letter, "Arial", 12, i * 10, 0, "Black")

print(f"Characters in document: {len(doc.characters)}")
print(f"Character flyweights created: {CharacterFactory.pool_size()}")

for render_result in doc.render():
    print(render_result)
```

### When to Use Flyweight Pattern
- ✅ Large numbers of similar objects
- ✅ Storage costs are high
- ✅ Object state can be divided into intrinsic and extrinsic
- ✅ Groups of objects can be replaced by fewer shared objects

## 🗂️ Composite Pattern

### Problem
Need to work with tree structures where individual objects and compositions should be treated uniformly.

### Solution
Compose objects into tree structures and let clients treat individual objects and compositions uniformly.

```python
from abc import ABC, abstractmethod
from typing import List

# Component interface
class FileSystemComponent(ABC):
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_size(self):
        pass

    @abstractmethod
    def display(self, indent=0):
        pass

    def add(self, component):
        raise NotImplementedError("Cannot add to leaf")

    def remove(self, component):
        raise NotImplementedError("Cannot remove from leaf")

    def get_child(self, index):
        raise NotImplementedError("Cannot get child from leaf")

# Leaf component
class File(FileSystemComponent):
    def __init__(self, name, size):
        self._name = name
        self._size = size

    def get_name(self):
        return self._name

    def get_size(self):
        return self._size

    def display(self, indent=0):
        return "  " * indent + f"📄 {self._name} ({self._size} bytes)"

# Composite component
class Directory(FileSystemComponent):
    def __init__(self, name):
        self._name = name
        self._children: List[FileSystemComponent] = []

    def get_name(self):
        return self._name

    def get_size(self):
        return sum(child.get_size() for child in self._children)

    def add(self, component: FileSystemComponent):
        self._children.append(component)

    def remove(self, component: FileSystemComponent):
        if component in self._children:
            self._children.remove(component)

    def get_child(self, index):
        if 0 <= index < len(self._children):
            return self._children[index]
        return None

    def display(self, indent=0):
        result = "  " * indent + f"📁 {self._name}/ ({self.get_size()} bytes total)\n"
        for child in self._children:
            result += child.display(indent + 1) + "\n"
        return result.rstrip()

# Advanced example: GUI Components
class UIComponent(ABC):
    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def get_bounds(self):
        pass

    def add(self, component):
        raise NotImplementedError()

    def remove(self, component):
        raise NotImplementedError()

class Button(UIComponent):
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def render(self):
        return f"Button('{self.text}') at ({self.x}, {self.y})"

    def get_bounds(self):
        return (self.x, self.y, self.width, self.height)

class TextBox(UIComponent):
    def __init__(self, placeholder, x, y, width, height):
        self.placeholder = placeholder
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def render(self):
        return f"TextBox('{self.placeholder}') at ({self.x}, {self.y})"

    def get_bounds(self):
        return (self.x, self.y, self.width, self.height)

class Panel(UIComponent):
    def __init__(self, name, x, y, width, height):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.children = []

    def add(self, component):
        self.children.append(component)

    def remove(self, component):
        if component in self.children:
            self.children.remove(component)

    def render(self):
        result = f"Panel('{self.name}') at ({self.x}, {self.y})\n"
        for child in self.children:
            child_render = child.render()
            result += f"  └─ {child_render}\n"
        return result.rstrip()

    def get_bounds(self):
        return (self.x, self.y, self.width, self.height)

# Usage
print("=== File System Example ===")
root = Directory("root")
documents = Directory("documents")
pictures = Directory("pictures")

# Add files
documents.add(File("resume.pdf", 1024))
documents.add(File("cover_letter.doc", 512))
pictures.add(File("vacation.jpg", 2048))
pictures.add(File("family.png", 1536))

# Create nested structure
root.add(documents)
root.add(pictures)
root.add(File("readme.txt", 256))

print(root.display())
print(f"\nTotal size: {root.get_size()} bytes")

print("\n=== GUI Example ===")
main_panel = Panel("MainPanel", 0, 0, 800, 600)
login_panel = Panel("LoginPanel", 100, 100, 300, 200)

# Add components to login panel
login_panel.add(TextBox("Username", 10, 10, 200, 30))
login_panel.add(TextBox("Password", 10, 50, 200, 30))
login_panel.add(Button("Login", 10, 90, 80, 30))
login_panel.add(Button("Cancel", 100, 90, 80, 30))

# Add login panel to main panel
main_panel.add(login_panel)
main_panel.add(Button("Exit", 700, 10, 60, 30))

print(main_panel.render())
```

### When to Use Composite Pattern
- ✅ Represent part-whole hierarchies
- ✅ Treat individual and composite objects uniformly
- ✅ Build recursive tree structures
- ✅ Simplify client code working with trees

## ⚖️ Pattern Comparison

| Pattern | Purpose | When to Use | Complexity |
|---------|---------|-------------|------------|
| **Adapter** | Interface compatibility | Legacy integration | Low |
| **Bridge** | Separate abstraction/implementation | Independent variations | Medium |
| **Decorator** | Add behavior dynamically | Flexible extensions | Medium |
| **Facade** | Simplify complex subsystem | Hide complexity | Low |
| **Flyweight** | Share objects efficiently | Many similar objects | High |
| **Composite** | Tree structures | Part-whole hierarchies | Medium |

## 🛠️ Practical Exercise

Design a text editor system using multiple structural patterns:

```python
# Your task: Implement a text editor that:
# 1. Uses Composite for document structure (paragraphs, sections)
# 2. Uses Decorator for text formatting (bold, italic, underline)
# 3. Uses Facade for complex editing operations
# 4. Uses Flyweight for character storage optimization

class TextElement:
    """Base class for text elements"""
    pass

# Implement the patterns here...
```

## ✅ Knowledge Check

- [ ] Can implement Adapter for interface compatibility
- [ ] Understand Bridge pattern for abstraction separation
- [ ] Know how to use Decorator for dynamic behavior
- [ ] Can create Facade for complex subsystems
- [ ] Understand Flyweight for memory optimization
- [ ] Can build Composite tree structures

## 🚀 Next Steps

- Study [Behavioral Patterns](../behavioral/) for object interaction
- Practice with [Case Studies](../../case-studies/)
- Apply patterns in [Real-World Examples](../../../04-real-world-examples/)