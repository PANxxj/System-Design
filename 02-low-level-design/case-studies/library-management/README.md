# Library Management System Design 🟢

## 🎯 Learning Objectives
- Design a comprehensive library management system
- Apply object-oriented design principles
- Implement reservation and borrowing workflows
- Handle different user types and permissions

## 📋 Problem Statement

Design a library management system that can:

1. **Manage Books**: Add, remove, update book information
2. **Manage Users**: Handle different types of users (members, librarians, admins)
3. **Book Operations**: Search, reserve, borrow, return books
4. **Inventory Management**: Track book availability and locations
5. **Fine Management**: Calculate and manage overdue fines
6. **Reporting**: Generate reports on book usage, overdue books, etc.

## 🏗️ System Requirements

### Functional Requirements
- Users can search for books by title, author, ISBN, or genre
- Members can reserve and borrow available books
- System tracks due dates and calculates fines for overdue books
- Librarians can manage book inventory and member accounts
- System supports different book formats (physical, digital)
- Generate reports on book circulation and member activity

### Non-Functional Requirements
- Handle 10,000+ books and 1,000+ active members
- Support concurrent access by multiple users
- Maintain audit trail of all operations
- Ensure data consistency and integrity

## 🎯 Core Classes Design

### 1. User Management

```python
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

class UserType(Enum):
    MEMBER = "member"
    LIBRARIAN = "librarian"
    ADMIN = "admin"

class AccountStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    BLOCKED = "blocked"

class User(ABC):
    def __init__(self, user_id: str, name: str, email: str, phone: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.created_date = datetime.now()
        self.status = AccountStatus.ACTIVE

    @abstractmethod
    def get_user_type(self) -> UserType:
        pass

    @abstractmethod
    def get_max_books_limit(self) -> int:
        pass

class Address:
    def __init__(self, street: str, city: str, state: str, zip_code: str, country: str):
        self.street = street
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"

class Member(User):
    def __init__(self, user_id: str, name: str, email: str, phone: str, address: Address):
        super().__init__(user_id, name, email, phone)
        self.address = address
        self.membership_date = datetime.now()
        self.total_books_borrowed = 0
        self.total_fines_paid = 0.0

    def get_user_type(self) -> UserType:
        return UserType.MEMBER

    def get_max_books_limit(self) -> int:
        return 5  # Regular members can borrow up to 5 books

class Librarian(User):
    def __init__(self, user_id: str, name: str, email: str, phone: str, employee_id: str):
        super().__init__(user_id, name, email, phone)
        self.employee_id = employee_id

    def get_user_type(self) -> UserType:
        return UserType.LIBRARIAN

    def get_max_books_limit(self) -> int:
        return 10  # Librarians can borrow more books

class Admin(User):
    def __init__(self, user_id: str, name: str, email: str, phone: str):
        super().__init__(user_id, name, email, phone)

    def get_user_type(self) -> UserType:
        return UserType.ADMIN

    def get_max_books_limit(self) -> int:
        return 20  # Admins have highest limit
```

### 2. Book Management

```python
class BookFormat(Enum):
    HARDCOVER = "hardcover"
    PAPERBACK = "paperback"
    EBOOK = "ebook"
    AUDIOBOOK = "audiobook"

class BookStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    LOANED = "loaned"
    LOST = "lost"
    DAMAGED = "damaged"

class Author:
    def __init__(self, name: str, biography: str = ""):
        self.name = name
        self.biography = biography

    def __str__(self):
        return self.name

class Genre:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

class Book:
    def __init__(self, isbn: str, title: str, authors: List[Author],
                 publisher: str, publication_date: datetime,
                 genres: List[Genre], number_of_pages: int):
        self.isbn = isbn
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.publication_date = publication_date
        self.genres = genres
        self.number_of_pages = number_of_pages

    def __str__(self):
        author_names = ", ".join([author.name for author in self.authors])
        return f"{self.title} by {author_names}"

class BookItem:
    def __init__(self, barcode: str, book: Book, book_format: BookFormat,
                 is_reference_only: bool = False, location: str = ""):
        self.barcode = barcode
        self.book = book
        self.format = book_format
        self.is_reference_only = is_reference_only
        self.status = BookStatus.AVAILABLE
        self.date_of_purchase = datetime.now()
        self.location = location
        self.price = 0.0

    def checkout(self, member_id: str) -> bool:
        if self.status == BookStatus.AVAILABLE and not self.is_reference_only:
            self.status = BookStatus.LOANED
            return True
        return False

    def checkin(self) -> bool:
        if self.status == BookStatus.LOANED:
            self.status = BookStatus.AVAILABLE
            return True
        return False

    def reserve(self, member_id: str) -> bool:
        if self.status == BookStatus.AVAILABLE and not self.is_reference_only:
            self.status = BookStatus.RESERVED
            return True
        return False
```

