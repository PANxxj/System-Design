# Data Structures Implementation 🟢

## 🎯 Learning Objectives
- Implement fundamental data structures from scratch
- Understand time and space complexity trade-offs
- Design thread-safe data structures
- Optimize data structures for specific use cases

## 📊 Core Data Structures

### 1. Dynamic Array (ArrayList)

```python
class DynamicArray:
    def __init__(self, initial_capacity=10):
        self.capacity = initial_capacity
        self.size = 0
        self.data = [None] * self.capacity

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        if not 0 <= index < self.size:
            raise IndexError("Index out of range")
        return self.data[index]

    def __setitem__(self, index, value):
        if not 0 <= index < self.size:
            raise IndexError("Index out of range")
        self.data[index] = value

    def append(self, value):
        if self.size == self.capacity:
            self._resize()
        self.data[self.size] = value
        self.size += 1

    def insert(self, index, value):
        if not 0 <= index <= self.size:
            raise IndexError("Index out of range")

        if self.size == self.capacity:
            self._resize()

        # Shift elements to the right
        for i in range(self.size, index, -1):
            self.data[i] = self.data[i - 1]

        self.data[index] = value
        self.size += 1

    def remove(self, index):
        if not 0 <= index < self.size:
            raise IndexError("Index out of range")

        # Shift elements to the left
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]

        self.size -= 1
        self.data[self.size] = None

        # Shrink if necessary
        if self.size < self.capacity // 4:
            self._shrink()

    def _resize(self):
        old_data = self.data
        self.capacity *= 2
        self.data = [None] * self.capacity

        for i in range(self.size):
            self.data[i] = old_data[i]

    def _shrink(self):
        if self.capacity <= 10:  # Minimum capacity
            return

        old_data = self.data
        self.capacity //= 2
        self.data = [None] * self.capacity

        for i in range(self.size):
            self.data[i] = old_data[i]

# Usage and testing
arr = DynamicArray()
for i in range(15):
    arr.append(i)
print(f"Array size: {len(arr)}, Capacity: {arr.capacity}")
```

**Time Complexity:**
- Access: O(1)
- Append: O(1) amortized
- Insert: O(n)
- Remove: O(n)

### 2. Linked List

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def __len__(self):
        return self.size

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def insert(self, index, data):
        if index < 0 or index > self.size:
            raise IndexError("Index out of range")

        if index == 0:
            self.prepend(data)
            return

        new_node = Node(data)
        current = self.head
        for _ in range(index - 1):
            current = current.next

        new_node.next = current.next
        current.next = new_node
        self.size += 1

    def remove(self, index):
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")

        if index == 0:
            self.head = self.head.next
            self.size -= 1
            return

        current = self.head
        for _ in range(index - 1):
            current = current.next

        current.next = current.next.next
        self.size -= 1

    def find(self, data):
        current = self.head
        index = 0
        while current:
            if current.data == data:
                return index
            current = current.next
            index += 1
        return -1

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

