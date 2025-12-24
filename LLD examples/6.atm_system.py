"""
ATM SYSTEM - Interview Level
=============================

Problem Statement:
Design an ATM system for basic banking operations.

Requirements:
1. Card validation (PIN check)
2. Balance inquiry
3. Cash withdrawal
4. Cash deposit
5. Transaction history
6. ATM cash management

Design Patterns:
- State Pattern (ATM states)
- Singleton (ATM)
- Strategy (Transaction types)
- Chain of Responsibility (Cash dispensing)

Time Complexity: O(1) for most operations
Space Complexity: O(n) for transactions
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class TransactionType(Enum):
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    BALANCE_INQUIRY = "BALANCE_INQUIRY"


class Card:
    def __init__(self, card_number: str, pin: str, account):
        self.card_number = card_number
        self.pin = pin
        self.account = account
        self.is_blocked = False

    def validate_pin(self, pin: str) -> bool:
        return self.pin == pin and not self.is_blocked


class Account:
    def __init__(self, account_number: str, holder_name: str, balance: float = 0.0):
        self.account_number = account_number
        self.holder_name = holder_name
        self.balance = balance
        self.transactions: List['Transaction'] = []

    def get_balance(self) -> float:
        return self.balance

    def debit(self, amount: float) -> bool:
        """Withdraw money"""
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def credit(self, amount: float):
        """Deposit money"""
        self.balance += amount

    def add_transaction(self, transaction):
        """Add transaction to history"""
        self.transactions.append(transaction)

    def get_recent_transactions(self, count: int = 5) -> List['Transaction']:
        """Get recent transactions"""
        return self.transactions[-count:]


class Transaction:
    transaction_counter = 0

    def __init__(self, transaction_type: TransactionType, amount: float, account: Account):
        Transaction.transaction_counter += 1
        self.transaction_id = f"TXN{Transaction.transaction_counter:08d}"
        self.transaction_type = transaction_type
        self.amount = amount
        self.account = account
        self.timestamp = datetime.now()
        self.status = "SUCCESS"

    def __str__(self):
        return (f"{self.transaction_id} | {self.timestamp.strftime('%Y-%m-%d %H:%M')} | "
                f"{self.transaction_type.value} | ${self.amount:.2f} | {self.status}")


class CashDispenser:
    """Handles cash dispensing with different denominations"""

    def __init__(self):
        # denomination -> count
        self.cash_inventory = {
            100: 10,
            50: 20,
            20: 50,
            10: 100,
            5: 100,
            1: 200
        }

    def has_cash(self, amount: float) -> bool:
        """Check if ATM has enough cash"""
        total = sum(denom * count for denom, count in self.cash_inventory.items())
        return total >= amount

    def dispense_cash(self, amount: int) -> Optional[Dict[int, int]]:
        """Dispense cash using greedy algorithm"""
        if not self.has_cash(amount):
            return None

        result = {}
        remaining = amount

        # Sort denominations in descending order
        for denom in sorted(self.cash_inventory.keys(), reverse=True):
            if remaining == 0:
                break

            count_needed = min(remaining // denom, self.cash_inventory[denom])
            if count_needed > 0:
                result[denom] = count_needed
                remaining -= denom * count_needed

        # If we couldn't dispense exact amount
        if remaining > 0:
            return None

        # Update inventory
        for denom, count in result.items():
            self.cash_inventory[denom] -= count

        return result

    def add_cash(self, denomination: int, count: int):
        """Add cash to ATM"""
        if denomination in self.cash_inventory:
            self.cash_inventory[denomination] += count
        else:
            self.cash_inventory[denomination] = count

    def get_total_cash(self) -> float:
        """Get total cash in ATM"""
        return sum(denom * count for denom, count in self.cash_inventory.items())


class ATMState(ABC):
    """Abstract state"""

    @abstractmethod
    def insert_card(self, card: Card):
        pass

    @abstractmethod
    def enter_pin(self, pin: str):
        pass

    @abstractmethod
    def select_operation(self, operation: str):
        pass

    @abstractmethod
    def eject_card(self):
        pass


class IdleState(ATMState):
    def __init__(self, atm):
        self.atm = atm

    def insert_card(self, card: Card):
        if card.is_blocked:
            print("❌ Card is blocked! Contact your bank.")
            return

        self.atm.current_card = card
        print(f"✓ Card inserted. Please enter PIN.")
        self.atm.set_state(self.atm.has_card_state)

    def enter_pin(self, pin: str):
        print("❌ Please insert card first!")

    def select_operation(self, operation: str):
        print("❌ Please insert card first!")

    def eject_card(self):
        print("❌ No card to eject!")


class HasCardState(ATMState):
    def __init__(self, atm):
        self.atm = atm
        self.attempts = 0
        self.max_attempts = 3

    def insert_card(self, card: Card):
        print("❌ Card already inserted!")

    def enter_pin(self, pin: str):
        if self.atm.current_card.validate_pin(pin):
            print("✓ PIN verified successfully!")
            self.attempts = 0
            self.atm.set_state(self.atm.authenticated_state)
        else:
            self.attempts += 1
            remaining = self.max_attempts - self.attempts

            if remaining > 0:
                print(f"❌ Incorrect PIN! {remaining} attempt(s) remaining.")
            else:
                print("❌ Maximum attempts exceeded! Card blocked.")
                self.atm.current_card.is_blocked = True
                self.eject_card()

    def select_operation(self, operation: str):
        print("❌ Please enter PIN first!")

    def eject_card(self):
        print("✓ Card ejected.")
        self.atm.current_card = None
        self.attempts = 0
        self.atm.set_state(self.atm.idle_state)


class AuthenticatedState(ATMState):
    def __init__(self, atm):
        self.atm = atm

    def insert_card(self, card: Card):
        print("❌ Card already inserted!")

    def enter_pin(self, pin: str):
        print("❌ Already authenticated!")

    def select_operation(self, operation: str):
        """Handle different operations"""
        if operation == "balance":
            self.check_balance()
        elif operation.startswith("withdraw_"):
            amount = float(operation.split("_")[1])
            self.withdraw(amount)
        elif operation.startswith("deposit_"):
            amount = float(operation.split("_")[1])
            self.deposit(amount)
        elif operation == "history":
            self.show_history()
        else:
            print("❌ Invalid operation!")

    def check_balance(self):
        """Check account balance"""
        account = self.atm.current_card.account
        balance = account.get_balance()
        print(f"\n{'='*40}")
        print(f"Account Balance: ${balance:.2f}")
        print(f"{'='*40}\n")

        # Record transaction
        txn = Transaction(TransactionType.BALANCE_INQUIRY, 0, account)
        account.add_transaction(txn)

    def withdraw(self, amount: float):
        """Withdraw cash"""
        account = self.atm.current_card.account

        # Validation
        if amount <= 0:
            print("❌ Invalid amount!")
            return

        if amount % 5 != 0:  # ATM dispenses in multiples of 5
            print("❌ Amount must be multiple of $5!")
            return

        if amount > account.get_balance():
            print("❌ Insufficient funds!")
            return

        if not self.atm.cash_dispenser.has_cash(amount):
            print("❌ ATM has insufficient cash!")
            return

        # Dispense cash
        dispensed = self.atm.cash_dispenser.dispense_cash(int(amount))
        if not dispensed:
            print("❌ Cannot dispense exact amount!")
            return

        # Debit account
        account.debit(amount)

        # Record transaction
        txn = Transaction(TransactionType.WITHDRAWAL, amount, account)
        account.add_transaction(txn)

        print(f"\n{'='*40}")
        print(f"✓ Withdrawal Successful!")
        print(f"Amount: ${amount:.2f}")
        print(f"Dispensed:")
        for denom, count in sorted(dispensed.items(), reverse=True):
            print(f"  ${denom} x {count} = ${denom * count}")
        print(f"Remaining balance: ${account.get_balance():.2f}")
        print(f"{'='*40}\n")

    def deposit(self, amount: float):
        """Deposit cash"""
        account = self.atm.current_card.account

        if amount <= 0:
            print("❌ Invalid amount!")
            return

        # Credit account
        account.credit(amount)

        # Record transaction
        txn = Transaction(TransactionType.DEPOSIT, amount, account)
        account.add_transaction(txn)

        print(f"\n{'='*40}")
        print(f"✓ Deposit Successful!")
        print(f"Amount: ${amount:.2f}")
        print(f"New balance: ${account.get_balance():.2f}")
        print(f"{'='*40}\n")

    def show_history(self):
        """Show transaction history"""
        account = self.atm.current_card.account
        transactions = account.get_recent_transactions(5)

        print(f"\n{'='*70}")
        print("RECENT TRANSACTIONS")
        print(f"{'='*70}")

        if not transactions:
            print("No transactions found.")
        else:
            for txn in transactions:
                print(txn)

        print(f"{'='*70}\n")

    def eject_card(self):
        print("✓ Card ejected. Thank you!")
        self.atm.current_card = None
        self.atm.set_state(self.atm.idle_state)


class ATM:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.atm_id = "ATM001"
        self.location = "Main Street"
        self.cash_dispenser = CashDispenser()
        self.current_card: Optional[Card] = None

        # States
        self.idle_state = IdleState(self)
        self.has_card_state = HasCardState(self)
        self.authenticated_state = AuthenticatedState(self)

        self.state = self.idle_state
        self._initialized = True

    def set_state(self, state: ATMState):
        """Change ATM state"""
        self.state = state

    def insert_card(self, card: Card):
        self.state.insert_card(card)

    def enter_pin(self, pin: str):
        self.state.enter_pin(pin)

    def select_operation(self, operation: str):
        self.state.select_operation(operation)

    def eject_card(self):
        self.state.eject_card()

    def get_cash_level(self) -> float:
        return self.cash_dispenser.get_total_cash()


def run_demo():
    """Run ATM demo"""
    print("\n" + "="*70)
    print("ATM SYSTEM - DEMO".center(70))
    print("="*70 + "\n")

    # Initialize ATM
    atm = ATM()
    print(f"ATM initialized: {atm.atm_id} at {atm.location}")
    print(f"Total cash available: ${atm.get_cash_level():.2f}\n")

    # Create accounts and cards
    account1 = Account("ACC001", "Alice Johnson", 1000.0)
    card1 = Card("1234-5678-9012-3456", "1234", account1)

    account2 = Account("ACC002", "Bob Smith", 500.0)
    card2 = Card("9876-5432-1098-7654", "5678", account2)

    # Test 1: Successful withdrawal
    print("="*70)
    print("TEST 1: Successful Withdrawal")
    print("="*70 + "\n")

    atm.insert_card(card1)
    atm.enter_pin("1234")
    atm.select_operation("balance")
    atm.select_operation("withdraw_100")
    atm.select_operation("balance")
    atm.eject_card()

    # Test 2: Wrong PIN
    print("\n" + "="*70)
    print("TEST 2: Wrong PIN")
    print("="*70 + "\n")

    atm.insert_card(card2)
    atm.enter_pin("0000")  # Wrong PIN
    atm.enter_pin("5678")  # Correct PIN
    atm.select_operation("balance")
    atm.eject_card()

    # Test 3: Deposit
    print("\n" + "="*70)
    print("TEST 3: Deposit")
    print("="*70 + "\n")

    atm.insert_card(card2)
    atm.enter_pin("5678")
    atm.select_operation("deposit_250")
    atm.select_operation("balance")
    atm.eject_card()

    # Test 4: Transaction history
    print("\n" + "="*70)
    print("TEST 4: Transaction History")
    print("="*70 + "\n")

    atm.insert_card(card1)
    atm.enter_pin("1234")
    atm.select_operation("history")
    atm.eject_card()

    # Test 5: Insufficient funds
    print("\n" + "="*70)
    print("TEST 5: Insufficient Funds")
    print("="*70 + "\n")

    atm.insert_card(card2)
    atm.enter_pin("5678")
    atm.select_operation("withdraw_1000")  # More than balance
    atm.eject_card()

    print("\nFinal ATM cash level: ${:.2f}".format(atm.get_cash_level()))

    print("\n" + "="*70)
    print("DEMO COMPLETE".center(70))
    print("="*70 + "\n")


if __name__ == "__main__":
    run_demo()


"""
INTERVIEW DISCUSSION POINTS:
=============================

1. REQUIREMENTS CLARIFICATION:
   - Supported operations?
   - Cash denominations?
   - Daily withdrawal limit?
   - Multiple accounts per card?
   - Receipt printing?

2. DESIGN CHOICES:
   - State Pattern for ATM states
   - Separate cash dispenser logic
   - PIN attempts limiting
   - Transaction recording

3. EXTENSIONS:
   - Multiple currencies
   - Check deposit
   - Bill payment
   - Mini statement
   - Fund transfer
   - Change language
   - Accessibility features

4. SECURITY:
   - Encrypt PIN
   - Card skimming detection
   - Timeout for idle sessions
   - Video surveillance integration
   - Tamper detection

5. EDGE CASES:
   - Power failure during transaction
   - Network failure
   - Cash jam
   - Printer out of paper
   - Card captured
   - Exact change not available

6. OPTIMIZATIONS:
   - Smart cash dispensing algorithm
   - Predictive cash restocking
   - Transaction batching
   - Local caching for offline mode

7. COMPLEXITY:
   - Withdraw: O(k) where k=number of denominations
   - Deposit: O(1)
   - Balance inquiry: O(1)
   - History: O(n) where n=transactions
"""