### 3. Lending Management

```python
class ReservationStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class BookReservation:
    def __init__(self, reservation_id: str, member: Member, book_item: BookItem):
        self.reservation_id = reservation_id
        self.member = member
        self.book_item = book_item
        self.creation_date = datetime.now()
        self.status = ReservationStatus.ACTIVE
        # Reservation valid for 3 days
        self.expiry_date = datetime.now() + timedelta(days=3)

    def is_expired(self) -> bool:
        return datetime.now() > self.expiry_date

    def cancel(self):
        self.status = ReservationStatus.CANCELLED
        self.book_item.status = BookStatus.AVAILABLE

class BookLending:
    def __init__(self, lending_id: str, member: Member, book_item: BookItem,
                 librarian: Librarian, lending_period_days: int = 14):
        self.lending_id = lending_id
        self.member = member
        self.book_item = book_item
        self.librarian = librarian
        self.creation_date = datetime.now()
        self.due_date = datetime.now() + timedelta(days=lending_period_days)
        self.return_date: Optional[datetime] = None
        self.is_returned = False

    def return_book(self, librarian: Librarian) -> 'Fine':
        if not self.is_returned:
            self.return_date = datetime.now()
            self.is_returned = True
            self.book_item.checkin()

            # Calculate fine if overdue
            if self.return_date > self.due_date:
                days_overdue = (self.return_date - self.due_date).days
                fine_amount = days_overdue * 1.0  # $1 per day
                return Fine(str(uuid.uuid4()), self.member, fine_amount,
                           f"Overdue book: {self.book_item.book.title}")

        return None

    def is_overdue(self) -> bool:
        return not self.is_returned and datetime.now() > self.due_date

    def get_days_overdue(self) -> int:
        if self.is_overdue():
            return (datetime.now() - self.due_date).days
        return 0

class Fine:
    def __init__(self, fine_id: str, member: Member, amount: float, description: str):
        self.fine_id = fine_id
        self.member = member
        self.amount = amount
        self.description = description
        self.creation_date = datetime.now()
        self.is_paid = False
        self.payment_date: Optional[datetime] = None

    def pay(self) -> bool:
        if not self.is_paid:
            self.is_paid = True
            self.payment_date = datetime.now()
            self.member.total_fines_paid += self.amount
            return True
        return False
```

### 4. Search and Catalog

```python
from typing import Dict, List
import re

class SearchCriteria:
    def __init__(self):
        self.title: Optional[str] = None
        self.author: Optional[str] = None
        self.isbn: Optional[str] = None
        self.genre: Optional[str] = None
        self.publisher: Optional[str] = None
        self.year_from: Optional[int] = None
        self.year_to: Optional[int] = None

class Catalog:
    def __init__(self):
        self.books: Dict[str, Book] = {}  # ISBN -> Book
        self.book_items: Dict[str, BookItem] = {}  # Barcode -> BookItem
        self.authors_index: Dict[str, List[Book]] = {}  # Author name -> Books
        self.genre_index: Dict[str, List[Book]] = {}  # Genre -> Books
        self.title_index: Dict[str, List[Book]] = {}  # Title words -> Books

    def add_book(self, book: Book) -> bool:
        if book.isbn in self.books:
            return False

        self.books[book.isbn] = book
        self._update_indexes(book)
        return True

    def add_book_item(self, book_item: BookItem) -> bool:
        if book_item.barcode in self.book_items:
            return False

        self.book_items[book_item.barcode] = book_item
        return True

    def _update_indexes(self, book: Book):
        # Author index
        for author in book.authors:
            if author.name not in self.authors_index:
                self.authors_index[author.name] = []
            self.authors_index[author.name].append(book)

        # Genre index
        for genre in book.genres:
            if genre.name not in self.genre_index:
                self.genre_index[genre.name] = []
            self.genre_index[genre.name].append(book)

        # Title index (split title into words)
        words = re.findall(r'\w+', book.title.lower())
        for word in words:
            if word not in self.title_index:
                self.title_index[word] = []
            self.title_index[word].append(book)

    def search_books(self, criteria: SearchCriteria) -> List[Book]:
        results = set()

        if criteria.title:
            title_words = re.findall(r'\w+', criteria.title.lower())
            for word in title_words:
                if word in self.title_index:
                    results.update(self.title_index[word])

        if criteria.author:
            author_books = self.authors_index.get(criteria.author, [])
            if results:
                results.intersection_update(author_books)
            else:
                results.update(author_books)

        if criteria.isbn:
            book = self.books.get(criteria.isbn)
            if book:
                if results:
                    results.intersection_update([book])
                else:
                    results.add(book)

        if criteria.genre:
            genre_books = self.genre_index.get(criteria.genre, [])
            if results:
                results.intersection_update(genre_books)
            else:
                results.update(genre_books)

        # If no criteria specified, return empty list
        if not any([criteria.title, criteria.author, criteria.isbn, criteria.genre]):
            return []

        # Filter by year if specified
        if criteria.year_from or criteria.year_to:
            filtered_results = []
            for book in results:
                year = book.publication_date.year
                if criteria.year_from and year < criteria.year_from:
                    continue
                if criteria.year_to and year > criteria.year_to:
                    continue
                filtered_results.append(book)
            return filtered_results

        return list(results)

    def get_available_items(self, isbn: str) -> List[BookItem]:
        available_items = []
        for book_item in self.book_items.values():
            if (book_item.book.isbn == isbn and
                book_item.status == BookStatus.AVAILABLE and
                not book_item.is_reference_only):
                available_items.append(book_item)
        return available_items
```

