# API Reference

## Cryptographic Modules

### X448KeyExchange

Classical elliptic curve key exchange.

```python
from src.crypto import X448KeyExchange

kex = X448KeyExchange()
```

#### Methods

##### `generate_keypair() -> bytes`
Generate a new X448 key pair.

**Returns:** Public key bytes (56 bytes)

**Example:**
```python
public_key = kex.generate_keypair()
```

##### `get_public_key_bytes() -> bytes`
Get the public key as bytes.

**Returns:** Public key bytes

##### `compute_shared_secret(peer_public_key_bytes: bytes) -> bytes`
Compute shared secret from peer's public key.

**Parameters:**
- `peer_public_key_bytes`: Peer's X448 public key (56 bytes)

**Returns:** Shared secret (56 bytes)

---

### KyberKEM

Post-quantum key encapsulation mechanism.

```python
from src.crypto import KyberKEM

kem = KyberKEM(variant="Kyber768")
```

#### Parameters
- `variant`: Kyber variant - "Kyber512", "Kyber768", or "Kyber1024" (default: "Kyber768")

#### Methods

##### `generate_keypair() -> bytes`
Generate a new Kyber key pair.

**Returns:** Public key bytes

##### `encapsulate(peer_public_key: bytes) -> tuple[bytes, bytes]`
Encapsulate a shared secret.

**Parameters:**
- `peer_public_key`: Peer's Kyber public key

**Returns:** Tuple of (ciphertext, shared_secret)

##### `decapsulate(ciphertext: bytes) -> bytes`
Decapsulate to recover shared secret.

**Parameters:**
- `ciphertext`: Encapsulated secret

**Returns:** Shared secret

---

### DilithiumSignature

Post-quantum digital signature scheme.

```python
from src.crypto import DilithiumSignature

sig = DilithiumSignature(variant="Dilithium3")
```

#### Parameters
- `variant`: Dilithium variant - "Dilithium2", "Dilithium3", or "Dilithium5" (default: "Dilithium3")

#### Methods

##### `generate_keypair() -> bytes`
Generate a new Dilithium key pair.

**Returns:** Public key bytes

##### `sign(message: bytes) -> bytes`
Sign a message.

**Parameters:**
- `message`: Message to sign

**Returns:** Signature bytes

##### `verify(message: bytes, signature: bytes, public_key: bytes = None) -> bool`
Verify a signature.

**Parameters:**
- `message`: Original message
- `signature`: Signature to verify
- `public_key`: Public key (optional, uses own if None)

**Returns:** True if signature is valid

---

### ChaCha20Poly1305Cipher

Authenticated encryption with associated data.

```python
from src.crypto import ChaCha20Poly1305Cipher

cipher = ChaCha20Poly1305Cipher(key=None)
```

#### Parameters
- `key`: 256-bit (32-byte) encryption key (optional, auto-generated if None)

#### Methods

##### `encrypt(plaintext: bytes, associated_data: bytes = None) -> tuple[bytes, bytes]`
Encrypt plaintext with optional associated data.

**Parameters:**
- `plaintext`: Data to encrypt
- `associated_data`: Additional authenticated data (optional)

**Returns:** Tuple of (nonce, ciphertext)

##### `decrypt(nonce: bytes, ciphertext: bytes, associated_data: bytes = None) -> bytes`
Decrypt ciphertext.

**Parameters:**
- `nonce`: Nonce used during encryption
- `ciphertext`: Encrypted data
- `associated_data`: Additional authenticated data (optional)

**Returns:** Decrypted plaintext

**Raises:** `InvalidTag` if authentication fails

##### `get_key() -> bytes`
Get the encryption key.

**Returns:** 32-byte encryption key

---

### HybridKeyExchange

Hybrid key exchange combining X448 and Kyber.

```python
from src.crypto import HybridKeyExchange

hybrid = HybridKeyExchange()
```

#### Methods

##### `generate_keypair() -> tuple[bytes, bytes]`
Generate hybrid key pair.

**Returns:** Tuple of (x448_public_key, kyber_public_key)

##### `initiate_exchange(peer_x448_pk: bytes, peer_kyber_pk: bytes) -> tuple[bytes, bytes]`
Initiate key exchange (client side).

**Parameters:**
- `peer_x448_pk`: Peer's X448 public key
- `peer_kyber_pk`: Peer's Kyber public key

**Returns:** Tuple of (kyber_ciphertext, combined_secret)

##### `complete_exchange(peer_x448_pk: bytes, kyber_ciphertext: bytes) -> bytes`
Complete key exchange (server side).

