# E-Commerce System Implementation 🟢

## 🎯 Learning Objectives
- Build a complete e-commerce platform from scratch
- Implement microservices architecture
- Handle high-scale transactions and inventory management
- Design secure payment processing

## 📋 System Overview

A comprehensive e-commerce platform supporting:

1. **User Management**: Registration, authentication, profiles
2. **Product Catalog**: Browse, search, filter products
3. **Shopping Cart**: Add, remove, modify items
4. **Order Processing**: Checkout, payment, fulfillment
5. **Inventory Management**: Stock tracking, reservations
6. **Reviews & Ratings**: Customer feedback system
7. **Recommendations**: Personalized product suggestions

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  Mobile Apps    │    │  Admin Portal   │
│   (React/Vue)   │    │ (iOS/Android)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                ┌─────────────────▼─────────────────┐
                │          API Gateway             │
                │      (Kong/Ambassador)           │
                └─────────────────┬─────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│  User Service  │    │ Product Service  │    │  Order Service   │
│                │    │                  │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│  Cart Service  │    │Inventory Service │    │ Payment Service  │
│                │    │                  │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Review Service │    │Notification Svc  │    │Recommendation Svc│
│                │    │                  │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
```

## 📝 Core Domain Models

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
import uuid
from decimal import Decimal

# Enums
class UserRole(Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    VENDOR = "vendor"

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class ProductStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

# Core Models
@dataclass
class User:
    user_id: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CUSTOMER
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    email_verified: bool = False

@dataclass
class Address:
    address_id: str
    user_id: str
    street_address: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False
    address_type: str = "shipping"  # shipping, billing

@dataclass
class Category:
    category_id: str
    name: str
    description: str
    parent_category_id: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

@dataclass
class Product:
    product_id: str
    name: str
    description: str
    price: Decimal
    category_id: str
    vendor_id: str
    sku: str
    weight: Optional[Decimal] = None
    dimensions: Optional[Dict] = None
    images: List[str] = field(default_factory=list)
    attributes: Dict = field(default_factory=dict)
    status: ProductStatus = ProductStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProductVariant:
    variant_id: str
    product_id: str
    name: str
    sku: str
    price: Decimal
    attributes: Dict  # e.g., {"size": "L", "color": "Red"}
    stock_quantity: int = 0
    is_active: bool = True

@dataclass
class CartItem:
    cart_item_id: str
    user_id: str
    product_id: str
    variant_id: Optional[str]
    quantity: int
    price: Decimal  # Price at time of adding to cart
    added_at: datetime = field(default_factory=datetime.now)

@dataclass
class Order:
    order_id: str
    user_id: str
    status: OrderStatus
    total_amount: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    discount_amount: Decimal = Decimal('0')
    shipping_address: Address
    billing_address: Address
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class OrderItem:
    order_item_id: str
    order_id: str
    product_id: str
    variant_id: Optional[str]
    quantity: int
    unit_price: Decimal
    total_price: Decimal

@dataclass
class Payment:
    payment_id: str
    order_id: str
    user_id: str
    amount: Decimal
    payment_method: str
    payment_status: PaymentStatus
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None

@dataclass
class Review:
    review_id: str
    product_id: str
    user_id: str
    order_id: str
    rating: int  # 1-5
    title: str
    comment: str
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

## 🔧 Service Implementation

### 1. User Service

```python
import bcrypt
import jwt
from typing import Optional
from datetime import datetime, timedelta

