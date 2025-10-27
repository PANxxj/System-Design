# WhatsApp Messaging System Design 🔴

## 🎯 Learning Objectives
- Design a real-time messaging system at scale
- Handle billions of messages per day
- Implement message delivery guarantees
- Design for global availability and low latency

## 📋 Problem Statement

Design a messaging system like WhatsApp that can:

1. **Real-time Messaging**: Send and receive messages instantly
2. **Message Types**: Text, media (images, videos, audio), documents
3. **Group Messaging**: Support group chats with up to 256 members
4. **Message Status**: Sent, delivered, read receipts
5. **Online Status**: Show user online/offline status
6. **Message History**: Store and sync message history
7. **End-to-End Encryption**: Secure message transmission
8. **Global Scale**: Support 2+ billion users worldwide

## 📊 Scale Estimation

### Traffic Estimates
- **Daily Active Users (DAU)**: 2 billion
- **Messages per day**: 100 billion
- **Peak messages per second**: 1.5 million
- **Average message size**: 100 bytes
- **Media messages**: 20% of total (larger size)

### Storage Estimates
- **Text messages**: 100B × 100 bytes = 10TB/day
- **Media messages**: 20B × 1MB average = 20PB/day
- **Message retention**: 5 years
- **Total storage needed**: ~35PB (with compression and replicas)

### Bandwidth Estimates
- **Peak traffic**: 1.5M messages/sec × 100 bytes = 150MB/s
- **Media uploads**: 20% × 1MB = 300GB/s peak
- **Total bandwidth**: ~500GB/s peak

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile Apps   │    │   Web Client    │    │  Desktop Apps   │
│  (iOS/Android)  │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                ┌─────────────────▼─────────────────┐
                │           Load Balancer          │
                │        (Global/Regional)         │
                └─────────────────┬─────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Connection Mgr │    │  Message Service │    │  User Service    │
│   (WebSocket)  │    │                  │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Presence Svc   │    │  Delivery Svc    │    │   Media Service  │
│                │    │                  │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
┌───────▼────────┐    ┌─────────▼────────┐    ┌─────────▼────────┐
│ Notification   │    │  Message Store   │    │  Encryption Svc  │
│   Service      │    │    (Cassandra)   │    │                  │
└────────────────┘    └──────────────────┘    └──────────────────┘
```

### Core Components

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from datetime import datetime
import uuid
import asyncio
import websockets
import json

# Enums
class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    LOCATION = "location"

class MessageStatus(Enum):
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class ChatType(Enum):
    INDIVIDUAL = "individual"
    GROUP = "group"

class UserStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"

# Core Models
@dataclass
class User:
    user_id: str
    phone_number: str
    username: Optional[str]
    profile_photo_url: Optional[str]
    status: UserStatus = UserStatus.OFFLINE
    last_seen: Optional[datetime] = None
    public_key: Optional[str] = None  # For encryption
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Chat:
    chat_id: str
    chat_type: ChatType
    participants: List[str]  # List of user_ids
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    # Group chat specific fields
    group_name: Optional[str] = None
    group_description: Optional[str] = None
    group_photo_url: Optional[str] = None
    admins: List[str] = field(default_factory=list)

@dataclass
class Message:
    message_id: str
    chat_id: str
    sender_id: str
    message_type: MessageType
    content: str  # Text or media URL
    timestamp: datetime = field(default_factory=datetime.now)
    reply_to_message_id: Optional[str] = None
    # Encryption
    encrypted_content: Optional[str] = None
    # Media specific
    media_url: Optional[str] = None
    media_size: Optional[int] = None
    media_duration: Optional[int] = None  # For audio/video
    # Location specific
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@dataclass
class MessageStatus:
    message_id: str
    user_id: str
    status: MessageStatus
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Connection:
    connection_id: str
    user_id: str
    websocket: websockets.WebSocketServerProtocol
    last_ping: datetime = field(default_factory=datetime.now)
    device_info: Optional[Dict] = None
```

## 🔧 Core Services Implementation

### 1. Connection Manager Service

