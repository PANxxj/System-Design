"""
LIBRARY MANAGEMENT SYSTEM - Interview Level
============================================

Problem Statement:
Design a library management system for borrowing and returning books.

Requirements:
1. Book catalog management
2. Member management
3. Borrow/Return books
4. Due date tracking
5. Fine calculation for late returns
6. Search books by title/author

Design Patterns:
- Singleton (Library)
- Factory (Member types)
- Strategy (Fine calculation)

Time Complexity: O(1) for most operations, O(n) for search
Space Complexity: O(n) for books and members
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


class BookStatus(Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    RESERVED = "RESERVED"
    LOST = "LOST"


class MemberType(Enum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    PUBLIC = "PUBLIC"


class Book:
    def __init__(self, isbn: str, title: str, author: str, category: str):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.category = category
        self.status = BookStatus.AVAILABLE

    def is_available(self) -> bool:
        return self.status == BookStatus.AVAILABLE

    def __str__(self):
        return f"'{self.title}' by {self.author} [{self.isbn}]"


class Member:
    def __init__(self, member_id: str, name: str, member_type: MemberType):
        self.member_id = member_id
        self.name = name
        self.member_type = member_type
        self.borrowed_books: List[str] = []  # List of ISBNs
        self.max_books = self._get_max_books()

    def _get_max_books(self) -> int:
        """Get max books allowed based on member type"""
        limits = {
            MemberType.STUDENT: 3,
            MemberType.FACULTY: 5,
            MemberType.PUBLIC: 2
        }
        return limits.get(self.member_type, 2)

    def can_borrow(self) -> bool:
        """Check if member can borrow more books"""
        return len(self.borrowed_books) < self.max_books

    def __str__(self):
        return f"{self.name} ({self.member_type.value}) [ID: {self.member_id}]"


class BorrowRecord:
    def __init__(self, member: Member, book: Book, borrow_days: int = 14):
        self.record_id = f"BR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.member = member
        self.book = book
        self.borrow_date = datetime.now()
        self.due_date = self.borrow_date + timedelta(days=borrow_days)
        self.return_date: Optional[datetime] = None
        self.fine: float = 0.0

    def is_overdue(self) -> bool:
        """Check if book is overdue"""
        if self.return_date:
            return False
        return datetime.now() > self.due_date

    def days_overdue(self) -> int:
        """Calculate days overdue"""
        if not self.is_overdue():
            return 0
        return (datetime.now() - self.due_date).days

    def __str__(self):
        status = "Returned" if self.return_date else ("Overdue" if self.is_overdue() else "Active")
        return f"{self.record_id}: {self.book.title} - {status}"


class FineCalculator(ABC):
    @abstractmethod
    def calculate_fine(self, record: BorrowRecord) -> float:
        pass


class StandardFineCalculator(FineCalculator):
    def __init__(self, rate_per_day: float = 1.0):
        self.rate_per_day = rate_per_day

    def calculate_fine(self, record: BorrowRecord) -> float:
        """Calculate fine: $1 per day overdue"""
        if not record.is_overdue():
            return 0.0

        days = record.days_overdue()
        return days * self.rate_per_day


class Library:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.name = "City Library"
        self.books: Dict[str, Book] = {}  # ISBN -> Book
        self.members: Dict[str, Member] = {}  # Member ID -> Member
        self.borrow_records: Dict[str, BorrowRecord] = {}  # ISBN -> BorrowRecord
        self.fine_calculator = StandardFineCalculator()
        self._initialized = True

    def add_book(self, book: Book):
        """Add book to library"""
        self.books[book.isbn] = book
        print(f"✓ Added book: {book}")

    def add_member(self, member: Member):
        """Add member to library"""
        self.members[member.member_id] = member
        print(f"✓ Registered member: {member}")

    def search_by_title(self, title: str) -> List[Book]:
        """Search books by title"""
        results = []
        for book in self.books.values():
            if title.lower() in book.title.lower():
                results.append(book)
        return results

    def search_by_author(self, author: str) -> List[Book]:
        """Search books by author"""
        results = []
        for book in self.books.values():
            if author.lower() in book.author.lower():
                results.append(book)
        return results

    def borrow_book(self, member_id: str, isbn: str) -> Optional[BorrowRecord]:
        """Borrow a book"""
        # Validate member
        member = self.members.get(member_id)
        if not member:
            print(f"❌ Member {member_id} not found!")
            return None

        # Validate book
        book = self.books.get(isbn)
        if not book:
            print(f"❌ Book {isbn} not found!")
            return None

        # Check if book is available
        if not book.is_available():
            print(f"❌ Book '{book.title}' is not available!")
            return None

        # Check member's borrowing limit
        if not member.can_borrow():
            print(f"❌ {member.name} has reached borrowing limit ({member.max_books} books)!")
            return None

        # Create borrow record
        record = BorrowRecord(member, book, borrow_days=14)

        # Update book status
        book.status = BookStatus.BORROWED

        # Update member's borrowed books
        member.borrowed_books.append(isbn)

        # Store record
        self.borrow_records[isbn] = record

        print(f"✓ {member.name} borrowed {book}")
        print(f"  Due date: {record.due_date.strftime('%Y-%m-%d')}")

        return record

    def return_book(self, isbn: str) -> Optional[float]:
        """Return a book and calculate fine"""
        # Get borrow record
        record = self.borrow_records.get(isbn)
        if not record:
            print(f"❌ No active borrow record for ISBN {isbn}!")
            return None

        # Set return date
        record.return_date = datetime.now()

        # Calculate fine if overdue
        fine = self.fine_calculator.calculate_fine(record)
        record.fine = fine

        # Update book status
        book = record.book
        book.status = BookStatus.AVAILABLE

        # Update member's borrowed books
        member = record.member
        if isbn in member.borrowed_books:
            member.borrowed_books.remove(isbn)

        # Remove from active records
        del self.borrow_records[isbn]

        print(f"✓ {member.name} returned {book}")
        if fine > 0:
            print(f"  ⚠️  Late return! Fine: ${fine:.2f}")
        else:
            print(f"  ✓ Returned on time!")

        return fine

    def display_available_books(self):
        """Display all available books"""
        print("\n" + "="*70)
        print("AVAILABLE BOOKS")
        print("="*70)

        available = [b for b in self.books.values() if b.is_available()]

        if not available:
            print("No books available.")
        else:
            for book in available:
                print(f"  [{book.isbn}] {book.title} by {book.author} ({book.category})")

        print("="*70 + "\n")

    def display_borrowed_books(self):
        """Display all borrowed books"""
        print("\n" + "="*70)
        print("BORROWED BOOKS")
        print("="*70)

        if not self.borrow_records:
            print("No books currently borrowed.")
        else:
            for record in self.borrow_records.values():
                overdue = "⚠️ OVERDUE" if record.is_overdue() else "✓"
                print(f"  {overdue} {record.book.title}")
                print(f"      Borrower: {record.member.name}")
                print(f"      Due: {record.due_date.strftime('%Y-%m-%d')}")
                if record.is_overdue():
                    print(f"      Days overdue: {record.days_overdue()}")

        print("="*70 + "\n")

    def get_member_books(self, member_id: str):
        """Display books borrowed by a member"""
        member = self.members.get(member_id)
        if not member:
            print(f"❌ Member {member_id} not found!")
            return

        print(f"\n{member.name}'s Borrowed Books:")
        if not member.borrowed_books:
            print("  No books borrowed.")
        else:
            for isbn in member.borrowed_books:
                book = self.books.get(isbn)
                record = self.borrow_records.get(isbn)
                if book and record:
                    print(f"  - {book.title} (Due: {record.due_date.strftime('%Y-%m-%d')})")


def run_demo():
    """Run library management demo"""
    print("\n" + "="*70)
    print("LIBRARY MANAGEMENT SYSTEM - DEMO".center(70))
    print("="*70 + "\n")

    library = Library()

    # Add books
    print("--- Adding Books ---\n")
    books = [
        Book("978-0-13-468599-1", "Clean Code", "Robert Martin", "Programming"),
        Book("978-0-13-235088-4", "Clean Architecture", "Robert Martin", "Programming"),
        Book("978-0-596-51774-8", "Head First Design Patterns", "Freeman", "Programming"),
        Book("978-0-13-110362-7", "The Pragmatic Programmer", "Hunt & Thomas", "Programming"),
        Book("978-0-13-597783-0", "Introduction to Algorithms", "Cormen", "Computer Science"),
    ]

    for book in books:
        library.add_book(book)

    print()

    # Add members
    print("--- Registering Members ---\n")
    members = [
        Member("M001", "Alice", MemberType.STUDENT),
        Member("M002", "Bob", MemberType.FACULTY),
        Member("M003", "Charlie", MemberType.PUBLIC),
    ]

    for member in members:
        library.add_member(member)

    print()

    # Display available books
    library.display_available_books()

    # Test borrowing
    print("--- Borrowing Books ---\n")
    library.borrow_book("M001", "978-0-13-468599-1")  # Alice borrows Clean Code
    library.borrow_book("M002", "978-0-13-235088-4")  # Bob borrows Clean Architecture
    library.borrow_book("M003", "978-0-596-51774-8")  # Charlie borrows Design Patterns
    print()

    # Try to borrow already borrowed book
    print("--- Attempting to Borrow Already Borrowed Book ---\n")
    library.borrow_book("M001", "978-0-13-235088-4")
    print()

    # Display borrowed books
    library.display_borrowed_books()

    # Display member's books
    library.get_member_books("M001")
    print()

    # Search functionality
    print("--- Searching Books ---\n")
    print("Search by title 'Clean':")
    results = library.search_by_title("Clean")
    for book in results:
        print(f"  - {book}")

    print("\nSearch by author 'Martin':")
    results = library.search_by_author("Martin")
    for book in results:
        print(f"  - {book}")
    print()

    # Return books
    print("--- Returning Books ---\n")
    library.return_book("978-0-13-468599-1")  # Alice returns Clean Code
    print()

    # Simulate overdue return
    print("--- Simulating Overdue Return ---\n")
    # Manually set borrow date to 20 days ago
    record = library.borrow_records.get("978-0-596-51774-8")
    if record:
        record.borrow_date = datetime.now() - timedelta(days=20)
        record.due_date = datetime.now() - timedelta(days=6)
        print("(Simulated: Book borrowed 20 days ago, due 6 days ago)")

    library.return_book("978-0-596-51774-8")  # Charlie returns late
    print()

    # Test borrowing limit
    print("--- Testing Borrowing Limit ---\n")
    library.borrow_book("M003", "978-0-13-468599-1")  # Charlie borrows 1st book
    library.borrow_book("M003", "978-0-596-51774-8")  # Charlie borrows 2nd book (limit for PUBLIC)
    library.borrow_book("M003", "978-0-13-110362-7")  # Charlie tries 3rd (should fail)
    print()

    # Final state
    library.display_available_books()
    library.display_borrowed_books()

    print("="*70)
    print("DEMO COMPLETE".center(70))
    print("="*70 + "\n")


if __name__ == "__main__":
    run_demo()


"""
INTERVIEW DISCUSSION POINTS:
=============================

1. REQUIREMENTS CLARIFICATION:
   - Member types and their limits?
   - Fine calculation policy?
   - Book reservation system?
   - Multiple copies of same book?
   - Lost book handling?

2. DESIGN CHOICES:
   - Singleton for Library
   - Strategy pattern for fine calculation
   - Separate Book and BorrowRecord
   - ISBN as unique identifier

3. EXTENSIONS:
   - Book reservation queue
   - Multiple copies per title
   - Different loan periods per book type
   - Member notifications (email/SMS)
   - Digital books/e-books
   - Inter-library transfers
   - Recommendation system

4. OPTIMIZATIONS:
   - Index books by title/author for faster search
   - Cache frequently accessed books
   - Batch fine calculation
   - Database persistence

5. EDGE CASES:
   - Book lost by member
   - Member loses card
   - Book damaged during borrowing
   - Multiple members requesting same book
   - Late fee payment tracking

6. COMPLEXITY:
   - Borrow: O(1)
   - Return: O(1)
   - Search: O(n) - can optimize with indexing
   - Fine calculation: O(1)

7. REAL-WORLD:
   - Integration with payment systems
   - Barcode scanning
   - RFID tags
   - Mobile app
   - Analytics dashboard
"""