class UserService:
    def __init__(self, db_connection, cache_client, email_service):
        self.db = db_connection
        self.cache = cache_client
        self.email_service = email_service
        self.jwt_secret = "your-secret-key"  # Should be from config

    async def register_user(self, email: str, password: str,
                          first_name: str, last_name: str) -> User:
        """Register a new user"""
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Create user
        user = User(
            user_id=str(uuid.uuid4()),
            email=email.lower(),
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )

        # Save to database
        await self._save_user(user)

        # Send verification email
        await self._send_verification_email(user)

        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token"""
        user = await self.get_user_by_email(email)
        if not user or not user.is_active:
            return None

        # Verify password
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return None

        # Generate JWT token
        token_data = {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }

        token = jwt.encode(token_data, self.jwt_secret, algorithm="HS256")

        # Cache user session
        await self.cache.setex(f"user_session:{user.user_id}", 86400, token)

        return token

    async def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            user_id = payload.get("user_id")

            if user_id:
                return await self.get_user_by_id(user_id)
        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass

        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID with caching"""
        # Try cache first
        cached_user = await self.cache.get(f"user:{user_id}")
        if cached_user:
            return User(**cached_user)

        # Query database
        user_data = await self.db.fetch_one(
            "SELECT * FROM users WHERE user_id = :user_id",
            {"user_id": user_id}
        )

        if user_data:
            user = User(**user_data)
            # Cache for 1 hour
            await self.cache.setex(f"user:{user_id}", 3600, user.__dict__)
            return user

        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_data = await self.db.fetch_one(
            "SELECT * FROM users WHERE email = :email",
            {"email": email.lower()}
        )

        if user_data:
            return User(**user_data)
        return None

    async def update_user_profile(self, user_id: str, **kwargs) -> bool:
        """Update user profile"""
        allowed_fields = ['first_name', 'last_name', 'phone']
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not update_data:
            return False

        update_data['updated_at'] = datetime.now()

        # Build update query
        set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
        query = f"UPDATE users SET {set_clause} WHERE user_id = :user_id"
        update_data['user_id'] = user_id

        result = await self.db.execute(query, update_data)

        if result:
            # Clear cache
            await self.cache.delete(f"user:{user_id}")
            return True

        return False

    async def add_address(self, user_id: str, address_data: Dict) -> Address:
        """Add address for user"""
        address = Address(
            address_id=str(uuid.uuid4()),
            user_id=user_id,
            **address_data
        )

        # If this is the first address, make it default
        existing_addresses = await self.get_user_addresses(user_id)
        if not existing_addresses:
            address.is_default = True

        await self._save_address(address)
        return address

    async def get_user_addresses(self, user_id: str) -> List[Address]:
        """Get all addresses for user"""
        addresses_data = await self.db.fetch_all(
            "SELECT * FROM addresses WHERE user_id = :user_id ORDER BY is_default DESC",
            {"user_id": user_id}
        )

        return [Address(**addr) for addr in addresses_data]

    async def _save_user(self, user: User):
        """Save user to database"""
        query = """
        INSERT INTO users (user_id, email, password_hash, first_name, last_name,
                          phone, role, created_at, updated_at, is_active, email_verified)
        VALUES (:user_id, :email, :password_hash, :first_name, :last_name,
                :phone, :role, :created_at, :updated_at, :is_active, :email_verified)
        """

        await self.db.execute(query, {
            "user_id": user.user_id,
            "email": user.email,
            "password_hash": user.password_hash,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "role": user.role.value,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active,
            "email_verified": user.email_verified
        })

    async def _save_address(self, address: Address):
        """Save address to database"""
        query = """
        INSERT INTO addresses (address_id, user_id, street_address, city, state,
                              postal_code, country, is_default, address_type)
        VALUES (:address_id, :user_id, :street_address, :city, :state,
                :postal_code, :country, :is_default, :address_type)
        """

        await self.db.execute(query, address.__dict__)

    async def _send_verification_email(self, user: User):
        """Send email verification"""
        verification_token = jwt.encode(
            {"user_id": user.user_id, "exp": datetime.utcnow() + timedelta(hours=24)},
            self.jwt_secret,
            algorithm="HS256"
        )

        verification_link = f"https://yoursite.com/verify-email?token={verification_token}"

        await self.email_service.send_email(
            to_email=user.email,
            subject="Verify your email address",
            template="email_verification",
            context={
                "first_name": user.first_name,
                "verification_link": verification_link
            }
        )
```

### 2. Product Service

```python
from typing import List, Dict, Optional
import elasticsearch