# Doubly Linked List
class DoublyNode:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data):
        new_node = DoublyNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def prepend(self, data):
        new_node = DoublyNode(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1

    def remove_node(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        self.size -= 1
```

### 3. Stack Implementation

```python
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

# Stack with Linked List (memory efficient)
class LinkedStack:
    def __init__(self):
        self.head = None
        self.size = 0

    def push(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def pop(self):
        if not self.head:
            raise IndexError("Stack is empty")

        data = self.head.data
        self.head = self.head.next
        self.size -= 1
        return data

    def peek(self):
        if not self.head:
            raise IndexError("Stack is empty")
        return self.head.data

    def is_empty(self):
        return self.head is None

# Min Stack - O(1) min operation
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, x):
        self.stack.append(x)
        if not self.min_stack or x <= self.min_stack[-1]:
            self.min_stack.append(x)

    def pop(self):
        if not self.stack:
            raise IndexError("Stack is empty")

        value = self.stack.pop()
        if value == self.min_stack[-1]:
            self.min_stack.pop()
        return value

    def top(self):
        if not self.stack:
            raise IndexError("Stack is empty")
        return self.stack[-1]

    def get_min(self):
        if not self.min_stack:
            raise IndexError("Stack is empty")
        return self.min_stack[-1]
```

### 4. Queue Implementation

```python
from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items.popleft()

    def front(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

# Circular Queue
class CircularQueue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.head = 0
        self.tail = 0
        self.size = 0

    def enqueue(self, item):
        if self.is_full():
            raise OverflowError("Queue is full")

        self.queue[self.tail] = item
        self.tail = (self.tail + 1) % self.capacity
        self.size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")

        item = self.queue[self.head]
        self.queue[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self.size -= 1
        return item

    def is_empty(self):
        return self.size == 0

    def is_full(self):
        return self.size == self.capacity

# Priority Queue using Heap
import heapq

class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.index = 0

    def push(self, item, priority):
        # Use negative priority for max heap behavior
        heapq.heappush(self.heap, (priority, self.index, item))
        self.index += 1

    def pop(self):
        if not self.heap:
            raise IndexError("Priority queue is empty")
        return heapq.heappop(self.heap)[2]

    def peek(self):
        if not self.heap:
            raise IndexError("Priority queue is empty")
        return self.heap[0][2]

    def is_empty(self):
        return len(self.heap) == 0
```

### 5. Hash Table Implementation

```python
class HashTable:
    def __init__(self, initial_capacity=16):
        self.capacity = initial_capacity
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]

    def _hash(self, key):
        return hash(key) % self.capacity

    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.size = 0
        self.buckets = [[] for _ in range(self.capacity)]

        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)

    def put(self, key, value):
        if self.size >= self.capacity * 0.75:  # Load factor threshold
            self._resize()

        index = self._hash(key)
        bucket = self.buckets[index]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self.size += 1

    def get(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]

        for k, v in bucket:
            if k == key:
                return v

        raise KeyError(key)

    def remove(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return

        raise KeyError(key)

    def keys(self):
        result = []
        for bucket in self.buckets:
            for key, _ in bucket:
                result.append(key)
        return result

# Open Addressing Hash Table
class OpenAddressingHashTable:
    def __init__(self, initial_capacity=16):
        self.capacity = initial_capacity
        self.size = 0
        self.keys = [None] * self.capacity
        self.values = [None] * self.capacity
        self.deleted = [False] * self.capacity

    def _hash(self, key):
        return hash(key) % self.capacity

    def _probe(self, key):
        index = self._hash(key)
        while self.keys[index] is not None:
            if self.keys[index] == key and not self.deleted[index]:
                return index
            index = (index + 1) % self.capacity
        return index

    def put(self, key, value):
        if self.size >= self.capacity * 0.5:  # Lower threshold for open addressing
            self._resize()

        index = self._probe(key)
        if self.keys[index] is None or self.deleted[index]:
            self.size += 1

        self.keys[index] = key
        self.values[index] = value
        self.deleted[index] = False

    def get(self, key):
        index = self._probe(key)
        if self.keys[index] == key and not self.deleted[index]:
            return self.values[index]
        raise KeyError(key)

    def remove(self, key):
        index = self._probe(key)
        if self.keys[index] == key and not self.deleted[index]:
            self.deleted[index] = True
            self.size -= 1
            return
        raise KeyError(key)
```

### 6. Binary Search Tree

```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, val):
        self.root = self._insert_recursive(self.root, val)

    def _insert_recursive(self, node, val):
        if not node:
            return TreeNode(val)

        if val < node.val:
            node.left = self._insert_recursive(node.left, val)
        elif val > node.val:
            node.right = self._insert_recursive(node.right, val)

        return node

    def search(self, val):
        return self._search_recursive(self.root, val)

    def _search_recursive(self, node, val):
        if not node or node.val == val:
            return node

        if val < node.val:
            return self._search_recursive(node.left, val)
        return self._search_recursive(node.right, val)

    def delete(self, val):
        self.root = self._delete_recursive(self.root, val)

    def _delete_recursive(self, node, val):
        if not node:
            return node

        if val < node.val:
            node.left = self._delete_recursive(node.left, val)
        elif val > node.val:
            node.right = self._delete_recursive(node.right, val)
        else:
            # Node to be deleted found
            if not node.left:
                return node.right
            elif not node.right:
                return node.left

            # Node has two children
            successor = self._find_min(node.right)
            node.val = successor.val
            node.right = self._delete_recursive(node.right, successor.val)

        return node

    def _find_min(self, node):
        while node.left:
            node = node.left
        return node

    def inorder_traversal(self):
        result = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node, result):
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.val)
            self._inorder_recursive(node.right, result)