```python
import asyncio
import websockets
import json
from typing import Dict, Set
import logging

class ConnectionManager:
    def __init__(self, redis_client, message_service):
        self.connections: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.user_connections: Dict[str, str] = {}  # websocket -> user_id
        self.redis = redis_client
        self.message_service = message_service
        self.logger = logging.getLogger(__name__)

    async def register_connection(self, websocket: websockets.WebSocketServerProtocol, user_id: str):
        """Register a new WebSocket connection"""
        if user_id not in self.connections:
            self.connections[user_id] = set()

        self.connections[user_id].add(websocket)
        self.user_connections[websocket] = user_id

        # Update user status to online
        await self.update_user_status(user_id, UserStatus.ONLINE)

        # Send pending messages
        await self.send_pending_messages(user_id)

        self.logger.info(f"User {user_id} connected. Active connections: {len(self.connections[user_id])}")

    async def unregister_connection(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a WebSocket connection"""
        user_id = self.user_connections.get(websocket)
        if not user_id:
            return

        if user_id in self.connections:
            self.connections[user_id].discard(websocket)

            # If no more connections, mark user as offline
            if not self.connections[user_id]:
                await self.update_user_status(user_id, UserStatus.OFFLINE)
                del self.connections[user_id]

        del self.user_connections[websocket]
        self.logger.info(f"User {user_id} disconnected")

    async def send_message_to_user(self, user_id: str, message: Dict):
        """Send message to a specific user"""
        if user_id not in self.connections:
            # User is offline, store message for later delivery
            await self.store_pending_message(user_id, message)
            return False

        # Send to all user's active connections
        disconnected_sockets = []
        message_json = json.dumps(message)

        for websocket in self.connections[user_id]:
            try:
                await websocket.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_sockets.append(websocket)

        # Clean up disconnected sockets
        for socket in disconnected_sockets:
            await self.unregister_connection(socket)

        return len(self.connections.get(user_id, [])) > 0

    async def send_message_to_chat(self, chat_id: str, message: Dict, exclude_user: str = None):
        """Send message to all participants in a chat"""
        # Get chat participants
        chat_participants = await self.get_chat_participants(chat_id)

        delivery_results = {}
        for participant_id in chat_participants:
            if participant_id == exclude_user:
                continue

            delivered = await self.send_message_to_user(participant_id, message)
            delivery_results[participant_id] = delivered

        return delivery_results

    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, raw_message: str):
        """Handle incoming message from client"""
        try:
            message_data = json.loads(raw_message)
            message_type = message_data.get("type")
            user_id = self.user_connections.get(websocket)

            if not user_id:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Unauthorized"
                }))
                return

            if message_type == "send_message":
                await self.handle_send_message(user_id, message_data)
            elif message_type == "typing":
                await self.handle_typing_indicator(user_id, message_data)
            elif message_type == "message_status":
                await self.handle_message_status_update(user_id, message_data)
            elif message_type == "ping":
                await self.handle_ping(websocket, user_id)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON"
            }))
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")

    async def handle_send_message(self, sender_id: str, message_data: Dict):
        """Handle new message from user"""
        chat_id = message_data.get("chat_id")
        content = message_data.get("content")
        message_type = MessageType(message_data.get("message_type", "text"))

        # Validate chat membership
        if not await self.is_user_in_chat(sender_id, chat_id):
            return

        # Create message
        message = Message(
            message_id=str(uuid.uuid4()),
            chat_id=chat_id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            reply_to_message_id=message_data.get("reply_to_message_id")
        )

        # Store message
        await self.message_service.store_message(message)

        # Prepare message for delivery
        delivery_message = {
            "type": "new_message",
            "message": {
                "message_id": message.message_id,
                "chat_id": message.chat_id,
                "sender_id": message.sender_id,
                "message_type": message.message_type.value,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "reply_to_message_id": message.reply_to_message_id
            }
        }

        # Send to chat participants
        delivery_results = await self.send_message_to_chat(chat_id, delivery_message, exclude_user=sender_id)

        # Update message delivery status
        for participant_id, delivered in delivery_results.items():
            if delivered:
                await self.message_service.update_message_status(
                    message.message_id, participant_id, MessageStatus.DELIVERED
                )

        # Send delivery confirmation to sender
        await self.send_message_to_user(sender_id, {
            "type": "message_sent",
            "message_id": message.message_id,
            "timestamp": message.timestamp.isoformat()
        })

    async def handle_typing_indicator(self, user_id: str, message_data: Dict):
        """Handle typing indicator"""
        chat_id = message_data.get("chat_id")
        is_typing = message_data.get("is_typing", False)

        if not await self.is_user_in_chat(user_id, chat_id):
            return

        typing_message = {
            "type": "typing_indicator",
            "chat_id": chat_id,
            "user_id": user_id,
            "is_typing": is_typing
        }

        await self.send_message_to_chat(chat_id, typing_message, exclude_user=user_id)

    async def handle_message_status_update(self, user_id: str, message_data: Dict):
        """Handle message status updates (read receipts)"""
        message_id = message_data.get("message_id")
        status = MessageStatus(message_data.get("status"))

        await self.message_service.update_message_status(message_id, user_id, status)

        # Notify sender about status update
        message_info = await self.message_service.get_message(message_id)
        if message_info:
            await self.send_message_to_user(message_info.sender_id, {
                "type": "message_status_update",
                "message_id": message_id,
                "user_id": user_id,
                "status": status.value
            })

    async def handle_ping(self, websocket: websockets.WebSocketServerProtocol, user_id: str):
        """Handle ping for connection keepalive"""
        await websocket.send(json.dumps({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }))

        # Update last seen
        await self.update_user_last_seen(user_id)

    async def update_user_status(self, user_id: str, status: UserStatus):
        """Update user online status"""
        await self.redis.setex(f"user_status:{user_id}", 300, status.value)

        # Notify contacts about status change
        contacts = await self.get_user_contacts(user_id)
        status_message = {
            "type": "user_status_update",
            "user_id": user_id,
            "status": status.value,
            "last_seen": datetime.now().isoformat() if status == UserStatus.OFFLINE else None
        }

        for contact_id in contacts:
            await self.send_message_to_user(contact_id, status_message)

    async def update_user_last_seen(self, user_id: str):
        """Update user's last seen timestamp"""
        await self.redis.setex(f"user_last_seen:{user_id}", 3600, datetime.now().isoformat())

    async def store_pending_message(self, user_id: str, message: Dict):
        """Store message for offline user"""
        await self.redis.lpush(f"pending_messages:{user_id}", json.dumps(message))
        await self.redis.expire(f"pending_messages:{user_id}", 86400 * 7)  # 7 days

    async def send_pending_messages(self, user_id: str):
        """Send pending messages to newly connected user"""
        pending_key = f"pending_messages:{user_id}"
        while True:
            message_json = await self.redis.rpop(pending_key)
            if not message_json:
                break

            try:
                message = json.loads(message_json)
                await self.send_message_to_user(user_id, message)
            except Exception as e:
                self.logger.error(f"Error sending pending message: {e}")

    # Helper methods (simplified implementations)
    async def get_chat_participants(self, chat_id: str) -> List[str]:
        """Get list of chat participants"""
        # Implementation would query database
        return []

    async def is_user_in_chat(self, user_id: str, chat_id: str) -> bool:
        """Check if user is member of chat"""
        # Implementation would check database
        return True

    async def get_user_contacts(self, user_id: str) -> List[str]:
        """Get user's contact list"""
        # Implementation would query database
        return []

# WebSocket Server
class WhatsAppWebSocketServer:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    async def handle_client(self, websocket, path):
        """Handle new WebSocket connection"""
        try:
            # Authenticate user (simplified)
            auth_message = await websocket.recv()
            auth_data = json.loads(auth_message)

            user_id = auth_data.get("user_id")  # In real app, validate JWT token
            if not user_id:
                await websocket.send(json.dumps({"type": "auth_error"}))
                return

            # Register connection
            await self.connection_manager.register_connection(websocket, user_id)

            # Send auth success
            await websocket.send(json.dumps({
                "type": "auth_success",
                "user_id": user_id
            }))

            # Handle messages
            async for message in websocket:
                await self.connection_manager.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logging.error(f"WebSocket error: {e}")
        finally:
            await self.connection_manager.unregister_connection(websocket)

    def start_server(self, host="localhost", port=8765):
        """Start WebSocket server"""
        return websockets.serve(self.handle_client, host, port)
```