class ProductService:
    def __init__(self, db_connection, cache_client, es_client):
        self.db = db_connection
        self.cache = cache_client
        self.es = es_client

    async def create_product(self, product_data: Dict, variants_data: List[Dict] = None) -> Product:
        """Create a new product"""
        product = Product(
            product_id=str(uuid.uuid4()),
            **product_data
        )

        # Save product
        await self._save_product(product)

        # Create variants if provided
        if variants_data:
            for variant_data in variants_data:
                variant = ProductVariant(
                    variant_id=str(uuid.uuid4()),
                    product_id=product.product_id,
                    **variant_data
                )
                await self._save_product_variant(variant)

        # Index in Elasticsearch for search
        await self._index_product_for_search(product)

        return product

    async def get_product(self, product_id: str, include_variants: bool = True) -> Optional[Product]:
        """Get product by ID"""
        # Try cache first
        cache_key = f"product:{product_id}"
        cached_product = await self.cache.get(cache_key)

        if cached_product:
            product = Product(**cached_product)
        else:
            # Query database
            product_data = await self.db.fetch_one(
                "SELECT * FROM products WHERE product_id = :product_id",
                {"product_id": product_id}
            )

            if not product_data:
                return None

            product = Product(**product_data)

            # Cache for 1 hour
            await self.cache.setex(cache_key, 3600, product.__dict__)

        # Get variants if requested
        if include_variants:
            variants = await self.get_product_variants(product_id)
            product.variants = variants

        return product

    async def get_product_variants(self, product_id: str) -> List[ProductVariant]:
        """Get all variants for a product"""
        variants_data = await self.db.fetch_all(
            "SELECT * FROM product_variants WHERE product_id = :product_id AND is_active = true",
            {"product_id": product_id}
        )

        return [ProductVariant(**variant) for variant in variants_data]

    async def search_products(self, query: str = None, filters: Dict = None,
                            sort_by: str = "relevance", page: int = 1,
                            page_size: int = 20) -> Dict:
        """Search products with filters"""
        # Build Elasticsearch query
        es_query = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "sort": [],
            "from": (page - 1) * page_size,
            "size": page_size
        }

        # Add text search
        if query:
            es_query["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "description^2", "category_name", "attributes.*"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })

        # Add filters
        if filters:
            if "category_id" in filters:
                es_query["query"]["bool"]["filter"].append({
                    "term": {"category_id": filters["category_id"]}
                })

            if "price_range" in filters:
                price_range = filters["price_range"]
                range_filter = {"range": {"price": {}}}
                if "min" in price_range:
                    range_filter["range"]["price"]["gte"] = price_range["min"]
                if "max" in price_range:
                    range_filter["range"]["price"]["lte"] = price_range["max"]
                es_query["query"]["bool"]["filter"].append(range_filter)

            if "attributes" in filters:
                for attr_name, attr_value in filters["attributes"].items():
                    es_query["query"]["bool"]["filter"].append({
                        "term": {f"attributes.{attr_name}": attr_value}
                    })

        # Add sorting
        if sort_by == "price_low":
            es_query["sort"].append({"price": {"order": "asc"}})
        elif sort_by == "price_high":
            es_query["sort"].append({"price": {"order": "desc"}})
        elif sort_by == "newest":
            es_query["sort"].append({"created_at": {"order": "desc"}})
        elif sort_by == "rating":
            es_query["sort"].append({"average_rating": {"order": "desc"}})

        # Execute search
        try:
            response = await self.es.search(
                index="products",
                body=es_query
            )

            products = []
            for hit in response["hits"]["hits"]:
                products.append(Product(**hit["_source"]))

            return {
                "products": products,
                "total": response["hits"]["total"]["value"],
                "page": page,
                "page_size": page_size,
                "total_pages": (response["hits"]["total"]["value"] + page_size - 1) // page_size
            }

        except Exception as e:
            # Fallback to database search
            return await self._fallback_search(query, filters, page, page_size)

    async def get_products_by_category(self, category_id: str,
                                     page: int = 1, page_size: int = 20) -> Dict:
        """Get products by category"""
        offset = (page - 1) * page_size

        products_data = await self.db.fetch_all(
            """SELECT p.*, c.name as category_name
               FROM products p
               JOIN categories c ON p.category_id = c.category_id
               WHERE p.category_id = :category_id AND p.status = 'active'
               ORDER BY p.created_at DESC
               LIMIT :limit OFFSET :offset""",
            {"category_id": category_id, "limit": page_size, "offset": offset}
        )

        # Get total count
        total_count = await self.db.fetch_val(
            "SELECT COUNT(*) FROM products WHERE category_id = :category_id AND status = 'active'",
            {"category_id": category_id}
        )

        products = [Product(**product) for product in products_data]

        return {
            "products": products,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }

    async def update_product(self, product_id: str, update_data: Dict) -> bool:
        """Update product information"""
        allowed_fields = ['name', 'description', 'price', 'status', 'images', 'attributes']
        update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}

        if not update_fields:
            return False

        update_fields['updated_at'] = datetime.now()

        # Build update query
        set_clause = ", ".join([f"{k} = :{k}" for k in update_fields.keys()])
        query = f"UPDATE products SET {set_clause} WHERE product_id = :product_id"
        update_fields['product_id'] = product_id

        result = await self.db.execute(query, update_fields)

        if result:
            # Clear cache and reindex
            await self.cache.delete(f"product:{product_id}")

            # Update search index
            product = await self.get_product(product_id)
            if product:
                await self._index_product_for_search(product)

            return True

        return False

    async def _save_product(self, product: Product):
        """Save product to database"""
        query = """
        INSERT INTO products (product_id, name, description, price, category_id, vendor_id,
                             sku, weight, dimensions, images, attributes, status, created_at, updated_at)
        VALUES (:product_id, :name, :description, :price, :category_id, :vendor_id,
                :sku, :weight, :dimensions, :images, :attributes, :status, :created_at, :updated_at)
        """

        await self.db.execute(query, {
            **product.__dict__,
            "status": product.status.value,
            "images": json.dumps(product.images),
            "attributes": json.dumps(product.attributes),
            "dimensions": json.dumps(product.dimensions) if product.dimensions else None
        })

    async def _save_product_variant(self, variant: ProductVariant):
        """Save product variant to database"""
        query = """
        INSERT INTO product_variants (variant_id, product_id, name, sku, price,
                                    attributes, stock_quantity, is_active)
        VALUES (:variant_id, :product_id, :name, :sku, :price,
                :attributes, :stock_quantity, :is_active)
        """

        await self.db.execute(query, {
            **variant.__dict__,
            "attributes": json.dumps(variant.attributes)
        })

    async def _index_product_for_search(self, product: Product):
        """Index product in Elasticsearch"""
        # Get category name
        category = await self.db.fetch_one(
            "SELECT name FROM categories WHERE category_id = :category_id",
            {"category_id": product.category_id}
        )

        doc = {
            **product.__dict__,
            "status": product.status.value,
            "category_name": category["name"] if category else "",
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat()
        }

        await self.es.index(
            index="products",
            id=product.product_id,
            body=doc
        )

    async def _fallback_search(self, query: str, filters: Dict,
                             page: int, page_size: int) -> Dict:
        """Fallback search using database when Elasticsearch is unavailable"""
        # Simple database search implementation
        where_conditions = ["p.status = 'active'"]
        params = {}

        if query:
            where_conditions.append("(p.name ILIKE :query OR p.description ILIKE :query)")
            params["query"] = f"%{query}%"

        if filters and "category_id" in filters:
            where_conditions.append("p.category_id = :category_id")
            params["category_id"] = filters["category_id"]

        where_clause = " AND ".join(where_conditions)
        offset = (page - 1) * page_size

        products_data = await self.db.fetch_all(
            f"""SELECT p.* FROM products p
                WHERE {where_clause}
                ORDER BY p.created_at DESC
                LIMIT :limit OFFSET :offset""",
            {**params, "limit": page_size, "offset": offset}
        )

        total_count = await self.db.fetch_val(
            f"SELECT COUNT(*) FROM products p WHERE {where_clause}",
            params
        )

        products = [Product(**product) for product in products_data]

        return {
            "products": products,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }
```

### 3. Cart Service

```python
class CartService:
    def __init__(self, db_connection, cache_client, product_service, inventory_service):
        self.db = db_connection
        self.cache = cache_client
        self.product_service = product_service
        self.inventory_service = inventory_service

    async def add_to_cart(self, user_id: str, product_id: str,
                         variant_id: str = None, quantity: int = 1) -> CartItem:
        """Add item to cart"""
        # Validate product exists and is available
        product = await self.product_service.get_product(product_id)
        if not product or product.status != ProductStatus.ACTIVE:
            raise ValueError("Product not available")

        # Check stock availability
        available_stock = await self.inventory_service.get_available_stock(
            product_id, variant_id
        )

        if available_stock < quantity:
            raise ValueError(f"Only {available_stock} items available")

        # Check if item already exists in cart
        existing_item = await self._get_cart_item(user_id, product_id, variant_id)

        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + quantity
            if available_stock < new_quantity:
                raise ValueError(f"Only {available_stock} items available")

            await self._update_cart_item_quantity(existing_item.cart_item_id, new_quantity)
            existing_item.quantity = new_quantity

            # Update cache
            await self._invalidate_cart_cache(user_id)
            return existing_item
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_item_id=str(uuid.uuid4()),
                user_id=user_id,
                product_id=product_id,
                variant_id=variant_id,
                quantity=quantity,
                price=product.price  # Store current price
            )

            await self._save_cart_item(cart_item)

            # Update cache
            await self._invalidate_cart_cache(user_id)
            return cart_item

    async def update_cart_item(self, user_id: str, cart_item_id: str,
                             quantity: int) -> bool:
        """Update cart item quantity"""
        if quantity <= 0:
            return await self.remove_from_cart(user_id, cart_item_id)

        # Get cart item
        cart_item = await self._get_cart_item_by_id(cart_item_id)
        if not cart_item or cart_item.user_id != user_id:
            return False

        # Check stock availability
        available_stock = await self.inventory_service.get_available_stock(
            cart_item.product_id, cart_item.variant_id
        )

        if available_stock < quantity:
            raise ValueError(f"Only {available_stock} items available")

        # Update quantity
        await self._update_cart_item_quantity(cart_item_id, quantity)

        # Update cache
        await self._invalidate_cart_cache(user_id)
        return True

    async def remove_from_cart(self, user_id: str, cart_item_id: str) -> bool:
        """Remove item from cart"""
        # Verify ownership
        cart_item = await self._get_cart_item_by_id(cart_item_id)
        if not cart_item or cart_item.user_id != user_id:
            return False

        # Remove item
        await self.db.execute(
            "DELETE FROM cart_items WHERE cart_item_id = :cart_item_id",
            {"cart_item_id": cart_item_id}
        )

        # Update cache
        await self._invalidate_cart_cache(user_id)
        return True

    async def get_cart(self, user_id: str) -> List[Dict]:
        """Get user's cart with product details"""
        # Try cache first
        cache_key = f"cart:{user_id}"
        cached_cart = await self.cache.get(cache_key)

        if cached_cart:
            return cached_cart

        # Query database
        cart_items_data = await self.db.fetch_all(
            """SELECT ci.*, p.name, p.images, p.status as product_status,
                      pv.name as variant_name, pv.attributes as variant_attributes
               FROM cart_items ci
               JOIN products p ON ci.product_id = p.product_id
               LEFT JOIN product_variants pv ON ci.variant_id = pv.variant_id
               WHERE ci.user_id = :user_id
               ORDER BY ci.added_at DESC""",
            {"user_id": user_id}
        )

        cart_items = []
        for item_data in cart_items_data:
            # Check current stock availability
            available_stock = await self.inventory_service.get_available_stock(
                item_data["product_id"], item_data["variant_id"]
            )

            cart_item = {
                "cart_item_id": item_data["cart_item_id"],
                "product_id": item_data["product_id"],
                "variant_id": item_data["variant_id"],
                "product_name": item_data["name"],
                "variant_name": item_data["variant_name"],
                "variant_attributes": json.loads(item_data["variant_attributes"]) if item_data["variant_attributes"] else {},
                "quantity": item_data["quantity"],
                "price": item_data["price"],
                "total_price": item_data["price"] * item_data["quantity"],
                "images": json.loads(item_data["images"]),
                "available_stock": available_stock,
                "is_available": item_data["product_status"] == "active" and available_stock > 0,
                "added_at": item_data["added_at"]
            }
            cart_items.append(cart_item)

        # Cache for 5 minutes
        await self.cache.setex(cache_key, 300, cart_items)
        return cart_items

    async def get_cart_summary(self, user_id: str) -> Dict:
        """Get cart summary with totals"""
        cart_items = await self.get_cart(user_id)

        total_items = sum(item["quantity"] for item in cart_items)
        subtotal = sum(item["total_price"] for item in cart_items if item["is_available"])

        # Calculate tax (simplified - would be more complex in real implementation)
        tax_rate = Decimal('0.08')  # 8% tax
        tax_amount = subtotal * tax_rate

        # Calculate shipping (simplified)
        shipping_amount = Decimal('5.99') if subtotal < 50 else Decimal('0')

        total_amount = subtotal + tax_amount + shipping_amount

        return {
            "items": cart_items,
            "total_items": total_items,
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "shipping_amount": shipping_amount,
            "total_amount": total_amount
        }

    async def clear_cart(self, user_id: str) -> bool:
        """Clear all items from cart"""
        await self.db.execute(
            "DELETE FROM cart_items WHERE user_id = :user_id",
            {"user_id": user_id}
        )

        # Update cache
        await self._invalidate_cart_cache(user_id)
        return True

    async def _get_cart_item(self, user_id: str, product_id: str,
                           variant_id: str = None) -> Optional[CartItem]:
        """Get specific cart item"""
        query = """SELECT * FROM cart_items
                   WHERE user_id = :user_id AND product_id = :product_id"""
        params = {"user_id": user_id, "product_id": product_id}

        if variant_id:
            query += " AND variant_id = :variant_id"
            params["variant_id"] = variant_id
        else:
            query += " AND variant_id IS NULL"

        item_data = await self.db.fetch_one(query, params)

        if item_data:
            return CartItem(**item_data)
        return None

    async def _get_cart_item_by_id(self, cart_item_id: str) -> Optional[CartItem]:
        """Get cart item by ID"""
        item_data = await self.db.fetch_one(
            "SELECT * FROM cart_items WHERE cart_item_id = :cart_item_id",
            {"cart_item_id": cart_item_id}
        )

        if item_data:
            return CartItem(**item_data)
        return None

    async def _save_cart_item(self, cart_item: CartItem):
        """Save cart item to database"""
        query = """
        INSERT INTO cart_items (cart_item_id, user_id, product_id, variant_id,
                               quantity, price, added_at)
        VALUES (:cart_item_id, :user_id, :product_id, :variant_id,
                :quantity, :price, :added_at)
        """

        await self.db.execute(query, cart_item.__dict__)

    async def _update_cart_item_quantity(self, cart_item_id: str, quantity: int):
        """Update cart item quantity"""
        await self.db.execute(
            "UPDATE cart_items SET quantity = :quantity WHERE cart_item_id = :cart_item_id",
            {"cart_item_id": cart_item_id, "quantity": quantity}
        )

    async def _invalidate_cart_cache(self, user_id: str):
        """Invalidate cart cache"""
        await self.cache.delete(f"cart:{user_id}")