```

### 7. Heap Implementation

```python
class MinHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def insert(self, val):
        self.heap.append(val)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, i):
        parent_idx = self.parent(i)
        if i > 0 and self.heap[i] < self.heap[parent_idx]:
            self.swap(i, parent_idx)
            self._heapify_up(parent_idx)

    def extract_min(self):
        if not self.heap:
            raise IndexError("Heap is empty")

        if len(self.heap) == 1:
            return self.heap.pop()

        min_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return min_val

    def _heapify_down(self, i):
        smallest = i
        left = self.left_child(i)
        right = self.right_child(i)

        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left

        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right

        if smallest != i:
            self.swap(i, smallest)
            self._heapify_down(smallest)

    def peek(self):
        if not self.heap:
            raise IndexError("Heap is empty")
        return self.heap[0]

    def size(self):
        return len(self.heap)

    def is_empty(self):
        return len(self.heap) == 0

class MaxHeap(MinHeap):
    def _heapify_up(self, i):
        parent_idx = self.parent(i)
        if i > 0 and self.heap[i] > self.heap[parent_idx]:
            self.swap(i, parent_idx)
            self._heapify_up(parent_idx)

    def _heapify_down(self, i):
        largest = i
        left = self.left_child(i)
        right = self.right_child(i)

        if left < len(self.heap) and self.heap[left] > self.heap[largest]:
            largest = left

        if right < len(self.heap) and self.heap[right] > self.heap[largest]:
            largest = right

        if largest != i:
            self.swap(i, largest)
            self._heapify_down(largest)
```

## 🧵 Thread-Safe Data Structures

### Thread-Safe Queue

```python
import threading
from collections import deque

class ThreadSafeQueue:
    def __init__(self, maxsize=0):
        self.queue = deque()
        self.maxsize = maxsize
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)

    def put(self, item, block=True, timeout=None):
        with self.not_full:
            if self.maxsize > 0:
                while len(self.queue) >= self.maxsize:
                    if not block:
                        raise Exception("Queue is full")
                    self.not_full.wait(timeout)

            self.queue.append(item)
            self.not_empty.notify()

    def get(self, block=True, timeout=None):
        with self.not_empty:
            while not self.queue:
                if not block:
                    raise Exception("Queue is empty")
                self.not_empty.wait(timeout)

            item = self.queue.popleft()
            self.not_full.notify()
            return item

    def size(self):
        with self.lock:
            return len(self.queue)

    def empty(self):
        with self.lock:
            return len(self.queue) == 0
```

## 📈 Performance Analysis

### Time Complexity Summary

| Operation | Array | Linked List | Stack | Queue | Hash Table | BST (Avg) | Heap |
|-----------|-------|-------------|-------|-------|------------|-----------|------|
| Access    | O(1)  | O(n)        | O(1)  | O(1)  | O(1)       | O(log n)  | O(1) |
| Search    | O(n)  | O(n)        | O(n)  | O(n)  | O(1)       | O(log n)  | O(n) |
| Insert    | O(n)  | O(1)        | O(1)  | O(1)  | O(1)       | O(log n)  | O(log n) |
| Delete    | O(n)  | O(1)        | O(1)  | O(1)  | O(1)       | O(log n)  | O(log n) |

### Space Complexity Summary

| Data Structure | Space Complexity |
|----------------|------------------|
| Array          | O(n)            |
| Linked List    | O(n)            |
| Stack          | O(n)            |
| Queue          | O(n)            |
| Hash Table     | O(n)            |
| BST            | O(n)            |
| Heap           | O(n)            |

## 🎯 Use Case Guidelines

### When to Use Each Data Structure

**Array/Dynamic Array:**
- Random access needed
- Cache-friendly operations
- Memory usage is a concern

**Linked List:**
- Frequent insertions/deletions
- Size varies significantly
- No random access needed

**Stack:**
- LIFO operations
- Function call management
- Expression evaluation
- Undo operations

**Queue:**
- FIFO operations
- Task scheduling
- BFS algorithms
- Buffer for data streams

**Hash Table:**
- Fast key-value lookups
- Implementing sets
- Caching
- Indexing

**Binary Search Tree:**
- Maintaining sorted data
- Range queries
- When you need both search and insert/delete

**Heap:**
- Priority queue operations
- Finding min/max efficiently
- Heap sort algorithm
- Scheduling algorithms

## ✅ Knowledge Check

After studying this section, you should be able to:

- [ ] Implement basic data structures from scratch
- [ ] Choose appropriate data structure for specific use cases
- [ ] Analyze time and space complexity
- [ ] Design thread-safe data structures
- [ ] Optimize data structures for performance

## 🔄 Next Steps

- Practice implementing these data structures in your preferred language
- Study [Design Patterns](../design-patterns/) to see how these structures are used
- Learn [Object-Oriented Design](../object-oriented-design/) principles
- Apply these concepts in [Case Studies](../case-studies/)