### 2. Message Service

```python
import cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from typing import List, Optional

class MessageService:
    def __init__(self, cassandra_hosts, redis_client, encryption_service):
        self.cluster = Cluster(cassandra_hosts)
        self.session = self.cluster.connect()
        self.redis = redis_client
        self.encryption_service = encryption_service

        # Create keyspace and tables
        self.setup_database()

    def setup_database(self):
        """Setup Cassandra keyspace and tables"""
        self.session.execute("""
            CREATE KEYSPACE IF NOT EXISTS whatsapp
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3}
        """)

        self.session.set_keyspace('whatsapp')

        # Messages table partitioned by chat_id for efficient queries
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                chat_id text,
                message_id text,
                sender_id text,
                message_type text,
                content text,
                encrypted_content text,
                timestamp timestamp,
                reply_to_message_id text,
                media_url text,
                media_size bigint,
                media_duration int,
                latitude double,
                longitude double,
                PRIMARY KEY (chat_id, timestamp, message_id)
            ) WITH CLUSTERING ORDER BY (timestamp DESC)
        """)

        # Message status table for delivery tracking
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS message_status (
                message_id text,
                user_id text,
                status text,
                timestamp timestamp,
                PRIMARY KEY (message_id, user_id)
            )
        """)

        # User chats table for quick chat lookups
        self.session.execute("""
            CREATE TABLE IF NOT EXISTS user_chats (
                user_id text,
                chat_id text,
                chat_type text,
                last_message_time timestamp,
                unread_count counter,
                PRIMARY KEY (user_id, last_message_time, chat_id)
            ) WITH CLUSTERING ORDER BY (last_message_time DESC)
        """)

    async def store_message(self, message: Message) -> bool:
        """Store message in Cassandra"""
        try:
            # Encrypt content if it's sensitive
            encrypted_content = None
            if message.message_type == MessageType.TEXT:
                encrypted_content = await self.encryption_service.encrypt_message(
                    message.content, message.chat_id
                )

            # Insert message
            self.session.execute("""
                INSERT INTO messages (
                    chat_id, message_id, sender_id, message_type, content,
                    encrypted_content, timestamp, reply_to_message_id,
                    media_url, media_size, media_duration, latitude, longitude
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message.chat_id, message.message_id, message.sender_id,
                message.message_type.value, message.content, encrypted_content,
                message.timestamp, message.reply_to_message_id,
                message.media_url, message.media_size, message.media_duration,
                message.latitude, message.longitude
            ))

            # Update chat last message time
            await self.update_chat_last_message(message.chat_id, message.timestamp)

            # Cache recent message for quick access
            await self.cache_recent_message(message)

            return True

        except Exception as e:
            logging.error(f"Error storing message: {e}")
            return False

    async def get_messages(self, chat_id: str, limit: int = 50,
                          before_timestamp: datetime = None) -> List[Message]:
        """Get messages for a chat with pagination"""
        # Try cache first for recent messages
        if not before_timestamp:
            cached_messages = await self.get_cached_messages(chat_id, limit)
            if cached_messages:
                return cached_messages

        # Query Cassandra
        query = """
            SELECT * FROM messages
            WHERE chat_id = ?
        """
        params = [chat_id]

        if before_timestamp:
            query += " AND timestamp < ?"
            params.append(before_timestamp)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = self.session.execute(query, params)

        messages = []
        for row in rows:
            # Decrypt content if needed
            content = row.content
            if row.encrypted_content:
                try:
                    content = await self.encryption_service.decrypt_message(
                        row.encrypted_content, chat_id
                    )
                except Exception as e:
                    logging.error(f"Error decrypting message: {e}")

            message = Message(
                message_id=row.message_id,
                chat_id=row.chat_id,
                sender_id=row.sender_id,
                message_type=MessageType(row.message_type),
                content=content,
                timestamp=row.timestamp,
                reply_to_message_id=row.reply_to_message_id,
                media_url=row.media_url,
                media_size=row.media_size,
                media_duration=row.media_duration,
                latitude=row.latitude,
                longitude=row.longitude
            )
            messages.append(message)

        return messages

    async def get_message(self, message_id: str) -> Optional[Message]:
        """Get specific message by ID"""
        # Check cache first
        cached_message = await self.redis.get(f"message:{message_id}")
        if cached_message:
            return Message(**json.loads(cached_message))

        # Query database (this requires secondary index in production)
        rows = self.session.execute("""
            SELECT * FROM messages WHERE message_id = ? ALLOW FILTERING
        """, [message_id])

        row = rows.one()
        if row:
            message = Message(
                message_id=row.message_id,
                chat_id=row.chat_id,
                sender_id=row.sender_id,
                message_type=MessageType(row.message_type),
                content=row.content,
                timestamp=row.timestamp,
                reply_to_message_id=row.reply_to_message_id,
                media_url=row.media_url,
                media_size=row.media_size,
                media_duration=row.media_duration,
                latitude=row.latitude,
                longitude=row.longitude
            )

            # Cache for future access
            await self.redis.setex(
                f"message:{message_id}",
                3600,
                json.dumps(message.__dict__, default=str)
            )

            return message

        return None

    async def update_message_status(self, message_id: str, user_id: str, status: MessageStatus):
        """Update message delivery/read status"""
        self.session.execute("""
            INSERT INTO message_status (message_id, user_id, status, timestamp)
            VALUES (?, ?, ?, ?)
        """, [message_id, user_id, status.value, datetime.now()])

        # Cache status for quick lookup
        await self.redis.setex(
            f"msg_status:{message_id}:{user_id}",
            86400,
            status.value
        )

    async def get_message_status(self, message_id: str) -> Dict[str, MessageStatus]:
        """Get message status for all recipients"""
        rows = self.session.execute("""
            SELECT user_id, status FROM message_status WHERE message_id = ?
        """, [message_id])

        statuses = {}
        for row in rows:
            statuses[row.user_id] = MessageStatus(row.status)

        return statuses

    async def search_messages(self, chat_id: str, query: str, limit: int = 20) -> List[Message]:
        """Search messages in a chat (simplified implementation)"""
        # In production, this would use Elasticsearch or similar
        # For now, basic text search in Cassandra
        rows = self.session.execute("""
            SELECT * FROM messages
            WHERE chat_id = ? AND content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
            ALLOW FILTERING
        """, [chat_id, f"%{query}%", limit])

        messages = []
        for row in rows:
            message = Message(
                message_id=row.message_id,
                chat_id=row.chat_id,
                sender_id=row.sender_id,
                message_type=MessageType(row.message_type),
                content=row.content,
                timestamp=row.timestamp,
                reply_to_message_id=row.reply_to_message_id
            )
            messages.append(message)

        return messages

    async def cache_recent_message(self, message: Message):
        """Cache recent message for quick access"""
        # Add to recent messages list for the chat
        message_data = json.dumps(message.__dict__, default=str)
        await self.redis.lpush(f"recent_messages:{message.chat_id}", message_data)
        await self.redis.ltrim(f"recent_messages:{message.chat_id}", 0, 99)  # Keep last 100
        await self.redis.expire(f"recent_messages:{message.chat_id}", 3600)

    async def get_cached_messages(self, chat_id: str, limit: int) -> List[Message]:
        """Get cached recent messages"""
        cached_data = await self.redis.lrange(f"recent_messages:{chat_id}", 0, limit - 1)

        messages = []
        for data in cached_data:
            try:
                message_dict = json.loads(data)
                # Convert string timestamp back to datetime
                message_dict['timestamp'] = datetime.fromisoformat(message_dict['timestamp'])
                message_dict['message_type'] = MessageType(message_dict['message_type'])
                messages.append(Message(**message_dict))
            except Exception as e:
                logging.error(f"Error deserializing cached message: {e}")

        return messages

    async def update_chat_last_message(self, chat_id: str, timestamp: datetime):
        """Update chat's last message timestamp"""
        # Get chat participants and update their chat lists
        participants = await self.get_chat_participants(chat_id)

        for user_id in participants:
            self.session.execute("""
                UPDATE user_chats SET last_message_time = ?
                WHERE user_id = ? AND chat_id = ?
            """, [timestamp, user_id, chat_id])

    async def get_chat_participants(self, chat_id: str) -> List[str]:
        """Get chat participants"""
        # This would query the chats table
        # Simplified implementation
        return []

    async def mark_messages_as_read(self, chat_id: str, user_id: str, up_to_timestamp: datetime):
        """Mark messages as read up to a certain timestamp"""
        # Get unread messages
        rows = self.session.execute("""
            SELECT message_id FROM messages
            WHERE chat_id = ? AND timestamp <= ?
            ORDER BY timestamp DESC
        """, [chat_id, up_to_timestamp])

        # Update status for each message
        for row in rows:
            await self.update_message_status(row.message_id, user_id, MessageStatus.READ)

        # Reset unread counter
        self.session.execute("""
            UPDATE user_chats SET unread_count = 0
            WHERE user_id = ? AND chat_id = ?
        """, [user_id, chat_id])
```