### 5. Library Management System

```python
class LibrarySystem:
    def __init__(self):
        self.catalog = Catalog()
        self.users: Dict[str, User] = {}
        self.reservations: Dict[str, BookReservation] = {}
        self.lendings: Dict[str, BookLending] = {}
        self.fines: Dict[str, Fine] = {}

    def add_member(self, member: Member) -> bool:
        if member.user_id in self.users:
            return False
        self.users[member.user_id] = member
        return True

    def add_librarian(self, librarian: Librarian) -> bool:
        if librarian.user_id in self.users:
            return False
        self.users[librarian.user_id] = librarian
        return True

    def search_books(self, criteria: SearchCriteria) -> List[Book]:
        return self.catalog.search_books(criteria)

    def reserve_book(self, member_id: str, isbn: str) -> Optional[BookReservation]:
        member = self.users.get(member_id)
        if not member or member.get_user_type() != UserType.MEMBER:
            return None

        if member.status != AccountStatus.ACTIVE:
            return None

        # Check if member has unpaid fines
        if self._has_unpaid_fines(member_id):
            return None

        # Find available book item
        available_items = self.catalog.get_available_items(isbn)
        if not available_items:
            return None

        book_item = available_items[0]

        # Create reservation
        reservation_id = str(uuid.uuid4())
        reservation = BookReservation(reservation_id, member, book_item)

        # Update book status
        book_item.reserve(member_id)

        self.reservations[reservation_id] = reservation
        return reservation

    def checkout_book(self, member_id: str, barcode: str,
                     librarian_id: str, lending_days: int = 14) -> Optional[BookLending]:
        member = self.users.get(member_id)
        librarian = self.users.get(librarian_id)
        book_item = self.catalog.book_items.get(barcode)

        if not all([member, librarian, book_item]):
            return None

        if (member.get_user_type() != UserType.MEMBER or
            librarian.get_user_type() not in [UserType.LIBRARIAN, UserType.ADMIN]):
            return None

        if member.status != AccountStatus.ACTIVE:
            return None

        # Check member's current book limit
        current_books = self._get_current_book_count(member_id)
        if current_books >= member.get_max_books_limit():
            return None

        # Check if member has unpaid fines
        if self._has_unpaid_fines(member_id):
            return None

        # Checkout book
        if book_item.checkout(member_id):
            lending_id = str(uuid.uuid4())
            lending = BookLending(lending_id, member, book_item, librarian, lending_days)
            self.lendings[lending_id] = lending

            # Remove any active reservation for this book
            self._remove_reservation_for_book(barcode)

            member.total_books_borrowed += 1
            return lending

        return None

    def return_book(self, barcode: str, librarian_id: str) -> tuple[bool, Optional[Fine]]:
        librarian = self.users.get(librarian_id)
        book_item = self.catalog.book_items.get(barcode)

        if not librarian or librarian.get_user_type() not in [UserType.LIBRARIAN, UserType.ADMIN]:
            return False, None

        if not book_item or book_item.status != BookStatus.LOANED:
            return False, None

        # Find the lending record
        lending = None
        for l in self.lendings.values():
            if l.book_item.barcode == barcode and not l.is_returned:
                lending = l
                break

        if not lending:
            return False, None

        # Return the book
        fine = lending.return_book(librarian)
        if fine:
            self.fines[fine.fine_id] = fine

        return True, fine

    def pay_fine(self, fine_id: str) -> bool:
        fine = self.fines.get(fine_id)
        if fine and not fine.is_paid:
            return fine.pay()
        return False

    def get_member_lendings(self, member_id: str) -> List[BookLending]:
        return [lending for lending in self.lendings.values()
                if lending.member.user_id == member_id and not lending.is_returned]

    def get_overdue_books(self) -> List[BookLending]:
        return [lending for lending in self.lendings.values()
                if lending.is_overdue()]

    def get_member_fines(self, member_id: str) -> List[Fine]:
        return [fine for fine in self.fines.values()
                if fine.member.user_id == member_id and not fine.is_paid]

    def _has_unpaid_fines(self, member_id: str) -> bool:
        return len(self.get_member_fines(member_id)) > 0

    def _get_current_book_count(self, member_id: str) -> int:
        return len(self.get_member_lendings(member_id))

    def _remove_reservation_for_book(self, barcode: str):
        reservations_to_remove = []
        for reservation_id, reservation in self.reservations.items():
            if (reservation.book_item.barcode == barcode and
                reservation.status == ReservationStatus.ACTIVE):
                reservation.status = ReservationStatus.COMPLETED
                reservations_to_remove.append(reservation_id)

        for reservation_id in reservations_to_remove:
            del self.reservations[reservation_id]

    def cleanup_expired_reservations(self):
        """Remove expired reservations and free up books"""
        expired_reservations = []
        for reservation_id, reservation in self.reservations.items():
            if reservation.is_expired() and reservation.status == ReservationStatus.ACTIVE:
                reservation.status = ReservationStatus.EXPIRED
                reservation.book_item.status = BookStatus.AVAILABLE
                expired_reservations.append(reservation_id)

        for reservation_id in expired_reservations:
            del self.reservations[reservation_id]

        return len(expired_reservations)
```

