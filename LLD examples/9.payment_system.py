"""
PAYMENT SYSTEM - Interview Level
=================================

Problem Statement:
Design a payment processing system supporting multiple payment methods.

Requirements:
1. Multiple payment methods (Credit Card, Debit Card, UPI, Wallet)
2. Payment processing and validation
3. Transaction management
4. Refund handling
5. Payment status tracking
6. Retry mechanism for failed payments

Design Patterns:
- Strategy (Payment methods)
- Factory (Payment method creation)
- Observer (Payment notifications)
- State (Payment states)
- Chain of Responsibility (Payment validation)

Time Complexity: O(1) for most operations
Space Complexity: O(n) for transactions
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import random


class PaymentStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


class PaymentMethod(Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    UPI = "UPI"
    WALLET = "WALLET"
    NET_BANKING = "NET_BANKING"


class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    INR = "INR"


# ==================== PAYMENT VALIDATORS ====================

class PaymentValidator(ABC):
    """Base validator using Chain of Responsibility"""

    def __init__(self):
        self.next_validator: Optional[PaymentValidator] = None

    def set_next(self, validator: 'PaymentValidator'):
        """Set next validator in chain"""
        self.next_validator = validator
        return validator

    @abstractmethod
    def validate(self, payment_request) -> tuple[bool, str]:
        """Validate payment request"""
        pass

    def check_next(self, payment_request) -> tuple[bool, str]:
        """Check next validator"""
        if self.next_validator:
            return self.next_validator.validate(payment_request)
        return True, "Validation passed"


class AmountValidator(PaymentValidator):
    """Validates payment amount"""

    def validate(self, payment_request) -> tuple[bool, str]:
        if payment_request.amount <= 0:
            return False, "Invalid amount: must be greater than 0"
        if payment_request.amount > 100000:  # Max transaction limit
            return False, "Amount exceeds maximum transaction limit"
        return self.check_next(payment_request)


class CurrencyValidator(PaymentValidator):
    """Validates currency"""

    def validate(self, payment_request) -> tuple[bool, str]:
        if payment_request.currency not in Currency:
            return False, "Invalid currency"
        return self.check_next(payment_request)


class PaymentMethodValidator(PaymentValidator):
    """Validates payment method details"""

    def validate(self, payment_request) -> tuple[bool, str]:
        if not payment_request.payment_details:
            return False, "Payment details required"
        return self.check_next(payment_request)


# ==================== PAYMENT REQUEST ====================

class PaymentRequest:
    """Payment request object"""

    def __init__(self, amount: float, currency: Currency,
                 payment_method: PaymentMethod, payment_details: Dict):
        self.amount = amount
        self.currency = currency
        self.payment_method = payment_method
        self.payment_details = payment_details
        self.user_id: Optional[str] = None
        self.order_id: Optional[str] = None
        self.description: str = ""


# ==================== PAYMENT STRATEGIES ====================

class PaymentStrategy(ABC):
    """Abstract payment strategy"""

    @abstractmethod
    def process_payment(self, payment_request: PaymentRequest) -> tuple[bool, str]:
        """Process payment and return (success, transaction_id/error)"""
        pass

    @abstractmethod
    def validate_details(self, details: Dict) -> tuple[bool, str]:
        """Validate payment method specific details"""
        pass


class CreditCardPayment(PaymentStrategy):
    """Credit card payment processing"""

    def validate_details(self, details: Dict) -> tuple[bool, str]:
        """Validate credit card details"""
        required = ['card_number', 'cvv', 'expiry', 'name']
        for field in required:
            if field not in details:
                return False, f"Missing field: {field}"

        # Validate card number (simple Luhn algorithm check could be added)
        card_number = details['card_number'].replace(' ', '')
        if not card_number.isdigit() or len(card_number) != 16:
            return False, "Invalid card number"

        # Validate CVV
        if not details['cvv'].isdigit() or len(details['cvv']) != 3:
            return False, "Invalid CVV"

        return True, "Valid"

    def process_payment(self, payment_request: PaymentRequest) -> tuple[bool, str]:
        """Simulate credit card payment"""
        # Validate details
        is_valid, message = self.validate_details(payment_request.payment_details)
        if not is_valid:
            return False, message

        # Simulate payment processing (90% success rate)
        success = random.random() > 0.1

        if success:
            txn_id = f"CC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
            return True, txn_id
        else:
            return False, "Payment declined by bank"


class DebitCardPayment(PaymentStrategy):
    """Debit card payment processing"""

    def validate_details(self, details: Dict) -> tuple[bool, str]:
        required = ['card_number', 'pin', 'expiry']
        for field in required:
            if field not in details:
                return False, f"Missing field: {field}"

        card_number = details['card_number'].replace(' ', '')
        if not card_number.isdigit() or len(card_number) != 16:
            return False, "Invalid card number"

        return True, "Valid"

    def process_payment(self, payment_request: PaymentRequest) -> tuple[bool, str]:
        is_valid, message = self.validate_details(payment_request.payment_details)
        if not is_valid:
            return False, message

        success = random.random() > 0.1

        if success:
            txn_id = f"DC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
            return True, txn_id
        else:
            return False, "Insufficient funds"


class UPIPayment(PaymentStrategy):
    """UPI payment processing"""

    def validate_details(self, details: Dict) -> tuple[bool, str]:
        if 'upi_id' not in details:
            return False, "UPI ID required"

        upi_id = details['upi_id']
        if '@' not in upi_id:
            return False, "Invalid UPI ID format"

        return True, "Valid"

    def process_payment(self, payment_request: PaymentRequest) -> tuple[bool, str]:
        is_valid, message = self.validate_details(payment_request.payment_details)
        if not is_valid:
            return False, message

        success = random.random() > 0.05  # 95% success rate for UPI

        if success:
            txn_id = f"UPI-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
            return True, txn_id
        else:
            return False, "UPI transaction failed"


class WalletPayment(PaymentStrategy):
    """Digital wallet payment processing"""

    def __init__(self):
        # Simulated wallet balances
        self.wallet_balances = {
            'user1@wallet': 5000.0,
            'user2@wallet': 1000.0,
            'user3@wallet': 10000.0,
        }

    def validate_details(self, details: Dict) -> tuple[bool, str]:
        if 'wallet_id' not in details:
            return False, "Wallet ID required"
        return True, "Valid"

    def process_payment(self, payment_request: PaymentRequest) -> tuple[bool, str]:
        is_valid, message = self.validate_details(payment_request.payment_details)
        if not is_valid:
            return False, message

        wallet_id = payment_request.payment_details['wallet_id']
        balance = self.wallet_balances.get(wallet_id, 0)

        if balance < payment_request.amount:
            return False, "Insufficient wallet balance"

        # Deduct from wallet
        self.wallet_balances[wallet_id] -= payment_request.amount

        txn_id = f"WLT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        return True, txn_id


# ==================== PAYMENT FACTORY ====================

class PaymentStrategyFactory:
    """Factory to create payment strategies"""

    @staticmethod
    def create_strategy(payment_method: PaymentMethod) -> PaymentStrategy:
        """Create appropriate payment strategy"""
        strategies = {
            PaymentMethod.CREDIT_CARD: CreditCardPayment(),
            PaymentMethod.DEBIT_CARD: DebitCardPayment(),
            PaymentMethod.UPI: UPIPayment(),
            PaymentMethod.WALLET: WalletPayment(),
        }

        strategy = strategies.get(payment_method)
        if not strategy:
            raise ValueError(f"Unsupported payment method: {payment_method}")

        return strategy


# ==================== TRANSACTION ====================

class Transaction:
    """Represents a payment transaction"""

    transaction_counter = 0

    def __init__(self, payment_request: PaymentRequest):
        Transaction.transaction_counter += 1
        self.transaction_id = f"TXN-{Transaction.transaction_counter:08d}"
        self.amount = payment_request.amount
        self.currency = payment_request.currency
        self.payment_method = payment_request.payment_method
        self.status = PaymentStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.payment_gateway_txn_id: Optional[str] = None
        self.error_message: Optional[str] = None
        self.user_id = payment_request.user_id
        self.order_id = payment_request.order_id
        self.refund_amount: float = 0.0

    def mark_success(self, gateway_txn_id: str):
        """Mark transaction as successful"""
        self.status = PaymentStatus.SUCCESS
        self.payment_gateway_txn_id = gateway_txn_id
        self.updated_at = datetime.now()

    def mark_failed(self, error_message: str):
        """Mark transaction as failed"""
        self.status = PaymentStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.now()

    def mark_refunded(self, amount: float):
        """Mark transaction as refunded"""
        if self.status != PaymentStatus.SUCCESS:
            return False

        self.refund_amount = min(amount, self.amount)
        self.status = PaymentStatus.REFUNDED
        self.updated_at = datetime.now()
        return True

    def __str__(self):
        return (f"Transaction {self.transaction_id}\n"
                f"  Amount: {self.currency.value} {self.amount:.2f}\n"
                f"  Method: {self.payment_method.value}\n"
                f"  Status: {self.status.value}\n"
                f"  Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")


# ==================== PAYMENT OBSERVER ====================

class PaymentObserver(ABC):
    """Observer for payment events"""

    @abstractmethod
    def on_payment_success(self, transaction: Transaction):
        pass

    @abstractmethod
    def on_payment_failed(self, transaction: Transaction):
        pass


class NotificationService(PaymentObserver):
    """Sends notifications on payment events"""

    def on_payment_success(self, transaction: Transaction):
        print(f"📧 Email: Payment of {transaction.currency.value} {transaction.amount:.2f} successful!")
        print(f"   Transaction ID: {transaction.transaction_id}")

    def on_payment_failed(self, transaction: Transaction):
        print(f"📧 Email: Payment failed - {transaction.error_message}")


class AnalyticsService(PaymentObserver):
    """Tracks payment analytics"""

    def __init__(self):
        self.successful_payments = 0
        self.failed_payments = 0
        self.total_amount = 0.0

    def on_payment_success(self, transaction: Transaction):
        self.successful_payments += 1
        self.total_amount += transaction.amount
        print(f"📊 Analytics: Total successful payments: {self.successful_payments}, "
              f"Total amount: ${self.total_amount:.2f}")

    def on_payment_failed(self, transaction: Transaction):
        self.failed_payments += 1


# ==================== PAYMENT PROCESSOR ====================

class PaymentProcessor:
    """Main payment processing system"""

    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self.observers: List[PaymentObserver] = []

        # Setup validation chain
        self.validator_chain = AmountValidator()
        self.validator_chain.set_next(CurrencyValidator()).set_next(PaymentMethodValidator())

    def add_observer(self, observer: PaymentObserver):
        """Add payment observer"""
        self.observers.append(observer)

    def notify_success(self, transaction: Transaction):
        """Notify observers of success"""
        for observer in self.observers:
            observer.on_payment_success(transaction)

    def notify_failure(self, transaction: Transaction):
        """Notify observers of failure"""
        for observer in self.observers:
            observer.on_payment_failed(transaction)

    def process_payment(self, payment_request: PaymentRequest) -> Transaction:
        """Process a payment"""
        # Create transaction
        transaction = Transaction(payment_request)
        self.transactions[transaction.transaction_id] = transaction

        print(f"\n💳 Processing payment: {transaction.transaction_id}")
        print(f"   Amount: {payment_request.currency.value} {payment_request.amount:.2f}")
        print(f"   Method: {payment_request.payment_method.value}")

        # Validate request
        is_valid, message = self.validator_chain.validate(payment_request)
        if not is_valid:
            transaction.mark_failed(f"Validation failed: {message}")
            print(f"   ❌ {message}")
            self.notify_failure(transaction)
            return transaction

        # Get payment strategy
        try:
            strategy = PaymentStrategyFactory.create_strategy(payment_request.payment_method)
        except ValueError as e:
            transaction.mark_failed(str(e))
            print(f"   ❌ {e}")
            self.notify_failure(transaction)
            return transaction

        # Process payment
        transaction.status = PaymentStatus.PROCESSING
        success, result = strategy.process_payment(payment_request)

        if success:
            transaction.mark_success(result)
            print(f"   ✓ Payment successful!")
            print(f"   Gateway Transaction ID: {result}")
            self.notify_success(transaction)
        else:
            transaction.mark_failed(result)
            print(f"   ❌ Payment failed: {result}")
            self.notify_failure(transaction)

        return transaction

    def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        """Refund a transaction"""
        transaction = self.transactions.get(transaction_id)

        if not transaction:
            print(f"❌ Transaction {transaction_id} not found!")
            return False

        if transaction.status != PaymentStatus.SUCCESS:
            print(f"❌ Cannot refund: Transaction status is {transaction.status.value}")
            return False

        refund_amount = amount if amount else transaction.amount

        if refund_amount > transaction.amount:
            print(f"❌ Refund amount exceeds transaction amount!")
            return False

        # Process refund
        if transaction.mark_refunded(refund_amount):
            print(f"\n💰 Refund processed successfully!")
            print(f"   Transaction ID: {transaction_id}")
            print(f"   Refund Amount: {transaction.currency.value} {refund_amount:.2f}")
            return True

        return False

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.transactions.get(transaction_id)

    def get_transaction_status(self, transaction_id: str) -> Optional[PaymentStatus]:
        """Get transaction status"""
        transaction = self.transactions.get(transaction_id)
        return transaction.status if transaction else None


# ==================== DEMO ====================

def run_demo():
    """Run payment system demo"""
    print("\n" + "="*70)
    print("PAYMENT SYSTEM - DEMO".center(70))
    print("="*70 + "\n")

    # Initialize payment processor
    processor = PaymentProcessor()

    # Add observers
    notification_service = NotificationService()
    analytics_service = AnalyticsService()
    processor.add_observer(notification_service)
    processor.add_observer(analytics_service)

    # Test 1: Successful credit card payment
    print("="*70)
    print("TEST 1: Credit Card Payment")
    print("="*70)

    payment1 = PaymentRequest(
        amount=150.00,
        currency=Currency.USD,
        payment_method=PaymentMethod.CREDIT_CARD,
        payment_details={
            'card_number': '4532 1234 5678 9010',
            'cvv': '123',
            'expiry': '12/25',
            'name': 'John Doe'
        }
    )
    payment1.user_id = 'user123'
    payment1.order_id = 'ORD-001'

    txn1 = processor.process_payment(payment1)

    # Test 2: UPI payment
    print("\n" + "="*70)
    print("TEST 2: UPI Payment")
    print("="*70)

    payment2 = PaymentRequest(
        amount=500.00,
        currency=Currency.INR,
        payment_method=PaymentMethod.UPI,
        payment_details={
            'upi_id': 'user@paytm'
        }
    )
    payment2.user_id = 'user456'

    txn2 = processor.process_payment(payment2)

    # Test 3: Wallet payment
    print("\n" + "="*70)
    print("TEST 3: Wallet Payment")
    print("="*70)

    payment3 = PaymentRequest(
        amount=75.50,
        currency=Currency.USD,
        payment_method=PaymentMethod.WALLET,
        payment_details={
            'wallet_id': 'user1@wallet'
        }
    )

    txn3 = processor.process_payment(payment3)

    # Test 4: Invalid payment (insufficient funds)
    print("\n" + "="*70)
    print("TEST 4: Wallet Payment - Insufficient Funds")
    print("="*70)

    payment4 = PaymentRequest(
        amount=10000.00,
        currency=Currency.USD,
        payment_method=PaymentMethod.WALLET,
        payment_details={
            'wallet_id': 'user1@wallet'
        }
    )

    txn4 = processor.process_payment(payment4)

    # Test 5: Validation failure (invalid amount)
    print("\n" + "="*70)
    print("TEST 5: Validation Failure - Invalid Amount")
    print("="*70)

    payment5 = PaymentRequest(
        amount=-50.00,
        currency=Currency.USD,
        payment_method=PaymentMethod.CREDIT_CARD,
        payment_details={'card_number': '1234'}
    )

    txn5 = processor.process_payment(payment5)

    # Test 6: Refund
    print("\n" + "="*70)
    print("TEST 6: Refund Transaction")
    print("="*70)

    if txn1.status == PaymentStatus.SUCCESS:
        processor.refund_payment(txn1.transaction_id, amount=50.00)

    # Display all transactions
    print("\n" + "="*70)
    print("ALL TRANSACTIONS")
    print("="*70 + "\n")

    for txn in processor.transactions.values():
        print(txn)
        print()

    print("="*70)
    print("DEMO COMPLETE".center(70))
    print("="*70 + "\n")


if __name__ == "__main__":
    run_demo()


"""
INTERVIEW DISCUSSION POINTS:
=============================