### 3. Media Service

```python
import boto3
import aiofiles
import ffmpeg
from PIL import Image
import tempfile
import os

class MediaService:
    def __init__(self, s3_bucket, cdn_domain):
        self.s3_client = boto3.client('s3')
        self.s3_bucket = s3_bucket
        self.cdn_domain = cdn_domain

    async def upload_image(self, file_data: bytes, user_id: str, chat_id: str) -> Dict:
        """Upload and process image"""
        file_id = str(uuid.uuid4())

        # Create different sizes
        sizes = await self.create_image_thumbnails(file_data)

        upload_results = {}
        for size_name, image_data in sizes.items():
            key = f"images/{chat_id}/{file_id}_{size_name}.jpg"

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=image_data,
                ContentType='image/jpeg',
                CacheControl='max-age=31536000'  # 1 year
            )

            upload_results[size_name] = f"https://{self.cdn_domain}/{key}"

        return {
            "file_id": file_id,
            "urls": upload_results,
            "file_size": len(file_data)
        }

    async def upload_video(self, file_data: bytes, user_id: str, chat_id: str) -> Dict:
        """Upload and process video"""
        file_id = str(uuid.uuid4())

        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name

        try:
            # Get video info
            probe = ffmpeg.probe(temp_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            duration = float(probe['format']['duration'])

            # Create thumbnail
            thumbnail_path = temp_path.replace('.mp4', '_thumb.jpg')
            (
                ffmpeg
                .input(temp_path, ss=duration/2)  # Middle frame
                .output(thumbnail_path, vframes=1, format='image2', vcodec='mjpeg')
                .overwrite_output()
                .run(quiet=True)
            )

            # Upload original video
            video_key = f"videos/{chat_id}/{file_id}.mp4"
            with open(temp_path, 'rb') as f:
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=video_key,
                    Body=f.read(),
                    ContentType='video/mp4'
                )

            # Upload thumbnail
            thumbnail_key = f"videos/{chat_id}/{file_id}_thumb.jpg"
            with open(thumbnail_path, 'rb') as f:
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=thumbnail_key,
                    Body=f.read(),
                    ContentType='image/jpeg'
                )

            return {
                "file_id": file_id,
                "video_url": f"https://{self.cdn_domain}/{video_key}",
                "thumbnail_url": f"https://{self.cdn_domain}/{thumbnail_key}",
                "duration": int(duration),
                "file_size": len(file_data),
                "width": int(video_info['width']),
                "height": int(video_info['height'])
            }

        finally:
            # Cleanup temp files
            os.unlink(temp_path)
            if os.path.exists(thumbnail_path):
                os.unlink(thumbnail_path)

    async def upload_audio(self, file_data: bytes, user_id: str, chat_id: str) -> Dict:
        """Upload and process audio"""
        file_id = str(uuid.uuid4())

        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name

        try:
            # Get audio info
            probe = ffmpeg.probe(temp_path)
            audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
            duration = float(probe['format']['duration'])

            # Convert to compressed format if needed
            compressed_path = temp_path.replace('.m4a', '_compressed.m4a')
            (
                ffmpeg
                .input(temp_path)
                .output(compressed_path, acodec='aac', audio_bitrate='64k')
                .overwrite_output()
                .run(quiet=True)
            )

            # Upload compressed audio
            audio_key = f"audio/{chat_id}/{file_id}.m4a"
            with open(compressed_path, 'rb') as f:
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=audio_key,
                    Body=f.read(),
                    ContentType='audio/mp4'
                )

            return {
                "file_id": file_id,
                "audio_url": f"https://{self.cdn_domain}/{audio_key}",
                "duration": int(duration),
                "file_size": os.path.getsize(compressed_path)
            }

        finally:
            # Cleanup temp files
            os.unlink(temp_path)
            if os.path.exists(compressed_path):
                os.unlink(compressed_path)

    async def create_image_thumbnails(self, image_data: bytes) -> Dict[str, bytes]:
        """Create different sized thumbnails"""
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(image_data)
            temp_file.seek(0)

            with Image.open(temp_file) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                sizes = {
                    'thumbnail': (150, 150),
                    'medium': (800, 600),
                    'original': img.size
                }

                results = {}
                for size_name, (width, height) in sizes.items():
                    if size_name == 'original':
                        resized_img = img
                    else:
                        resized_img = img.copy()
                        resized_img.thumbnail((width, height), Image.Resampling.LANCZOS)

                    # Save to bytes
                    with tempfile.BytesIO() as output:
                        resized_img.save(output, format='JPEG', quality=85, optimize=True)
                        results[size_name] = output.getvalue()

                return results
```