**Parameters:**
- `peer_x448_pk`: Peer's X448 public key
- `kyber_ciphertext`: Kyber encapsulated secret

**Returns:** Combined shared secret (32 bytes)

##### `get_shared_secret() -> bytes`
Get the combined shared secret.

**Returns:** 32-byte shared secret

---

## Communication Modules

### Session

Session management for secure connections.

```python
from src.communication import Session

session = Session(session_id="session-001")
```

#### Parameters
- `session_id`: Unique session identifier

#### Methods

##### `start_handshake()`
Start the handshake process.

##### `complete_handshake(shared_secret: bytes, peer_id: str)`
Complete handshake and activate session.

**Parameters:**
- `shared_secret`: Established shared secret
- `peer_id`: Peer identifier

##### `update_activity()`
Update last activity timestamp.

##### `close()`
Close the session.

##### `is_active() -> bool`
Check if session is active.

**Returns:** True if session is active

##### `is_expired(timeout: float = 3600.0) -> bool`
Check if session has expired.

**Parameters:**
- `timeout`: Timeout in seconds (default: 1 hour)

**Returns:** True if session has expired

##### `get_session_info() -> dict`
Get session information.

**Returns:** Dictionary with session details

---

### SecureChannel

Secure data transmission using encryption and signatures.

```python
from src.communication import SecureChannel

channel = SecureChannel(shared_secret, signing_key=None)
```

#### Parameters
- `shared_secret`: Shared secret for encryption (32 bytes)
- `signing_key`: Optional DilithiumSignature instance

#### Methods

##### `send(plaintext: bytes, sign: bool = False) -> dict`
Encrypt and optionally sign a message.

**Parameters:**
- `plaintext`: Message to send
- `sign`: Whether to sign the message (default: False)

**Returns:** Dictionary with nonce, ciphertext, counter, and optional signature

##### `receive(message: dict, verify_key: bytes = None) -> bytes`
Decrypt and optionally verify a message.

**Parameters:**
- `message`: Dictionary with encrypted message
- `verify_key`: Optional public key for signature verification

**Returns:** Decrypted plaintext

**Raises:** `ValueError` if verification or decryption fails

##### `reset_counter()`
Reset message counter.

##### `get_counter() -> int`
Get current message counter.

**Returns:** Message counter value

---

### TelemetryLogger

Telemetry logging for monitoring and analysis.

```python
from src.communication import TelemetryLogger

logger = TelemetryLogger(log_file="telemetry.log")
```

#### Methods

##### `log_event(event_type: str, data: dict)`
Log a telemetry event.

##### `log_handshake(session_id: str, duration: float, success: bool)`
Log handshake event.

##### `log_message(session_id: str, direction: str, size: int, latency: float = None)`
Log message transmission.

##### `log_error(session_id: str, error_type: str, error_message: str)`
Log error event.

##### `log_performance(operation: str, duration: float, metadata: dict = None)`
Log performance metrics.

---

### NetworkMonitor

Network connectivity and performance monitoring.

```python
from src.communication import NetworkMonitor

monitor = NetworkMonitor()
```

#### Methods

##### `get_network_stats() -> dict`
Get current network statistics.

##### `record_latency(latency: float)`
Record a latency sample.

##### `record_packet_sent()`
Record a packet sent.

##### `record_packet_loss()`
Record a packet loss.

##### `get_average_latency() -> float`
Get average latency in milliseconds.

##### `get_packet_loss_rate() -> float`
Get packet loss rate as percentage.

##### `get_connection_quality() -> str`
Get connection quality assessment.

**Returns:** Quality rating - "excellent", "good", "fair", "poor", or "unknown"

##### `get_monitor_summary() -> dict`
Get monitoring summary.

---

## Utility Modules

### Config

Configuration management.

```python
from src.utils import Config

config = Config(config_file="config/custom_config.json")
```

#### Methods

##### `get(key: str, default: any = None) -> any`
Get configuration value.

**Example:**
```python
kyber_variant = config.get("crypto.kyber_variant", "Kyber768")
```

##### `set(key: str, value: any)`
Set configuration value.

##### `save_to_file(config_file: str)`
Save configuration to JSON file.

---

### setup_logger

Set up structured logging.

```python
from src.utils import setup_logger

logger = setup_logger(name="my_app", level="INFO", log_file="app.log")
```

#### Parameters
- `name`: Logger name
- `level`: Logging level - "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
- `log_file`: Optional log file path

**Returns:** Configured structured logger

**Example:**
```python
logger.info("Connection established", peer_id="drone-01")
```
