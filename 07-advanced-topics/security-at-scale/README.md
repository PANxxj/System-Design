# Security at Scale 🔴

## 🎯 Learning Objectives
- Implement security measures for large-scale systems
- Design defense-in-depth strategies
- Handle authentication and authorization at scale
- Protect against common security threats
- Implement compliance and audit frameworks

## 🛡️ Security Fundamentals at Scale

### Core Security Principles

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from datetime import datetime, timedelta
import hashlib
import secrets
import jwt
import bcrypt
import logging

class SecurityPrinciple(Enum):
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"
    AVAILABILITY = "availability"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NON_REPUDIATION = "non_repudiation"

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityEvent:
    event_id: str
    event_type: str
    severity: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    timestamp: datetime
    description: str
    metadata: Dict
    resolved: bool = False

@dataclass
class SecurityPolicy:
    policy_id: str
    name: str
    description: str
    rules: List[Dict]
    enforcement_level: str  # warn, block, audit
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
```

## 🔐 Authentication at Scale

### 1. Multi-Factor Authentication (MFA)

```python
import pyotp
import qrcode
from io import BytesIO
import base64

class MFAService:
    def __init__(self, redis_client, notification_service):
        self.redis = redis_client
        self.notification_service = notification_service

    async def setup_totp(self, user_id: str, user_email: str) -> Dict:
        """Setup Time-based One-Time Password (TOTP)"""
        # Generate secret key
        secret = pyotp.random_base32()

        # Create TOTP instance
        totp = pyotp.TOTP(secret)

        # Generate QR code for authenticator apps
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name="YourApp"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 for easy transport
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_data = base64.b64encode(buffer.getvalue()).decode()

        # Store secret temporarily (user must verify setup)
        await self.redis.setex(
            f"mfa_setup:{user_id}",
            300,  # 5 minutes
            secret
        )

        return {
            "secret": secret,
            "qr_code": qr_code_data,
            "backup_codes": self.generate_backup_codes()
        }

    async def verify_totp_setup(self, user_id: str, token: str) -> bool:
        """Verify TOTP setup with user-provided token"""
        secret = await self.redis.get(f"mfa_setup:{user_id}")
        if not secret:
            return False

        totp = pyotp.TOTP(secret.decode())
        if totp.verify(token, valid_window=1):
            # Save MFA secret permanently
            await self.save_mfa_secret(user_id, secret.decode())
            await self.redis.delete(f"mfa_setup:{user_id}")
            return True

        return False

    async def verify_totp(self, user_id: str, token: str) -> bool:
        """Verify TOTP token for authentication"""
        secret = await self.get_mfa_secret(user_id)
        if not secret:
            return False

        totp = pyotp.TOTP(secret)

        # Check if token was recently used (prevent replay)
        token_key = f"used_token:{user_id}:{token}"
        if await self.redis.exists(token_key):
            return False

        if totp.verify(token, valid_window=1):
            # Mark token as used
            await self.redis.setex(token_key, 60, "used")
            return True

        return False

    async def send_sms_code(self, user_id: str, phone_number: str) -> bool:
        """Send SMS-based MFA code"""
        # Generate 6-digit code
        code = secrets.randbelow(900000) + 100000

        # Store code with expiration
        await self.redis.setex(
            f"sms_code:{user_id}",
            300,  # 5 minutes
            str(code)
        )

        # Send SMS
        message = f"Your verification code is: {code}. Valid for 5 minutes."
        return await self.notification_service.send_sms(phone_number, message)

    async def verify_sms_code(self, user_id: str, code: str) -> bool:
        """Verify SMS MFA code"""
        stored_code = await self.redis.get(f"sms_code:{user_id}")
        if not stored_code:
            return False

        if stored_code.decode() == code:
            await self.redis.delete(f"sms_code:{user_id}")
            return True

        return False

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for MFA recovery"""
        codes = []
        for _ in range(count):
            code = '-'.join([
                secrets.token_hex(4).upper()
                for _ in range(2)
            ])
            codes.append(code)
        return codes

    async def save_mfa_secret(self, user_id: str, secret: str):
        """Save MFA secret to secure storage"""
        # In production, encrypt before storage
        encrypted_secret = self.encrypt_secret(secret)
        # Store in database
        pass

    async def get_mfa_secret(self, user_id: str) -> Optional[str]:
        """Retrieve and decrypt MFA secret"""
        # Get from database and decrypt
        pass

    def encrypt_secret(self, secret: str) -> str:
        """Encrypt MFA secret"""
        # Use your encryption service
        pass

class AdvancedAuthService:
    def __init__(self, db_connection, redis_client, mfa_service):
        self.db = db_connection
        self.redis = redis_client
        self.mfa_service = mfa_service
        self.failed_attempts = {}

    async def authenticate_with_risk_scoring(self, email: str, password: str,
                                           request_context: Dict) -> Dict:
        """Authenticate with risk-based analysis"""
        # Calculate risk score
        risk_score = await self.calculate_risk_score(email, request_context)

        # Basic authentication
        user = await self.verify_credentials(email, password)
        if not user:
            await self.log_failed_attempt(email, request_context)
            return {"success": False, "reason": "invalid_credentials"}

        # Check if account is locked
        if await self.is_account_locked(user["user_id"]):
            return {"success": False, "reason": "account_locked"}

        auth_result = {
            "success": True,
            "user_id": user["user_id"],
            "risk_score": risk_score,
            "requires_mfa": False,
            "requires_additional_verification": False
        }

        # Determine if MFA is required based on risk
        if risk_score > 0.7 or user["mfa_enabled"]:
            auth_result["requires_mfa"] = True

        # High-risk scenarios require additional verification
        if risk_score > 0.9:
            auth_result["requires_additional_verification"] = True
            await self.initiate_additional_verification(user["user_id"])

        return auth_result

    async def calculate_risk_score(self, email: str, context: Dict) -> float:
        """Calculate authentication risk score (0-1)"""
        risk_factors = []

        # Geolocation risk
        user_location_history = await self.get_user_location_history(email)
        current_location = context.get("location", {})

        if self.is_unusual_location(current_location, user_location_history):
            risk_factors.append(0.3)

        # Device fingerprinting
        device_fingerprint = context.get("device_fingerprint")
        known_devices = await self.get_known_devices(email)

        if device_fingerprint not in known_devices:
            risk_factors.append(0.4)

        # Time-based risk
        login_time = datetime.now().hour
        typical_hours = await self.get_typical_login_hours(email)

        if login_time not in typical_hours:
            risk_factors.append(0.2)

        # IP reputation
        ip_address = context.get("ip_address")
        if await self.is_suspicious_ip(ip_address):
            risk_factors.append(0.5)

        # Recent failed attempts
        recent_failures = await self.get_recent_failed_attempts(email)
        if recent_failures > 3:
            risk_factors.append(0.3)

        # Behavioral analysis
        behavioral_risk = await self.analyze_behavioral_patterns(email, context)
        risk_factors.append(behavioral_risk)

        # Calculate final score (max of all factors, not sum)
        return min(1.0, max(risk_factors) if risk_factors else 0.0)

    async def verify_credentials(self, email: str, password: str) -> Optional[Dict]:
        """Verify user credentials with rate limiting"""
        # Check rate limiting
        if await self.is_rate_limited(email):
            return None

        # Get user from database
        user = await self.db.fetch_one(
            "SELECT user_id, email, password_hash, mfa_enabled, account_status FROM users WHERE email = ?",
            [email]
        )

        if not user or user["account_status"] != "active":
            return None

        # Verify password
        if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            await self.clear_failed_attempts(email)
            return user

        return None

    async def is_rate_limited(self, email: str) -> bool:
        """Check if user is rate limited"""
        attempts_key = f"auth_attempts:{email}"
        current_attempts = await self.redis.get(attempts_key)

        if current_attempts and int(current_attempts) >= 5:
            return True

        return False

    async def log_failed_attempt(self, email: str, context: Dict):
        """Log failed authentication attempt"""
        attempts_key = f"auth_attempts:{email}"

        # Increment attempts counter
        await self.redis.incr(attempts_key)
        await self.redis.expire(attempts_key, 3600)  # 1 hour window

        # Log security event
        security_event = SecurityEvent(
            event_id=str(secrets.token_hex(16)),
            event_type="failed_authentication",
            severity=ThreatLevel.MEDIUM,
            source_ip=context.get("ip_address", "unknown"),
            user_id=None,
            timestamp=datetime.now(),
            description=f"Failed authentication attempt for {email}",
            metadata=context
        )

        await self.log_security_event(security_event)

    async def initiate_additional_verification(self, user_id: str):
        """Initiate additional verification for high-risk logins"""
        # Send email with login verification link
        verification_token = secrets.token_urlsafe(32)

        await self.redis.setex(
            f"login_verification:{user_id}",
            1800,  # 30 minutes
            verification_token
        )

        # Send notification
        await self.notification_service.send_login_verification_email(
            user_id, verification_token
        )

    async def complete_additional_verification(self, user_id: str, token: str) -> bool:
        """Complete additional verification process"""
        stored_token = await self.redis.get(f"login_verification:{user_id}")

        if stored_token and stored_token.decode() == token:
            await self.redis.delete(f"login_verification:{user_id}")
            return True

        return False

    # Helper methods (simplified implementations)
    async def get_user_location_history(self, email: str) -> List[Dict]:
        return []

    async def is_unusual_location(self, current: Dict, history: List[Dict]) -> bool:
        return False

    async def get_known_devices(self, email: str) -> Set[str]:
        return set()

    async def get_typical_login_hours(self, email: str) -> Set[int]:
        return {9, 10, 11, 12, 13, 14, 15, 16, 17}

    async def is_suspicious_ip(self, ip_address: str) -> bool:
        return False

    async def get_recent_failed_attempts(self, email: str) -> int:
        attempts = await self.redis.get(f"auth_attempts:{email}")
        return int(attempts) if attempts else 0

    async def analyze_behavioral_patterns(self, email: str, context: Dict) -> float:
        return 0.0

    async def is_account_locked(self, user_id: str) -> bool:
        return False

    async def clear_failed_attempts(self, email: str):
        await self.redis.delete(f"auth_attempts:{email}")

    async def log_security_event(self, event: SecurityEvent):
        # Log to security monitoring system
        pass
```

## 🔒 Authorization and Access Control

### 1. Role-Based Access Control (RBAC)

```python
from typing import Set, List, Dict
from enum import Enum

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"

class ResourceType(Enum):
    USER = "user"
    ORDER = "order"
    PRODUCT = "product"
    SYSTEM = "system"
    REPORT = "report"

@dataclass
class Role:
    role_id: str
    name: str
    description: str
    permissions: Set[str]  # Set of permission strings
    is_system_role: bool = False

@dataclass
class PolicyRule:
    resource_type: ResourceType
    resource_id: Optional[str]  # None means all resources of this type
    permission: Permission
    conditions: Dict  # Additional conditions

class RBACService:
    def __init__(self, db_connection, cache_client):
        self.db = db_connection
        self.cache = cache_client

    async def assign_role_to_user(self, user_id: str, role_id: str,
                                assigned_by: str) -> bool:
        """Assign role to user"""
        # Check if assigner has permission
        if not await self.has_permission(assigned_by, Permission.ADMIN, ResourceType.USER):
            return False

        # Check if role exists
        role = await self.get_role(role_id)
        if not role:
            return False

        # Assign role
        await self.db.execute(
            """INSERT INTO user_roles (user_id, role_id, assigned_by, assigned_at)
               VALUES (?, ?, ?, ?)""",
            [user_id, role_id, assigned_by, datetime.now()]
        )

        # Clear user permissions cache
        await self.cache.delete(f"user_permissions:{user_id}")

        # Log assignment
        await self.log_role_assignment(user_id, role_id, assigned_by)

        return True

    async def has_permission(self, user_id: str, permission: Permission,
                           resource_type: ResourceType, resource_id: str = None,
                           context: Dict = None) -> bool:
        """Check if user has specific permission"""
        # Check cache first
        cache_key = f"permission:{user_id}:{permission.value}:{resource_type.value}:{resource_id}"
        cached_result = await self.cache.get(cache_key)

        if cached_result is not None:
            return cached_result == "true"

        # Get user permissions
        user_permissions = await self.get_user_permissions(user_id)

        # Check direct permission
        permission_string = f"{resource_type.value}:{permission.value}"
        if resource_id:
            specific_permission = f"{permission_string}:{resource_id}"
            if specific_permission in user_permissions:
                result = True
            elif permission_string in user_permissions:
                result = True
            else:
                result = False
        else:
            result = permission_string in user_permissions

        # Check policy-based permissions
        if not result:
            result = await self.check_policy_permissions(
                user_id, permission, resource_type, resource_id, context
            )

        # Cache result for 5 minutes
        await self.cache.setex(cache_key, 300, "true" if result else "false")

        return result

    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for a user"""
        cache_key = f"user_permissions:{user_id}"
        cached_permissions = await self.cache.get(cache_key)

        if cached_permissions:
            return set(cached_permissions.split(","))

        # Get user roles
        user_roles = await self.db.fetch_all(
            "SELECT role_id FROM user_roles WHERE user_id = ? AND is_active = true",
            [user_id]
        )

        all_permissions = set()

        # Collect permissions from all roles
        for role_row in user_roles:
            role = await self.get_role(role_row["role_id"])
            if role:
                all_permissions.update(role.permissions)

        # Cache permissions for 10 minutes
        if all_permissions:
            await self.cache.setex(
                cache_key, 600, ",".join(all_permissions)
            )

        return all_permissions

    async def check_policy_permissions(self, user_id: str, permission: Permission,
                                     resource_type: ResourceType, resource_id: str = None,
                                     context: Dict = None) -> bool:
        """Check policy-based permissions"""
        # Get applicable policies
        policies = await self.get_user_policies(user_id)

        for policy in policies:
            for rule in policy.rules:
                if (rule["resource_type"] == resource_type.value and
                    rule["permission"] == permission.value):

                    # Check resource-specific access
                    if rule.get("resource_id") and rule["resource_id"] != resource_id:
                        continue

                    # Check conditions
                    if await self.evaluate_policy_conditions(rule.get("conditions", {}), context):
                        return True

        return False

    async def evaluate_policy_conditions(self, conditions: Dict, context: Dict) -> bool:
        """Evaluate policy conditions"""
        if not conditions:
            return True

        # Time-based conditions
        if "time_range" in conditions:
            current_hour = datetime.now().hour
            time_range = conditions["time_range"]
            if not (time_range["start"] <= current_hour <= time_range["end"]):
                return False

        # IP-based conditions
        if "allowed_ips" in conditions:
            user_ip = context.get("ip_address") if context else None
            if user_ip not in conditions["allowed_ips"]:
                return False

        # Department-based conditions
        if "department" in conditions:
            user_department = await self.get_user_department(context.get("user_id"))
            if user_department != conditions["department"]:
                return False

        return True

    async def create_dynamic_role(self, base_role_id: str, additional_permissions: Set[str],
                                conditions: Dict, expires_at: datetime) -> str:
        """Create temporary role with additional permissions"""
        base_role = await self.get_role(base_role_id)
        if not base_role:
            raise ValueError("Base role not found")

        # Combine permissions
        combined_permissions = base_role.permissions.union(additional_permissions)

        # Create temporary role
        temp_role_id = f"temp_{secrets.token_hex(8)}"
        temp_role = Role(
            role_id=temp_role_id,
            name=f"Temporary role based on {base_role.name}",
            description="Dynamically created temporary role",
            permissions=combined_permissions
        )

        # Store with expiration
        await self.store_temporary_role(temp_role, conditions, expires_at)

        return temp_role_id

    async def audit_user_access(self, user_id: str, days_back: int = 30) -> Dict:
        """Audit user access patterns"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Get access logs
        access_logs = await self.db.fetch_all(
            """SELECT * FROM access_logs
               WHERE user_id = ? AND timestamp BETWEEN ? AND ?
               ORDER BY timestamp DESC""",
            [user_id, start_date, end_date]
        )

        # Analyze patterns
        resource_access = {}
        permission_usage = {}
        access_times = []

        for log in access_logs:
            # Resource access frequency
            resource_key = f"{log['resource_type']}:{log['resource_id']}"
            resource_access[resource_key] = resource_access.get(resource_key, 0) + 1

            # Permission usage
            permission = log['permission']
            permission_usage[permission] = permission_usage.get(permission, 0) + 1

            # Access times
            access_times.append(log['timestamp'].hour)

        return {
            "user_id": user_id,
            "audit_period": {"start": start_date, "end": end_date},
            "total_access_events": len(access_logs),
            "most_accessed_resources": sorted(resource_access.items(),
                                            key=lambda x: x[1], reverse=True)[:10],
            "permission_distribution": permission_usage,
            "typical_access_hours": list(set(access_times)),
            "unusual_access_patterns": await self.detect_unusual_patterns(access_logs)
        }

    async def detect_unusual_patterns(self, access_logs: List[Dict]) -> List[str]:
        """Detect unusual access patterns"""
        anomalies = []

        # Check for after-hours access
        after_hours_count = sum(1 for log in access_logs if log['timestamp'].hour > 22 or log['timestamp'].hour < 6)
        if after_hours_count > len(access_logs) * 0.1:  # More than 10% after hours
            anomalies.append("Frequent after-hours access detected")

        # Check for rapid successive access
        timestamps = [log['timestamp'] for log in access_logs]
        timestamps.sort()

        rapid_access_count = 0
        for i in range(1, len(timestamps)):
            if (timestamps[i] - timestamps[i-1]).total_seconds() < 1:
                rapid_access_count += 1

        if rapid_access_count > 50:
            anomalies.append("High frequency rapid access detected")

        # Check for access to sensitive resources
        sensitive_access = sum(1 for log in access_logs if 'admin' in log.get('permission', '').lower())
        if sensitive_access > 0:
            anomalies.append(f"Administrative access detected ({sensitive_access} times)")

        return anomalies

    # Helper methods
    async def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        # Implementation would fetch from database and cache
        pass

    async def get_user_policies(self, user_id: str) -> List[Dict]:
        """Get policies applicable to user"""
        # Implementation would fetch user-specific policies
        return []

    async def get_user_department(self, user_id: str) -> str:
        """Get user's department"""
        # Implementation would fetch from user profile
        return "engineering"

    async def store_temporary_role(self, role: Role, conditions: Dict, expires_at: datetime):
        """Store temporary role"""
        # Implementation would store in database with expiration
        pass

    async def log_role_assignment(self, user_id: str, role_id: str, assigned_by: str):
        """Log role assignment event"""
        # Implementation would log to audit system
        pass