## 🗄️ Database Design

### Cassandra Schema

```cql
-- Messages table (partitioned by chat_id for efficiency)
CREATE TABLE messages (
    chat_id text,
    message_id text,
    sender_id text,
    message_type text,
    content text,
    encrypted_content text,
    timestamp timestamp,
    reply_to_message_id text,
    media_url text,
    media_size bigint,
    media_duration int,
    latitude double,
    longitude double,
    PRIMARY KEY (chat_id, timestamp, message_id)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND gc_grace_seconds = 86400
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': 1, 'compaction_window_unit': 'DAYS'};

-- Message status for delivery tracking
CREATE TABLE message_status (
    message_id text,
    user_id text,
    status text,
    timestamp timestamp,
    PRIMARY KEY (message_id, user_id)
) WITH gc_grace_seconds = 86400;

-- User chats for quick chat list retrieval
CREATE TABLE user_chats (
    user_id text,
    chat_id text,
    chat_type text,
    last_message_time timestamp,
    unread_count counter,
    is_muted boolean,
    PRIMARY KEY (user_id, last_message_time, chat_id)
) WITH CLUSTERING ORDER BY (last_message_time DESC);

-- Chat metadata
CREATE TABLE chats (
    chat_id text PRIMARY KEY,
    chat_type text,
    created_by text,
    created_at timestamp,
    updated_at timestamp,
    group_name text,
    group_description text,
    group_photo_url text
);

-- Chat participants
CREATE TABLE chat_participants (
    chat_id text,
    user_id text,
    joined_at timestamp,
    role text, -- member, admin
    PRIMARY KEY (chat_id, user_id)
);

-- Users table
CREATE TABLE users (
    user_id text PRIMARY KEY,
    phone_number text,
    username text,
    profile_photo_url text,
    public_key text,
    created_at timestamp,
    last_seen timestamp
);

-- Create secondary indexes
CREATE INDEX ON users (phone_number);
CREATE INDEX ON chat_participants (user_id);
```