```

### 4. Order Service

```python
class OrderService:
    def __init__(self, db_connection, cart_service, inventory_service,
                 payment_service, notification_service):
        self.db = db_connection
        self.cart_service = cart_service
        self.inventory_service = inventory_service
        self.payment_service = payment_service
        self.notification_service = notification_service

    async def create_order(self, user_id: str, shipping_address_id: str,
                          billing_address_id: str, payment_method: str) -> Order:
        """Create order from cart"""
        # Get cart summary
        cart_summary = await self.cart_service.get_cart_summary(user_id)

        if not cart_summary["items"]:
            raise ValueError("Cart is empty")

        # Check if all items are available
        unavailable_items = [item for item in cart_summary["items"] if not item["is_available"]]
        if unavailable_items:
            raise ValueError("Some items in cart are no longer available")

        # Get addresses
        shipping_address = await self._get_address(shipping_address_id)
        billing_address = await self._get_address(billing_address_id)

        if not shipping_address or not billing_address:
            raise ValueError("Invalid address provided")

        # Create order
        order = Order(
            order_id=str(uuid.uuid4()),
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=cart_summary["total_amount"],
            tax_amount=cart_summary["tax_amount"],
            shipping_amount=cart_summary["shipping_amount"],
            shipping_address=shipping_address,
            billing_address=billing_address
        )

        # Start transaction
        async with self.db.transaction():
            # Save order
            await self._save_order(order)

            # Create order items and reserve inventory
            for cart_item in cart_summary["items"]:
                if not cart_item["is_available"]:
                    continue

                # Reserve inventory
                reservation_success = await self.inventory_service.reserve_stock(
                    cart_item["product_id"],
                    cart_item["variant_id"],
                    cart_item["quantity"],
                    order.order_id
                )

                if not reservation_success:
                    raise ValueError(f"Failed to reserve stock for {cart_item['product_name']}")

                # Create order item
                order_item = OrderItem(
                    order_item_id=str(uuid.uuid4()),
                    order_id=order.order_id,
                    product_id=cart_item["product_id"],
                    variant_id=cart_item["variant_id"],
                    quantity=cart_item["quantity"],
                    unit_price=cart_item["price"],
                    total_price=cart_item["total_price"]
                )

                await self._save_order_item(order_item)

            # Process payment
            payment_result = await self.payment_service.process_payment(
                user_id=user_id,
                order_id=order.order_id,
                amount=order.total_amount,
                payment_method=payment_method
            )

            if payment_result["success"]:
                # Update order status
                order.status = OrderStatus.CONFIRMED
                await self._update_order_status(order.order_id, OrderStatus.CONFIRMED)

                # Clear cart
                await self.cart_service.clear_cart(user_id)

                # Send confirmation
                await self.notification_service.send_order_confirmation(order)

            else:
                # Release reserved inventory
                await self.inventory_service.release_reservations(order.order_id)
                raise ValueError("Payment failed")

        return order

    async def get_order(self, order_id: str, user_id: str = None) -> Optional[Dict]:
        """Get order with items"""
        # Get order
        order_data = await self.db.fetch_one(
            "SELECT * FROM orders WHERE order_id = :order_id",
            {"order_id": order_id}
        )

        if not order_data:
            return None

        # Check authorization
        if user_id and order_data["user_id"] != user_id:
            return None

        order = Order(**order_data)

        # Get order items
        items_data = await self.db.fetch_all(
            """SELECT oi.*, p.name, p.images,
                      pv.name as variant_name, pv.attributes as variant_attributes
               FROM order_items oi
               JOIN products p ON oi.product_id = p.product_id
               LEFT JOIN product_variants pv ON oi.variant_id = pv.variant_id
               WHERE oi.order_id = :order_id""",
            {"order_id": order_id}
        )

        items = []
        for item_data in items_data:
            item = {
                "order_item_id": item_data["order_item_id"],
                "product_id": item_data["product_id"],
                "variant_id": item_data["variant_id"],
                "product_name": item_data["name"],
                "variant_name": item_data["variant_name"],
                "variant_attributes": json.loads(item_data["variant_attributes"]) if item_data["variant_attributes"] else {},
                "quantity": item_data["quantity"],
                "unit_price": item_data["unit_price"],
                "total_price": item_data["total_price"],
                "images": json.loads(item_data["images"])
            }
            items.append(item)

        return {
            "order": order.__dict__,
            "items": items
        }

    async def get_user_orders(self, user_id: str, page: int = 1,
                            page_size: int = 20) -> Dict:
        """Get user's orders"""
        offset = (page - 1) * page_size

        orders_data = await self.db.fetch_all(
            """SELECT * FROM orders
               WHERE user_id = :user_id
               ORDER BY created_at DESC
               LIMIT :limit OFFSET :offset""",
            {"user_id": user_id, "limit": page_size, "offset": offset}
        )

        total_count = await self.db.fetch_val(
            "SELECT COUNT(*) FROM orders WHERE user_id = :user_id",
            {"user_id": user_id}
        )

        orders = []
        for order_data in orders_data:
            order = Order(**order_data)
            orders.append(order.__dict__)

        return {
            "orders": orders,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }

    async def update_order_status(self, order_id: str, new_status: OrderStatus,
                                tracking_info: Dict = None) -> bool:
        """Update order status"""
        # Validate status transition
        current_order = await self.db.fetch_one(
            "SELECT status FROM orders WHERE order_id = :order_id",
            {"order_id": order_id}
        )

        if not current_order:
            return False

        current_status = OrderStatus(current_order["status"])

        if not self._is_valid_status_transition(current_status, new_status):
            return False

        # Update order
        await self._update_order_status(order_id, new_status)

        # Handle status-specific logic
        if new_status == OrderStatus.SHIPPED:
            # Update tracking info
            if tracking_info:
                await self._update_tracking_info(order_id, tracking_info)

            # Send shipping notification
            order = await self.get_order(order_id)
            await self.notification_service.send_shipping_notification(order, tracking_info)

        elif new_status == OrderStatus.DELIVERED:
            # Send delivery notification
            order = await self.get_order(order_id)
            await self.notification_service.send_delivery_notification(order)

        elif new_status == OrderStatus.CANCELLED:
            # Release inventory reservations
            await self.inventory_service.release_reservations(order_id)

        return True

    async def cancel_order(self, order_id: str, user_id: str,
                         reason: str = None) -> bool:
        """Cancel order"""
        order_data = await self.db.fetch_one(
            "SELECT * FROM orders WHERE order_id = :order_id AND user_id = :user_id",
            {"order_id": order_id, "user_id": user_id}
        )

        if not order_data:
            return False

        current_status = OrderStatus(order_data["status"])

        # Only allow cancellation for certain statuses
        if current_status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            return False

        # Cancel order
        await self._update_order_status(order_id, OrderStatus.CANCELLED)

        # Release inventory
        await self.inventory_service.release_reservations(order_id)

        # Process refund if payment was completed
        if current_status == OrderStatus.CONFIRMED:
            await self.payment_service.process_refund(order_id, order_data["total_amount"])

        # Send cancellation notification
        await self.notification_service.send_cancellation_notification(order_id, reason)

        return True

    def _is_valid_status_transition(self, current: OrderStatus, new: OrderStatus) -> bool:
        """Validate order status transition"""
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [OrderStatus.REFUNDED],
            OrderStatus.CANCELLED: [OrderStatus.REFUNDED],
            OrderStatus.REFUNDED: []
        }

        return new in valid_transitions.get(current, [])

    async def _save_order(self, order: Order):
        """Save order to database"""
        query = """
        INSERT INTO orders (order_id, user_id, status, total_amount, tax_amount,
                           shipping_amount, discount_amount, shipping_address_id,
                           billing_address_id, created_at, updated_at)
        VALUES (:order_id, :user_id, :status, :total_amount, :tax_amount,
                :shipping_amount, :discount_amount, :shipping_address_id,
                :billing_address_id, :created_at, :updated_at)
        """

        await self.db.execute(query, {
            "order_id": order.order_id,
            "user_id": order.user_id,
            "status": order.status.value,
            "total_amount": order.total_amount,
            "tax_amount": order.tax_amount,
            "shipping_amount": order.shipping_amount,
            "discount_amount": order.discount_amount,
            "shipping_address_id": order.shipping_address.address_id,
            "billing_address_id": order.billing_address.address_id,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        })

    async def _save_order_item(self, order_item: OrderItem):
        """Save order item to database"""
        query = """
        INSERT INTO order_items (order_item_id, order_id, product_id, variant_id,
                                quantity, unit_price, total_price)
        VALUES (:order_item_id, :order_id, :product_id, :variant_id,
                :quantity, :unit_price, :total_price)
        """

        await self.db.execute(query, order_item.__dict__)

    async def _update_order_status(self, order_id: str, status: OrderStatus):
        """Update order status"""
        await self.db.execute(
            "UPDATE orders SET status = :status, updated_at = :updated_at WHERE order_id = :order_id",
            {"order_id": order_id, "status": status.value, "updated_at": datetime.now()}
        )

    async def _get_address(self, address_id: str) -> Optional[Address]:
        """Get address by ID"""
        address_data = await self.db.fetch_one(
            "SELECT * FROM addresses WHERE address_id = :address_id",
            {"address_id": address_id}
        )

        if address_data:
            return Address(**address_data)
        return None

    async def _update_tracking_info(self, order_id: str, tracking_info: Dict):
        """Update order tracking information"""
        await self.db.execute(
            "UPDATE orders SET tracking_info = :tracking_info WHERE order_id = :order_id",
            {"order_id": order_id, "tracking_info": json.dumps(tracking_info)}
        )