1. REQUIREMENTS CLARIFICATION:
   - Payment methods supported?
   - Currency conversion needed?
   - Recurring payments?
   - Payment limits per transaction/day?
   - PCI compliance requirements?

2. DESIGN CHOICES:
   - Strategy pattern for payment methods
   - Chain of Responsibility for validation
   - Observer pattern for notifications
   - Factory for creating strategies
   - State pattern for transaction status

3. SECURITY CONSIDERATIONS:
   - PCI DSS compliance (never store CVV)
   - Tokenization of card details
   - Encryption at rest and in transit
   - 3D Secure authentication
   - Fraud detection
   - Rate limiting

4. EXTENSIONS:
   - Recurring/subscription payments
   - Split payments
   - Multi-currency support
   - Payment gateway integration (Stripe, PayPal)
   - Installment plans
   - Buy now, pay later
   - QR code payments
   - Cryptocurrency payments

5. EDGE CASES:
   - Network failure during payment
   - Duplicate transaction prevention (idempotency)
   - Partial refunds
   - Chargeback handling
   - Expired cards
   - Payment timeout

6. OPTIMIZATIONS:
   - Caching exchange rates
   - Batch processing for refunds
   - Async payment processing
   - Payment retry with exponential backoff
   - Load balancing across gateways

7. COMPLEXITY:
   - Process payment: O(1)
   - Validate: O(k) where k=validators
   - Refund: O(1)
   - Get transaction: O(1) with hashmap

8. REAL-WORLD:
   - Integration with payment gateways
   - Webhook handling for async updates
   - Settlement and reconciliation
   - Dispute management
   - Analytics and reporting
   - Compliance and auditing
   - Multi-tenant support
"""