## 🔒 End-to-End Encryption

```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

class EncryptionService:
    def __init__(self):
        self.chat_keys = {}  # In production, store in secure key management system

    async def generate_chat_key(self, chat_id: str) -> str:
        """Generate symmetric key for chat"""
        if chat_id in self.chat_keys:
            return self.chat_keys[chat_id]

        # Generate 256-bit key
        key = os.urandom(32)
        self.chat_keys[chat_id] = key

        # In production, store encrypted key in database
        await self.store_chat_key(chat_id, key)

        return key

    async def encrypt_message(self, content: str, chat_id: str) -> str:
        """Encrypt message content"""
        chat_key = await self.generate_chat_key(chat_id)

        # Generate random IV
        iv = os.urandom(16)

        # Encrypt content
        cipher = Cipher(algorithms.AES(chat_key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        # Pad content to multiple of 16 bytes
        padded_content = self.pad_content(content.encode())

        encrypted_content = encryptor.update(padded_content) + encryptor.finalize()

        # Combine IV and encrypted content
        result = iv + encrypted_content

        return base64.b64encode(result).decode()

    async def decrypt_message(self, encrypted_content: str, chat_id: str) -> str:
        """Decrypt message content"""
        chat_key = await self.get_chat_key(chat_id)

        # Decode base64
        encrypted_data = base64.b64decode(encrypted_content)

        # Extract IV and content
        iv = encrypted_data[:16]
        content = encrypted_data[16:]

        # Decrypt
        cipher = Cipher(algorithms.AES(chat_key), modes.CBC(iv))
        decryptor = cipher.decryptor()

        decrypted_padded = decryptor.update(content) + decryptor.finalize()

        # Remove padding
        decrypted_content = self.unpad_content(decrypted_padded)

        return decrypted_content.decode()

    def pad_content(self, content: bytes) -> bytes:
        """Add PKCS7 padding"""
        padding_length = 16 - (len(content) % 16)
        padding = bytes([padding_length] * padding_length)
        return content + padding

    def unpad_content(self, padded_content: bytes) -> bytes:
        """Remove PKCS7 padding"""
        padding_length = padded_content[-1]
        return padded_content[:-padding_length]

    async def store_chat_key(self, chat_id: str, key: bytes):
        """Store chat key securely"""
        # In production, encrypt key before storage
        pass

    async def get_chat_key(self, chat_id: str) -> bytes:
        """Retrieve chat key"""
        return self.chat_keys.get(chat_id)
```