```

### 2. Attribute-Based Access Control (ABAC)

```python
class ABACEngine:
    def __init__(self, policy_store, attribute_store):
        self.policy_store = policy_store
        self.attribute_store = attribute_store

    async def evaluate_access(self, subject: Dict, action: str,
                            resource: Dict, environment: Dict) -> bool:
        """Evaluate access using ABAC policies"""
        # Get applicable policies
        policies = await self.policy_store.get_policies(
            resource_type=resource.get("type"),
            action=action
        )

        for policy in policies:
            if await self.evaluate_policy(policy, subject, action, resource, environment):
                return True

        return False

    async def evaluate_policy(self, policy: Dict, subject: Dict, action: str,
                            resource: Dict, environment: Dict) -> bool:
        """Evaluate a single ABAC policy"""
        conditions = policy.get("conditions", [])

        for condition in conditions:
            if not await self.evaluate_condition(condition, subject, action, resource, environment):
                return False

        return True

    async def evaluate_condition(self, condition: Dict, subject: Dict, action: str,
                               resource: Dict, environment: Dict) -> bool:
        """Evaluate a policy condition"""
        condition_type = condition["type"]

        if condition_type == "attribute_match":
            return await self.evaluate_attribute_match(condition, subject, resource)
        elif condition_type == "time_constraint":
            return await self.evaluate_time_constraint(condition, environment)
        elif condition_type == "location_constraint":
            return await self.evaluate_location_constraint(condition, environment)
        elif condition_type == "risk_threshold":
            return await self.evaluate_risk_threshold(condition, subject, environment)

        return False

    async def evaluate_attribute_match(self, condition: Dict, subject: Dict, resource: Dict) -> bool:
        """Evaluate attribute matching condition"""
        subject_attr = condition["subject_attribute"]
        resource_attr = condition["resource_attribute"]
        operator = condition["operator"]

        subject_value = await self.get_subject_attribute(subject["id"], subject_attr)
        resource_value = await self.get_resource_attribute(resource["id"], resource_attr)

        if operator == "equals":
            return subject_value == resource_value
        elif operator == "contains":
            return subject_value in resource_value if isinstance(resource_value, list) else False
        elif operator == "greater_than":
            return subject_value > resource_value
        elif operator == "less_than":
            return subject_value < resource_value

        return False

    async def get_subject_attribute(self, subject_id: str, attribute: str):
        """Get subject attribute value"""
        return await self.attribute_store.get_subject_attribute(subject_id, attribute)

    async def get_resource_attribute(self, resource_id: str, attribute: str):
        """Get resource attribute value"""
        return await self.attribute_store.get_resource_attribute(resource_id, attribute)