### 6. Notification System

```python
from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, user: User, message: str, subject: str = ""):
        pass

class EmailNotificationService(NotificationService):
    def send_notification(self, user: User, message: str, subject: str = ""):
        print(f"Sending email to {user.email}")
        print(f"Subject: {subject}")
        print(f"Message: {message}")

class SMSNotificationService(NotificationService):
    def send_notification(self, user: User, message: str, subject: str = ""):
        print(f"Sending SMS to {user.phone}")
        print(f"Message: {message}")

class NotificationManager:
    def __init__(self):
        self.email_service = EmailNotificationService()
        self.sms_service = SMSNotificationService()

    def notify_due_soon(self, lending: BookLending, days_until_due: int):
        message = (f"Your book '{lending.book_item.book.title}' is due in "
                  f"{days_until_due} day(s). Due date: {lending.due_date.strftime('%Y-%m-%d')}")
        subject = "Book Due Soon - Library Reminder"

        self.email_service.send_notification(lending.member, message, subject)

    def notify_overdue(self, lending: BookLending):
        days_overdue = lending.get_days_overdue()
        message = (f"Your book '{lending.book_item.book.title}' is overdue by "
                  f"{days_overdue} day(s). Please return it as soon as possible.")
        subject = "Overdue Book - Immediate Action Required"

        self.email_service.send_notification(lending.member, message, subject)
        self.sms_service.send_notification(lending.member, message)

    def notify_reservation_available(self, reservation: BookReservation):
        message = (f"Your reserved book '{reservation.book_item.book.title}' is now available "
                  f"for pickup. Reservation expires on {reservation.expiry_date.strftime('%Y-%m-%d')}")
        subject = "Reserved Book Available for Pickup"

        self.email_service.send_notification(reservation.member, message, subject)

    def notify_fine_added(self, fine: Fine):
        message = (f"A fine of ${fine.amount:.2f} has been added to your account. "
                  f"Reason: {fine.description}")
        subject = "Library Fine Added"

        self.email_service.send_notification(fine.member, message, subject)
```

### 7. Usage Example