## 📊 Performance Optimizations

### 1. Message Caching Strategy

```python
class MessageCache:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def cache_chat_messages(self, chat_id: str, messages: List[Message]):
        """Cache recent messages for a chat"""
        pipe = self.redis.pipeline()

        for message in messages:
            message_data = json.dumps({
                'message_id': message.message_id,
                'sender_id': message.sender_id,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'message_type': message.message_type.value
            })

            pipe.zadd(
                f"chat_messages:{chat_id}",
                {message_data: message.timestamp.timestamp()}
            )

        # Keep only last 100 messages
        pipe.zremrangebyrank(f"chat_messages:{chat_id}", 0, -101)
        pipe.expire(f"chat_messages:{chat_id}", 3600)

        await pipe.execute()

    async def get_cached_messages(self, chat_id: str, limit: int = 50) -> List[Message]:
        """Get cached messages for a chat"""
        cached_data = await self.redis.zrevrange(
            f"chat_messages:{chat_id}", 0, limit - 1
        )

        messages = []
        for data in cached_data:
            try:
                message_dict = json.loads(data)
                message_dict['timestamp'] = datetime.fromisoformat(message_dict['timestamp'])
                message_dict['message_type'] = MessageType(message_dict['message_type'])
                messages.append(Message(**message_dict))
            except Exception as e:
                logging.error(f"Error parsing cached message: {e}")

        return messages
```