```

## 🗄️ Database Schema

```sql
-- Users table
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role ENUM('customer', 'admin', 'vendor') DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);

-- Addresses table
CREATE TABLE addresses (
    address_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    street_address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    address_type ENUM('shipping', 'billing') DEFAULT 'shipping',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_addresses (user_id)
);

-- Categories table
CREATE TABLE categories (
    category_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_category_id VARCHAR(36),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id),
    INDEX idx_parent_category (parent_category_id),
    INDEX idx_active (is_active)
);

-- Products table
CREATE TABLE products (
    product_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id VARCHAR(36) NOT NULL,
    vendor_id VARCHAR(36) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    weight DECIMAL(8,3),
    dimensions JSON,
    images JSON,
    attributes JSON,
    status ENUM('active', 'inactive', 'out_of_stock', 'discontinued') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (vendor_id) REFERENCES users(user_id),
    INDEX idx_category (category_id),
    INDEX idx_vendor (vendor_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FULLTEXT idx_search (name, description)
);

-- Product variants table
CREATE TABLE product_variants (
    variant_id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    attributes JSON NOT NULL,
    stock_quantity INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    INDEX idx_product_variants (product_id),
    INDEX idx_sku (sku)
);

-- Cart items table
CREATE TABLE cart_items (
    cart_item_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    variant_id VARCHAR(36),
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE,
    INDEX idx_user_cart (user_id),
    UNIQUE KEY unique_cart_item (user_id, product_id, variant_id)
);

-- Orders table
CREATE TABLE orders (
    order_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded') NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2) NOT NULL,
    shipping_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    shipping_address_id VARCHAR(36) NOT NULL,
    billing_address_id VARCHAR(36) NOT NULL,
    tracking_info JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id),
    FOREIGN KEY (billing_address_id) REFERENCES addresses(address_id),
    INDEX idx_user_orders (user_id, created_at),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- Order items table
CREATE TABLE order_items (
    order_item_id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    variant_id VARCHAR(36),
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id),
    INDEX idx_order_items (order_id)
);