```python
def main():
    # Initialize the library system
    library = LibrarySystem()
    notification_manager = NotificationManager()

    # Create authors and genres
    author1 = Author("J.K. Rowling", "British author")
    author2 = Author("George Orwell", "English novelist")
    genre_fantasy = Genre("Fantasy", "Fantasy fiction")
    genre_dystopian = Genre("Dystopian", "Dystopian fiction")

    # Create books
    harry_potter = Book(
        isbn="978-0439139595",
        title="Harry Potter and the Philosopher's Stone",
        authors=[author1],
        publisher="Bloomsbury",
        publication_date=datetime(1997, 6, 26),
        genres=[genre_fantasy],
        number_of_pages=320
    )

    nineteen_eighty_four = Book(
        isbn="978-0451524935",
        title="1984",
        authors=[author2],
        publisher="Secker & Warburg",
        publication_date=datetime(1949, 6, 8),
        genres=[genre_dystopian],
        number_of_pages=328
    )

    # Add books to catalog
    library.catalog.add_book(harry_potter)
    library.catalog.add_book(nineteen_eighty_four)

    # Create book items
    hp_item1 = BookItem("HP001", harry_potter, BookFormat.HARDCOVER, location="Fiction-A1")
    hp_item2 = BookItem("HP002", harry_potter, BookFormat.PAPERBACK, location="Fiction-A1")
    orwell_item = BookItem("OR001", nineteen_eighty_four, BookFormat.PAPERBACK, location="Fiction-O1")

    library.catalog.add_book_item(hp_item1)
    library.catalog.add_book_item(hp_item2)
    library.catalog.add_book_item(orwell_item)

    # Create users
    address = Address("123 Main St", "Anytown", "NY", "12345", "USA")
    member = Member("M001", "John Doe", "john@example.com", "555-1234", address)
    librarian = Librarian("L001", "Jane Smith", "jane@library.com", "555-5678", "EMP001")

    library.add_member(member)
    library.add_librarian(librarian)

    # Search for books
    criteria = SearchCriteria()
    criteria.title = "Harry Potter"
    search_results = library.search_books(criteria)
    print(f"Found {len(search_results)} books matching 'Harry Potter'")

    # Reserve a book
    reservation = library.reserve_book("M001", "978-0439139595")
    if reservation:
        print(f"Book reserved successfully: {reservation.reservation_id}")
        notification_manager.notify_reservation_available(reservation)

    # Checkout the reserved book
    lending = library.checkout_book("M001", "HP001", "L001", 14)
    if lending:
        print(f"Book checked out successfully: {lending.lending_id}")
        print(f"Due date: {lending.due_date}")

    # Simulate book return (overdue)
    # Force overdue by setting due date in the past
    lending.due_date = datetime.now() - timedelta(days=5)

    returned, fine = library.return_book("HP001", "L001")
    if returned:
        print("Book returned successfully")
        if fine:
            print(f"Fine added: ${fine.amount} - {fine.description}")
            notification_manager.notify_fine_added(fine)

    # Check member's current status
    current_lendings = library.get_member_lendings("M001")
    current_fines = library.get_member_fines("M001")

    print(f"Member {member.name} has {len(current_lendings)} books checked out")
    print(f"Member {member.name} has ${sum(f.amount for f in current_fines):.2f} in unpaid fines")

    # Pay fines
    for fine in current_fines:
        if library.pay_fine(fine.fine_id):
            print(f"Fine {fine.fine_id} paid successfully")

    # Generate reports
    overdue_books = library.get_overdue_books()
    print(f"Total overdue books: {len(overdue_books)}")

    # Cleanup expired reservations
    expired_count = library.cleanup_expired_reservations()
    print(f"Cleaned up {expired_count} expired reservations")

if __name__ == "__main__":
    main()
```

## 🎯 Key Design Patterns Used

1. **Strategy Pattern**: Different notification methods (Email, SMS)
2. **Factory Pattern**: Could be used for creating different types of users
3. **Observer Pattern**: Notification system observes lending events
4. **Command Pattern**: Could be used for audit logging of operations
5. **State Pattern**: Book status transitions

## 🔧 Possible Extensions

1. **Digital Books**: Support for e-books and audiobooks with DRM
2. **Multi-branch Support**: Handle multiple library branches
3. **Book Recommendations**: Suggest books based on reading history
4. **Online Catalog**: Web interface for book search and reservations
5. **Integration with External Systems**: ISBN lookup services
6. **Advanced Reporting**: Analytics on reading patterns and popular books

## ✅ Knowledge Check

After studying this design, you should understand:

- [ ] How to model complex domain entities and relationships
- [ ] Implementation of business rules and constraints
- [ ] User management with different roles and permissions
- [ ] State management for books and reservations
- [ ] Search and indexing strategies
- [ ] Fine calculation and payment processing
- [ ] Notification system design

## 🔄 Next Steps

- Implement additional features like book recommendations
- Add persistence layer with database integration
- Design web APIs for the library system
- Study [Chess Game Design](../chess-game/) for more complex state management
- Explore [Parking Lot Design](../parking-lot/) for space management concepts