```

## 🛡️ Threat Detection and Prevention

### 1. Real-time Threat Detection

```python
import asyncio
from collections import defaultdict, deque
from typing import Deque

class ThreatDetectionEngine:
    def __init__(self, redis_client, ml_service, notification_service):
        self.redis = redis_client
        self.ml_service = ml_service
        self.notification_service = notification_service
        self.detection_rules = []
        self.event_buffers = defaultdict(lambda: deque(maxlen=1000))

    async def process_security_event(self, event: SecurityEvent):
        """Process incoming security event"""
        # Store event
        await self.store_event(event)

        # Add to analysis buffers
        self.event_buffers[event.source_ip].append(event)
        self.event_buffers[f"user:{event.user_id}"].append(event)

        # Run detection rules
        threats = await self.run_detection_rules(event)

        # ML-based anomaly detection
        ml_threats = await self.ml_anomaly_detection(event)

        # Combine threats
        all_threats = threats + ml_threats

        # Handle detected threats
        for threat in all_threats:
            await self.handle_threat(threat)

    async def run_detection_rules(self, event: SecurityEvent) -> List[Dict]:
        """Run rule-based threat detection"""
        detected_threats = []

        # Brute force detection
        if await self.detect_brute_force(event):
            detected_threats.append({
                "type": "brute_force_attack",
                "severity": ThreatLevel.HIGH,
                "source": event.source_ip,
                "description": "Multiple failed login attempts detected"
            })

        # Credential stuffing detection
        if await self.detect_credential_stuffing(event):
            detected_threats.append({
                "type": "credential_stuffing",
                "severity": ThreatLevel.HIGH,
                "source": event.source_ip,
                "description": "Credential stuffing attack detected"
            })

        # Unusual access patterns
        if await self.detect_unusual_access(event):
            detected_threats.append({
                "type": "unusual_access_pattern",
                "severity": ThreatLevel.MEDIUM,
                "source": event.source_ip,
                "description": "Unusual access pattern detected"
            })

        # SQL injection attempts
        if await self.detect_sql_injection(event):
            detected_threats.append({
                "type": "sql_injection_attempt",
                "severity": ThreatLevel.CRITICAL,
                "source": event.source_ip,
                "description": "SQL injection attempt detected"
            })

        return detected_threats

    async def detect_brute_force(self, event: SecurityEvent) -> bool:
        """Detect brute force attacks"""
        if event.event_type != "failed_authentication":
            return False

        # Count failed attempts from same IP in last 5 minutes
        window_start = datetime.now() - timedelta(minutes=5)
        failed_count = 0

        for buffered_event in self.event_buffers[event.source_ip]:
            if (buffered_event.event_type == "failed_authentication" and
                buffered_event.timestamp > window_start):
                failed_count += 1

        return failed_count >= 10

    async def detect_credential_stuffing(self, event: SecurityEvent) -> bool:
        """Detect credential stuffing attacks"""
        if event.event_type != "failed_authentication":
            return False

        # Check for multiple usernames from same IP
        window_start = datetime.now() - timedelta(minutes=10)
        unique_users = set()

        for buffered_event in self.event_buffers[event.source_ip]:
            if (buffered_event.event_type == "failed_authentication" and
                buffered_event.timestamp > window_start):
                unique_users.add(buffered_event.user_id)

        return len(unique_users) >= 20

    async def detect_unusual_access(self, event: SecurityEvent) -> bool:
        """Detect unusual access patterns"""
        if not event.user_id:
            return False

        # Check for access from new locations
        user_locations = await self.get_user_typical_locations(event.user_id)
        current_location = event.metadata.get("location", {})

        if not self.is_typical_location(current_location, user_locations):
            return True

        # Check for access outside typical hours
        current_hour = event.timestamp.hour
        typical_hours = await self.get_user_typical_hours(event.user_id)

        if current_hour not in typical_hours:
            return True

        return False

    async def detect_sql_injection(self, event: SecurityEvent) -> bool:
        """Detect SQL injection attempts"""
        if event.event_type != "api_request":
            return False

        request_data = event.metadata.get("request_data", "")

        # SQL injection patterns
        sql_patterns = [
            r"(\b(select|insert|update|delete|drop|create|alter)\b)",
            r"(\b(union|or|and)\s+\d+\s*=\s*\d+)",
            r"(\'|\"|\`)\s*(or|and)\s*\1\s*=\s*\1",
            r"(exec|execute|sp_|xp_)",
            r"(\-\-|\#|\/\*)"
        ]

        import re
        for pattern in sql_patterns:
            if re.search(pattern, request_data, re.IGNORECASE):
                return True

        return False

    async def ml_anomaly_detection(self, event: SecurityEvent) -> List[Dict]:
        """Use ML for anomaly detection"""
        try:
            # Prepare features for ML model
            features = await self.extract_features(event)

            # Get anomaly score from ML service
            anomaly_score = await self.ml_service.get_anomaly_score(features)

            threats = []
            if anomaly_score > 0.8:
                threats.append({
                    "type": "ml_anomaly",
                    "severity": ThreatLevel.HIGH if anomaly_score > 0.9 else ThreatLevel.MEDIUM,
                    "source": event.source_ip,
                    "description": f"ML anomaly detected (score: {anomaly_score:.2f})",
                    "anomaly_score": anomaly_score
                })

            return threats

        except Exception as e:
            logging.error(f"ML anomaly detection error: {e}")
            return []

    async def extract_features(self, event: SecurityEvent) -> Dict:
        """Extract features for ML model"""
        features = {
            "hour_of_day": event.timestamp.hour,
            "day_of_week": event.timestamp.weekday(),
            "event_type": hash(event.event_type) % 1000,  # Simple hash
            "source_ip_reputation": await self.get_ip_reputation(event.source_ip),
            "user_risk_score": await self.get_user_risk_score(event.user_id) if event.user_id else 0,
            "request_size": len(str(event.metadata)),
            "geographic_distance": await self.calculate_geographic_distance(event)
        }

        return features

    async def handle_threat(self, threat: Dict):
        """Handle detected threat"""
        severity = threat["severity"]

        if severity == ThreatLevel.CRITICAL:
            # Immediate action required
            await self.block_ip(threat["source"])
            await self.alert_security_team(threat)
            await self.escalate_to_soc(threat)

        elif severity == ThreatLevel.HIGH:
            # High priority response
            await self.rate_limit_ip(threat["source"])
            await self.alert_security_team(threat)
            await self.require_additional_auth(threat)

        elif severity == ThreatLevel.MEDIUM:
            # Monitoring and logging
            await self.increase_monitoring(threat["source"])
            await self.log_threat(threat)

        # Always update threat intelligence
        await self.update_threat_intelligence(threat)

    async def block_ip(self, ip_address: str):
        """Block IP address"""
        await self.redis.setex(f"blocked_ip:{ip_address}", 3600, "blocked")
        # Also update firewall rules in production

    async def rate_limit_ip(self, ip_address: str):
        """Apply rate limiting to IP"""
        await self.redis.setex(f"rate_limit:{ip_address}", 1800, "limited")

    async def alert_security_team(self, threat: Dict):
        """Send alert to security team"""
        await self.notification_service.send_security_alert(threat)

    # Helper methods (simplified implementations)
    async def store_event(self, event: SecurityEvent):
        pass

    async def get_user_typical_locations(self, user_id: str) -> List[Dict]:
        return []

    async def is_typical_location(self, current: Dict, typical: List[Dict]) -> bool:
        return True

    async def get_user_typical_hours(self, user_id: str) -> Set[int]:
        return set(range(9, 18))

    async def get_ip_reputation(self, ip_address: str) -> float:
        return 0.5

    async def get_user_risk_score(self, user_id: str) -> float:
        return 0.3

    async def calculate_geographic_distance(self, event: SecurityEvent) -> float:
        return 0.0

    async def escalate_to_soc(self, threat: Dict):
        pass

    async def require_additional_auth(self, threat: Dict):
        pass

    async def increase_monitoring(self, source: str):
        pass

    async def log_threat(self, threat: Dict):
        pass

    async def update_threat_intelligence(self, threat: Dict):
        pass