-- Payments table
CREATE TABLE payments (
    payment_id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') NOT NULL,
    transaction_id VARCHAR(255),
    gateway_response JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_order_payment (order_id),
    INDEX idx_user_payments (user_id),
    INDEX idx_status (payment_status)
);

-- Reviews table
CREATE TABLE reviews (
    review_id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    order_id VARCHAR(36) NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    INDEX idx_product_reviews (product_id),
    INDEX idx_user_reviews (user_id),
    UNIQUE KEY unique_review (product_id, user_id, order_id)
);

-- Inventory table
CREATE TABLE inventory (
    inventory_id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL,
    variant_id VARCHAR(36),
    quantity_available INT NOT NULL DEFAULT 0,
    quantity_reserved INT NOT NULL DEFAULT 0,
    reorder_level INT DEFAULT 10,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE,
    UNIQUE KEY unique_inventory (product_id, variant_id),
    INDEX idx_product_inventory (product_id)
);
```

## 🚀 API Implementation

```python
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI(title="E-Commerce API", version="1.0.0")
security = HTTPBearer()

# Request/Response Models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AddToCartRequest(BaseModel):
    product_id: str
    variant_id: Optional[str] = None
    quantity: int = 1

class CreateOrderRequest(BaseModel):
    shipping_address_id: str
    billing_address_id: str
    payment_method: str

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = await user_service.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