### 2. Connection Pooling and Load Balancing

```python
class ConnectionLoadBalancer:
    def __init__(self, server_pool):
        self.servers = server_pool
        self.current_connections = {server: 0 for server in server_pool}

    def get_least_loaded_server(self):
        """Get server with least connections"""
        return min(self.current_connections, key=self.current_connections.get)

    def add_connection(self, server):
        """Record new connection"""
        self.current_connections[server] += 1

    def remove_connection(self, server):
        """Record connection removal"""
        self.current_connections[server] = max(0, self.current_connections[server] - 1)
```

## ✅ Knowledge Check

After studying this design, you should understand:

- [ ] Real-time messaging architecture with WebSockets
- [ ] Message storage and retrieval at scale using Cassandra
- [ ] End-to-end encryption implementation
- [ ] Media processing and CDN integration
- [ ] Message delivery and status tracking
- [ ] Connection management and presence system
- [ ] Database partitioning for chat applications
- [ ] Performance optimization techniques

## 🔄 Next Steps

- Study [YouTube Video Streaming](../youtube-video-streaming/) for media delivery
- Learn about [Netflix Architecture](../netflix-architecture/) for global scale
- Explore push notification systems
- Implement message search with Elasticsearch
- Add voice and video calling features
- Study WhatsApp's actual technical blog posts
- Practice implementing WebSocket servers
- Learn about message queue systems for reliability