```

### 2. DDoS Protection

```python
class DDoSProtectionService:
    def __init__(self, redis_client, cloudflare_client):
        self.redis = redis_client
        self.cloudflare = cloudflare_client
        self.rate_limits = {
            "requests_per_second": 100,
            "requests_per_minute": 3000,
            "concurrent_connections": 1000
        }

    async def check_rate_limit(self, ip_address: str, endpoint: str) -> bool:
        """Check if request should be rate limited"""
        current_time = int(time.time())

        # Per-second rate limiting
        second_key = f"rate_limit:{ip_address}:{current_time}"
        second_count = await self.redis.incr(second_key)
        await self.redis.expire(second_key, 1)

        if second_count > self.rate_limits["requests_per_second"]:
            await self.handle_rate_limit_exceeded(ip_address, "requests_per_second")
            return False

        # Per-minute rate limiting
        minute_key = f"rate_limit:{ip_address}:{current_time // 60}"
        minute_count = await self.redis.incr(minute_key)
        await self.redis.expire(minute_key, 60)

        if minute_count > self.rate_limits["requests_per_minute"]:
            await self.handle_rate_limit_exceeded(ip_address, "requests_per_minute")
            return False

        # Endpoint-specific rate limiting
        endpoint_key = f"endpoint_limit:{ip_address}:{endpoint}:{current_time // 60}"
        endpoint_count = await self.redis.incr(endpoint_key)
        await self.redis.expire(endpoint_key, 60)

        endpoint_limit = self.get_endpoint_limit(endpoint)
        if endpoint_count > endpoint_limit:
            await self.handle_rate_limit_exceeded(ip_address, f"endpoint_{endpoint}")
            return False

        return True

    async def detect_ddos_patterns(self, metrics: Dict) -> bool:
        """Detect DDoS attack patterns"""
        # Sudden traffic spike
        if metrics["requests_per_second"] > metrics["baseline_rps"] * 10:
            return True

        # High error rate
        if metrics["error_rate"] > 0.5:
            return True

        # Many unique IPs with similar patterns
        if (metrics["unique_ips"] > 1000 and
            metrics["avg_requests_per_ip"] > 100):
            return True

        # Geographic concentration
        if metrics["top_country_percentage"] > 0.8:
            return True

        return False

    async def activate_ddos_protection(self, attack_type: str):
        """Activate DDoS protection measures"""
        protection_measures = {
            "volumetric": {
                "enable_challenge": True,
                "rate_limit_factor": 0.1,
                "geo_blocking": True
            },
            "application": {
                "enable_captcha": True,
                "javascript_challenge": True,
                "user_agent_blocking": True
            },
            "protocol": {
                "syn_flood_protection": True,
                "connection_limit": 100
            }
        }

        measures = protection_measures.get(attack_type, {})

        for measure, enabled in measures.items():
            if enabled:
                await self.apply_protection_measure(measure)

    async def apply_protection_measure(self, measure: str):
        """Apply specific protection measure"""
        if measure == "enable_challenge":
            await self.cloudflare.set_security_level("high")
        elif measure == "enable_captcha":
            await self.cloudflare.enable_captcha_challenge()
        elif measure == "geo_blocking":
            await self.block_suspicious_countries()

    async def handle_rate_limit_exceeded(self, ip_address: str, limit_type: str):
        """Handle rate limit exceeded"""
        # Temporarily block IP
        block_duration = self.get_block_duration(limit_type)
        await self.redis.setex(f"blocked:{ip_address}", block_duration, limit_type)

        # Log incident
        await self.log_rate_limit_incident(ip_address, limit_type)

    def get_endpoint_limit(self, endpoint: str) -> int:
        """Get rate limit for specific endpoint"""
        endpoint_limits = {
            "/api/auth/login": 10,
            "/api/users/register": 5,
            "/api/orders/create": 60,
            "/api/search": 120
        }
        return endpoint_limits.get(endpoint, 100)

    def get_block_duration(self, limit_type: str) -> int:
        """Get block duration based on limit type"""
        durations = {
            "requests_per_second": 60,
            "requests_per_minute": 300,
            "endpoint_login": 900
        }
        return durations.get(limit_type, 300)

    async def block_suspicious_countries(self):
        """Block traffic from suspicious countries"""
        suspicious_countries = ["XX", "YY"]  # Country codes
        for country in suspicious_countries:
            await self.cloudflare.block_country(country)

    async def log_rate_limit_incident(self, ip_address: str, limit_type: str):
        """Log rate limiting incident"""
        incident = {
            "type": "rate_limit_exceeded",
            "ip_address": ip_address,
            "limit_type": limit_type,
            "timestamp": datetime.now().isoformat()
        }
        # Log to monitoring system
        pass