# Auth endpoints
@app.post("/api/auth/register")
async def register(user_data: UserRegistration):
    try:
        user = await user_service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        return {"message": "User registered successfully", "user_id": user.user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login(login_data: UserLogin):
    token = await user_service.authenticate_user(login_data.email, login_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    return {"access_token": token, "token_type": "bearer"}

# Product endpoints
@app.get("/api/products/search")
async def search_products(
    q: str = None,
    category_id: str = None,
    min_price: float = None,
    max_price: float = None,
    sort_by: str = "relevance",
    page: int = 1,
    page_size: int = 20
):
    filters = {}
    if category_id:
        filters["category_id"] = category_id
    if min_price is not None or max_price is not None:
        price_range = {}
        if min_price is not None:
            price_range["min"] = min_price
        if max_price is not None:
            price_range["max"] = max_price
        filters["price_range"] = price_range

    results = await product_service.search_products(
        query=q,
        filters=filters,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )
    return results

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/categories/{category_id}/products")
async def get_category_products(category_id: str, page: int = 1, page_size: int = 20):
    results = await product_service.get_products_by_category(
        category_id=category_id,
        page=page,
        page_size=page_size
    )
    return results

# Cart endpoints
@app.post("/api/cart/items")
async def add_to_cart(
    request: AddToCartRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        cart_item = await cart_service.add_to_cart(
            user_id=current_user.user_id,
            product_id=request.product_id,
            variant_id=request.variant_id,
            quantity=request.quantity
        )
        return {"message": "Item added to cart", "cart_item_id": cart_item.cart_item_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/cart")
async def get_cart(current_user: User = Depends(get_current_user)):
    cart_summary = await cart_service.get_cart_summary(current_user.user_id)
    return cart_summary

@app.put("/api/cart/items/{cart_item_id}")
async def update_cart_item(
    cart_item_id: str,
    quantity: int,
    current_user: User = Depends(get_current_user)
):
    try:
        success = await cart_service.update_cart_item(
            user_id=current_user.user_id,
            cart_item_id=cart_item_id,
            quantity=quantity
        )
        if success:
            return {"message": "Cart item updated"}
        else:
            raise HTTPException(status_code=404, detail="Cart item not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/cart/items/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: str,
    current_user: User = Depends(get_current_user)
):
    success = await cart_service.remove_from_cart(
        user_id=current_user.user_id,
        cart_item_id=cart_item_id
    )
    if success:
        return {"message": "Item removed from cart"}
    else:
        raise HTTPException(status_code=404, detail="Cart item not found")

# Order endpoints
@app.post("/api/orders")
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        order = await order_service.create_order(
            user_id=current_user.user_id,
            shipping_address_id=request.shipping_address_id,
            billing_address_id=request.billing_address_id,
            payment_method=request.payment_method
        )
        return {"message": "Order created successfully", "order_id": order.order_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/orders")
async def get_user_orders(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user)
):
    orders = await order_service.get_user_orders(
        user_id=current_user.user_id,
        page=page,
        page_size=page_size
    )
    return orders

@app.get("/api/orders/{order_id}")
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    order = await order_service.get_order(order_id, current_user.user_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/api/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    reason: str = None,
    current_user: User = Depends(get_current_user)
):
    success = await order_service.cancel_order(
        order_id=order_id,
        user_id=current_user.user_id,
        reason=reason
    )
    if success:
        return {"message": "Order cancelled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Unable to cancel order")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## ✅ Implementation Checklist

After building this e-commerce system, you should have:

- [ ] Complete user authentication and authorization
- [ ] Product catalog with search and filtering
- [ ] Shopping cart functionality
- [ ] Order processing workflow
- [ ] Payment integration
- [ ] Inventory management
- [ ] Review and rating system
- [ ] RESTful API with proper error handling
- [ ] Database schema with proper indexing
- [ ] Caching for performance optimization

## 🔄 Next Steps

- Add recommendation engine
- Implement wishlist functionality
- Build admin dashboard
- Add email notifications
- Integrate with shipping providers
- Implement analytics and reporting
- Add mobile app APIs
- Set up monitoring and logging

## 🎯 Advanced Features to Consider

1. **Real-time inventory updates**
2. **Recommendation engine using ML**
3. **Multi-vendor marketplace support**
4. **Advanced search with filters**
5. **Wishlist and favorites**
6. **Coupon and discount system**
7. **Loyalty points program**
8. **Social features (sharing, reviews)**
9. **Multi-language and multi-currency**
10. **Advanced analytics and reporting**