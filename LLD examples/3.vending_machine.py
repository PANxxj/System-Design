"""
VENDING MACHINE SYSTEM - Interview Level
=========================================

Problem Statement:
Design a vending machine that dispenses products.

Requirements:
1. Product inventory management
2. Accept coins/notes
3. Select product
4. Dispense product and return change
5. Handle out of stock
6. Different states (Idle, HasMoney, Dispensing)

Design Patterns:
- State Pattern (Machine states)
- Singleton (VendingMachine)
- Strategy (Payment processing)

Time Complexity: O(1) for operations
Space Complexity: O(n) for inventory
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional


class Coin(Enum):
    PENNY = 1
    NICKEL = 5
    DIME = 10
    QUARTER = 25


class Product:
    def __init__(self, name: str, price: int, code: str):
        self.name = name
        self.price = price  # in cents
        self.code = code

    def __str__(self):
        return f"{self.name} (${self.price/100:.2f})"


class Inventory:
    def __init__(self):
        self.products: Dict[str, List[Product]] = {}
        self.quantities: Dict[str, int] = {}

    def add_product(self, product: Product, quantity: int):
        """Add product to inventory"""
        code = product.code
        if code not in self.products:
            self.products[code] = []
            self.quantities[code] = 0

        for _ in range(quantity):
            self.products[code].append(product)
        self.quantities[code] += quantity

    def get_product(self, code: str) -> Optional[Product]:
        """Get a product by code"""
        if code in self.products and self.quantities[code] > 0:
            return self.products[code][0]
        return None

    def is_available(self, code: str) -> bool:
        """Check if product is available"""
        return code in self.quantities and self.quantities[code] > 0

    def dispense_product(self, code: str) -> Optional[Product]:
        """Remove and return product"""
        if self.is_available(code):
            product = self.products[code].pop(0)
            self.quantities[code] -= 1
            return product
        return None

    def get_quantity(self, code: str) -> int:
        """Get quantity of product"""
        return self.quantities.get(code, 0)

    def display_inventory(self):
        """Display all products"""
        print("\n" + "="*50)
        print("PRODUCT INVENTORY")
        print("="*50)
        print(f"{'Code':<8} {'Product':<20} {'Price':<10} {'Qty':<5}")
        print("-"*50)

        for code, products in self.products.items():
            if products:
                product = products[0]
                qty = self.quantities[code]
                status = "✓" if qty > 0 else "✗"
                print(f"{code:<8} {product.name:<20} ${product.price/100:>6.2f}    {qty:>2} {status}")

        print("="*50 + "\n")


class VendingMachineState(ABC):
    """Abstract state class"""

    @abstractmethod
    def insert_money(self, amount: int):
        pass

    @abstractmethod
    def select_product(self, code: str):
        pass

    @abstractmethod
    def dispense_product(self):
        pass

    @abstractmethod
    def return_money(self):
        pass


class IdleState(VendingMachineState):
    def __init__(self, machine):
        self.machine = machine

    def insert_money(self, amount: int):
        self.machine.current_balance += amount
        print(f"✓ Inserted ${amount/100:.2f}. Current balance: ${self.machine.current_balance/100:.2f}")
        self.machine.set_state(self.machine.has_money_state)

    def select_product(self, code: str):
        print("❌ Please insert money first!")

    def dispense_product(self):
        print("❌ No product selected!")

    def return_money(self):
        print("❌ No money to return!")


class HasMoneyState(VendingMachineState):
    def __init__(self, machine):
        self.machine = machine

    def insert_money(self, amount: int):
        self.machine.current_balance += amount
        print(f"✓ Inserted ${amount/100:.2f}. Current balance: ${self.machine.current_balance/100:.2f}")

    def select_product(self, code: str):
        # Check if product exists
        product = self.machine.inventory.get_product(code)

        if not product:
            print(f"❌ Product {code} not available!")
            return

        # Check if enough money
        if self.machine.current_balance < product.price:
            needed = product.price - self.machine.current_balance
            print(f"❌ Insufficient funds! Need ${needed/100:.2f} more.")
            return

        # Select product
        self.machine.selected_product_code = code
        print(f"✓ Selected: {product}")
        self.machine.set_state(self.machine.dispense_state)
        self.machine.state.dispense_product()

    def dispense_product(self):
        print("❌ Please select a product first!")

    def return_money(self):
        returned = self.machine.current_balance
        print(f"✓ Returning ${returned/100:.2f}")
        self.machine.current_balance = 0
        self.machine.set_state(self.machine.idle_state)


class DispenseState(VendingMachineState):
    def __init__(self, machine):
        self.machine = machine

    def insert_money(self, amount: int):
        print("❌ Please wait, dispensing product...")

    def select_product(self, code: str):
        print("❌ Product already selected!")

    def dispense_product(self):
        code = self.machine.selected_product_code
        product = self.machine.inventory.dispense_product(code)

        if product:
            print(f"✓ Dispensing: {product}")

            # Calculate change
            change = self.machine.current_balance - product.price
            if change > 0:
                print(f"✓ Returning change: ${change/100:.2f}")

            # Reset machine
            self.machine.current_balance = 0
            self.machine.selected_product_code = None
            self.machine.set_state(self.machine.idle_state)
            print("✓ Transaction complete!\n")
        else:
            print(f"❌ Failed to dispense product!")
            self.return_money()

    def return_money(self):
        returned = self.machine.current_balance
        print(f"✓ Returning ${returned/100:.2f}")
        self.machine.current_balance = 0
        self.machine.selected_product_code = None
        self.machine.set_state(self.machine.idle_state)


class VendingMachine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.inventory = Inventory()
        self.current_balance = 0
        self.selected_product_code: Optional[str] = None

        # States
        self.idle_state = IdleState(self)
        self.has_money_state = HasMoneyState(self)
        self.dispense_state = DispenseState(self)

        self.state = self.idle_state
        self._initialized = True

    def set_state(self, state: VendingMachineState):
        """Change machine state"""
        self.state = state

    def insert_money(self, amount: int):
        """Insert money"""
        self.state.insert_money(amount)

    def select_product(self, code: str):
        """Select product"""
        self.state.select_product(code)

    def return_money(self):
        """Return money"""
        self.state.return_money()

    def reset(self):
        """Reset machine"""
        self.current_balance = 0
        self.selected_product_code = None
        self.state = self.idle_state


def run_demo():
    """Run vending machine demo"""
    print("\n" + "="*60)
    print("VENDING MACHINE SYSTEM - DEMO".center(60))
    print("="*60 + "\n")

    # Initialize vending machine
    vm = VendingMachine()

    # Stock products
    products = [
        (Product("Coca Cola", 150, "A1"), 5),
        (Product("Pepsi", 150, "A2"), 3),
        (Product("Water", 100, "A3"), 10),
        (Product("Chips", 200, "B1"), 4),
        (Product("Chocolate", 250, "B2"), 6),
        (Product("Candy", 50, "B3"), 8),
    ]

    print("Stocking vending machine...\n")
    for product, qty in products:
        vm.inventory.add_product(product, qty)

    vm.inventory.display_inventory()

    # Test 1: Successful purchase
    print("="*60)
    print("TEST 1: Successful Purchase")
    print("="*60 + "\n")

    print("Buying Coca Cola (A1) for $1.50...")
    vm.insert_money(100)  # $1.00
    vm.insert_money(50)   # $0.50
    vm.select_product("A1")

    # Test 2: Insufficient funds
    print("\n" + "="*60)
    print("TEST 2: Insufficient Funds")
    print("="*60 + "\n")

    print("Trying to buy Chocolate (B2) for $2.50 with only $1.00...")
    vm.insert_money(100)
    vm.select_product("B2")
    print("Returning money...")
    vm.return_money()

    # Test 3: Exact change
    print("\n" + "="*60)
    print("TEST 3: Exact Change")
    print("="*60 + "\n")

    print("Buying Water (A3) for $1.00...")
    vm.insert_money(100)
    vm.select_product("A3")

    # Test 4: Product out of stock
    print("\n" + "="*60)
    print("TEST 4: Multiple Purchases")
    print("="*60 + "\n")

    print("Buying 3 Candy bars...")
    for i in range(3):
        print(f"\nPurchase {i+1}:")
        vm.insert_money(50)
        vm.select_product("B3")

    # Test 5: Return money before selection
    print("\n" + "="*60)
    print("TEST 5: Return Money")
    print("="*60 + "\n")

    print("Inserting $3.00 and returning without buying...")
    vm.insert_money(100)
    vm.insert_money(100)
    vm.insert_money(100)
    vm.return_money()

    # Test 6: Invalid product code
    print("\n" + "="*60)
    print("TEST 6: Invalid Product")
    print("="*60 + "\n")

    print("Trying to buy non-existent product Z9...")
    vm.insert_money(100)
    vm.select_product("Z9")
    vm.return_money()

    # Display final inventory
    print("\n" + "="*60)
    print("FINAL INVENTORY")
    print("="*60)
    vm.inventory.display_inventory()

    print("="*60)
    print("DEMO COMPLETE".center(60))
    print("="*60 + "\n")


if __name__ == "__main__":
    run_demo()


"""
INTERVIEW DISCUSSION POINTS:
=============================

1. REQUIREMENTS CLARIFICATION:
   - What denominations of coins/bills?
   - How to handle change shortage?
   - Refund policy?
   - Admin functions (restock, collect money)?

2. DESIGN CHOICES:
   - State Pattern for machine states
   - Singleton for VendingMachine
   - Separate Inventory management
   - Price in cents (avoid float issues)

3. STATES:
   - Idle: No money inserted
   - HasMoney: Money inserted, waiting for selection
   - Dispense: Dispensing product
   - (Optional) OutOfOrder, Maintenance

4. EXTENSIONS:
   - Multiple payment methods (card, mobile)
   - Discount/promotions
   - User authentication
   - Remote monitoring
   - Temperature control (for drinks)
   - Expiry date tracking

5. EDGE CASES:
   - Product stuck (hardware issue)
   - Exact change not available
   - Power failure during transaction
   - Concurrent access (locks needed)

6. OPTIMIZATIONS:
   - Cache popular products at front
   - Predictive restocking
   - Dynamic pricing

7. COMPLEXITY:
   - Insert money: O(1)
   - Select product: O(1)
   - Dispense: O(1)
   - Display inventory: O(n)
"""