```

## 🔍 Security Monitoring and Compliance

### 1. Security Information and Event Management (SIEM)

```python
class SIEMService:
    def __init__(self, elasticsearch_client, alert_service):
        self.es = elasticsearch_client
        self.alert_service = alert_service
        self.correlation_rules = []

    async def ingest_security_event(self, event: SecurityEvent):
        """Ingest security event into SIEM"""
        # Enrich event with additional context
        enriched_event = await self.enrich_event(event)

        # Index in Elasticsearch
        await self.es.index(
            index=f"security-events-{datetime.now().strftime('%Y-%m')}",
            body=enriched_event
        )

        # Run correlation analysis
        await self.correlate_events(enriched_event)

        # Check for compliance violations
        await self.check_compliance_violations(enriched_event)

    async def enrich_event(self, event: SecurityEvent) -> Dict:
        """Enrich security event with additional context"""
        enriched = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "severity": event.severity.value,
            "source_ip": event.source_ip,
            "user_id": event.user_id,
            "timestamp": event.timestamp.isoformat(),
            "description": event.description,
            "metadata": event.metadata,
            "resolved": event.resolved
        }

        # Add geolocation data
        if event.source_ip:
            geo_data = await self.get_geolocation(event.source_ip)
            enriched["geo_location"] = geo_data

        # Add threat intelligence
        threat_intel = await self.get_threat_intelligence(event.source_ip)
        enriched["threat_intelligence"] = threat_intel

        # Add user context
        if event.user_id:
            user_context = await self.get_user_context(event.user_id)
            enriched["user_context"] = user_context

        return enriched

    async def correlate_events(self, event: Dict):
        """Correlate events to detect attack patterns"""
        # Look for related events in the last hour
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": "now-1h"}}},
                        {"term": {"source_ip": event["source_ip"]}}
                    ]
                }
            },
            "size": 100
        }

        response = await self.es.search(
            index="security-events-*",
            body=query
        )

        related_events = [hit["_source"] for hit in response["hits"]["hits"]]

        # Apply correlation rules
        for rule in self.correlation_rules:
            if await self.apply_correlation_rule(rule, related_events):
                await self.create_correlation_alert(rule, related_events)

    async def apply_correlation_rule(self, rule: Dict, events: List[Dict]) -> bool:
        """Apply correlation rule to events"""
        rule_type = rule["type"]

        if rule_type == "failed_login_sequence":
            return await self.check_failed_login_sequence(rule, events)
        elif rule_type == "privilege_escalation":
            return await self.check_privilege_escalation(rule, events)
        elif rule_type == "data_exfiltration":
            return await self.check_data_exfiltration(rule, events)

        return False

    async def check_failed_login_sequence(self, rule: Dict, events: List[Dict]) -> bool:
        """Check for failed login followed by successful login"""
        failed_logins = [e for e in events if e["event_type"] == "failed_authentication"]
        successful_logins = [e for e in events if e["event_type"] == "successful_authentication"]

        if len(failed_logins) >= rule["min_failed_attempts"] and len(successful_logins) > 0:
            # Check if successful login came after failed attempts
            last_failed = max(failed_logins, key=lambda x: x["timestamp"])
            first_successful = min(successful_logins, key=lambda x: x["timestamp"])

            if first_successful["timestamp"] > last_failed["timestamp"]:
                return True

        return False

    async def create_correlation_alert(self, rule: Dict, events: List[Dict]):
        """Create alert for correlated events"""
        alert = {
            "alert_id": str(secrets.token_hex(16)),
            "rule_name": rule["name"],
            "severity": rule["severity"],
            "description": rule["description"],
            "correlated_events": [e["event_id"] for e in events],
            "created_at": datetime.now().isoformat()
        }

        await self.alert_service.create_alert(alert)

    async def check_compliance_violations(self, event: Dict):
        """Check for compliance violations"""
        violations = []

        # GDPR compliance checks
        if event["event_type"] == "data_access" and event.get("user_context", {}).get("country") == "EU":
            if not event["metadata"].get("consent_given"):
                violations.append("GDPR: Data access without proper consent")

        # PCI DSS compliance checks
        if event["event_type"] == "payment_processing":
            if not event["metadata"].get("encrypted"):
                violations.append("PCI DSS: Unencrypted payment data processing")

        # SOX compliance checks
        if event["event_type"] == "financial_data_access":
            if not event["metadata"].get("audit_trail"):
                violations.append("SOX: Financial data access without audit trail")

        for violation in violations:
            await self.create_compliance_alert(violation, event)

    async def generate_compliance_report(self, regulation: str, start_date: datetime,
                                       end_date: datetime) -> Dict:
        """Generate compliance report"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"timestamp": {"gte": start_date.isoformat(), "lte": end_date.isoformat()}}},
                        {"term": {"compliance_violation": regulation}}
                    ]
                }
            },
            "aggs": {
                "violation_types": {
                    "terms": {"field": "violation_type"}
                },
                "violations_by_day": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "day"
                    }
                }
            }
        }

        response = await self.es.search(
            index="security-events-*",
            body=query
        )

        return {
            "regulation": regulation,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_violations": response["hits"]["total"]["value"],
            "violation_types": response["aggregations"]["violation_types"]["buckets"],
            "daily_trend": response["aggregations"]["violations_by_day"]["buckets"]
        }

    # Helper methods
    async def get_geolocation(self, ip_address: str) -> Dict:
        return {"country": "US", "city": "San Francisco", "latitude": 37.7749, "longitude": -122.4194}

    async def get_threat_intelligence(self, ip_address: str) -> Dict:
        return {"reputation": "clean", "threat_types": [], "last_seen": None}

    async def get_user_context(self, user_id: str) -> Dict:
        return {"department": "engineering", "access_level": "standard", "country": "US"}

    async def create_compliance_alert(self, violation: str, event: Dict):
        pass
```

### 2. Vulnerability Management

```python
class VulnerabilityManagementService:
    def __init__(self, db_connection, scanner_service):
        self.db = db_connection
        self.scanner = scanner_service

    async def schedule_vulnerability_scan(self, target: str, scan_type: str) -> str:
        """Schedule vulnerability scan"""
        scan_id = str(uuid.uuid4())

        scan_config = {
            "scan_id": scan_id,
            "target": target,
            "scan_type": scan_type,
            "status": "scheduled",
            "created_at": datetime.now(),
            "scheduled_for": datetime.now() + timedelta(minutes=5)
        }

        await self.db.execute(
            """INSERT INTO vulnerability_scans (scan_id, target, scan_type, status, created_at, scheduled_for)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [scan_id, target, scan_type, "scheduled", datetime.now(), scan_config["scheduled_for"]]
        )

        # Schedule scan execution
        await self.schedule_scan_execution(scan_config)

        return scan_id

    async def execute_vulnerability_scan(self, scan_id: str):
        """Execute vulnerability scan"""
        scan = await self.get_scan(scan_id)
        if not scan:
            return

        # Update status
        await self.update_scan_status(scan_id, "running")

        try:
            # Run scan based on type
            if scan["scan_type"] == "network":
                results = await self.scanner.network_scan(scan["target"])
            elif scan["scan_type"] == "web_application":
                results = await self.scanner.web_app_scan(scan["target"])
            elif scan["scan_type"] == "container":
                results = await self.scanner.container_scan(scan["target"])
            else:
                raise ValueError(f"Unknown scan type: {scan['scan_type']}")

            # Process and store results
            await self.process_scan_results(scan_id, results)
            await self.update_scan_status(scan_id, "completed")

        except Exception as e:
            logging.error(f"Scan {scan_id} failed: {e}")
            await self.update_scan_status(scan_id, "failed")

    async def process_scan_results(self, scan_id: str, results: Dict):
        """Process and store scan results"""
        vulnerabilities = results.get("vulnerabilities", [])

        for vuln in vulnerabilities:
            vuln_id = str(uuid.uuid4())

            # Enrich vulnerability data
            enriched_vuln = await self.enrich_vulnerability(vuln)

            # Store vulnerability
            await self.db.execute(
                """INSERT INTO vulnerabilities
                   (vulnerability_id, scan_id, cve_id, severity, title, description,
                    affected_component, remediation, status, discovered_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    vuln_id, scan_id, enriched_vuln.get("cve_id"),
                    enriched_vuln["severity"], enriched_vuln["title"],
                    enriched_vuln["description"], enriched_vuln["affected_component"],
                    enriched_vuln["remediation"], "open", datetime.now()
                ]
            )

            # Create remediation ticket for high/critical vulnerabilities
            if enriched_vuln["severity"] in ["high", "critical"]:
                await self.create_remediation_ticket(vuln_id, enriched_vuln)

    async def enrich_vulnerability(self, vuln: Dict) -> Dict:
        """Enrich vulnerability with additional data"""
        # Add CVE data if available
        if vuln.get("cve_id"):
            cve_data = await self.get_cve_data(vuln["cve_id"])
            vuln.update(cve_data)

        # Add CVSS score calculation
        vuln["cvss_score"] = await self.calculate_cvss_score(vuln)

        # Add business impact assessment
        vuln["business_impact"] = await self.assess_business_impact(vuln)

        # Add remediation suggestions
        vuln["remediation"] = await self.get_remediation_suggestions(vuln)

        return vuln

    async def get_vulnerability_dashboard(self) -> Dict:
        """Get vulnerability management dashboard data"""
        # Get vulnerability counts by severity
        severity_counts = await self.db.fetch_all(
            """SELECT severity, COUNT(*) as count
               FROM vulnerabilities
               WHERE status = 'open'
               GROUP BY severity"""
        )

        # Get trending data
        trend_data = await self.db.fetch_all(
            """SELECT DATE(discovered_at) as date, COUNT(*) as count
               FROM vulnerabilities
               WHERE discovered_at >= DATE('now', '-30 days')
               GROUP BY DATE(discovered_at)
               ORDER BY date"""
        )

        # Get top affected components
        affected_components = await self.db.fetch_all(
            """SELECT affected_component, COUNT(*) as count
               FROM vulnerabilities
               WHERE status = 'open'
               GROUP BY affected_component
               ORDER BY count DESC
               LIMIT 10"""
        )

        # Calculate metrics
        total_vulns = sum(row["count"] for row in severity_counts)
        critical_high = sum(row["count"] for row in severity_counts
                           if row["severity"] in ["critical", "high"])

        return {
            "total_vulnerabilities": total_vulns,
            "critical_high_count": critical_high,
            "severity_breakdown": {row["severity"]: row["count"] for row in severity_counts},
            "discovery_trend": [{"date": row["date"], "count": row["count"]} for row in trend_data],
            "top_affected_components": [{"component": row["affected_component"], "count": row["count"]}
                                      for row in affected_components]
        }

    # Helper methods
    async def get_scan(self, scan_id: str) -> Optional[Dict]:
        return await self.db.fetch_one("SELECT * FROM vulnerability_scans WHERE scan_id = ?", [scan_id])

    async def update_scan_status(self, scan_id: str, status: str):
        await self.db.execute("UPDATE vulnerability_scans SET status = ? WHERE scan_id = ?", [status, scan_id])

    async def schedule_scan_execution(self, scan_config: Dict):
        # Schedule using task queue
        pass

    async def get_cve_data(self, cve_id: str) -> Dict:
        # Fetch from CVE database
        return {}

    async def calculate_cvss_score(self, vuln: Dict) -> float:
        # Calculate CVSS score
        return 7.5

    async def assess_business_impact(self, vuln: Dict) -> str:
        # Assess business impact
        return "medium"

    async def get_remediation_suggestions(self, vuln: Dict) -> str:
        # Get remediation suggestions
        return "Update to latest version"

    async def create_remediation_ticket(self, vuln_id: str, vuln: Dict):
        # Create ticket in ticketing system
        pass
```

## ✅ Knowledge Check

After studying this section, you should understand:

- [ ] Multi-factor authentication implementation at scale
- [ ] Advanced authorization models (RBAC, ABAC)
- [ ] Real-time threat detection and response
- [ ] DDoS protection strategies
- [ ] Security monitoring and SIEM implementation
- [ ] Vulnerability management processes
- [ ] Compliance frameworks and auditing
- [ ] Risk-based authentication systems

## 🔄 Next Steps

- Study incident response procedures
- Learn about security architecture patterns
- Explore zero-trust security models
- Practice implementing security controls
- Study regulatory compliance requirements
- Learn about security testing methodologies
- Understand security metrics and KPIs
- Explore emerging security threats and countermeasures