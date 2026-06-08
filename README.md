# MMPay Python SDK

A Python client library for integrating with the MMPay Payment Gateway. This SDK is a direct port of the official Node.js SDK, providing utilities for payment creation, transaction retrieval, handshake authentication, and callback verification for technical architects and developers.

## Features

- Sandbox & Production Support: Dedicated methods for both environments.
- Payment Creation & Retrieval: Endpoints to create payments and fetch transaction statuses.
- HMAC SHA256 Signing: Automatic signature generation for request integrity.
- Callback Verification: Utility to verify incoming webhooks from MMPay.
- Type Definitions: Includes TypedDict definitions for clear payload structuring.

## Installation

```bash 
pip install mmpay-python-sdk 
```

## Configuration

To use the SDK, you need your App ID, Publishable Key, and Secret Key provided by the MyanMyanPay dashboard.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| appId | str | Yes | Your unique Application ID. |
| publishableKey | str | Yes | Public key for authentication. |
| secretKey | str | Yes | Private key used for signing requests (HMAC). |
| apiBaseUrl | str | Yes | The base URL for the MMPay API. |


```python
from mmpay import MMPaySDK

options = {
    "appId": "YOUR_APP_ID",
    "publishableKey": "YOUR_PUBLISHABLE_KEY",
    "secretKey": "YOUR_SECRET_KEY",
    "apiBaseUrl": "https://xxx.myanmyanpay.com"
}

sdk = MMPaySDK(options)
```

## Usage

### 1. Payment Request Payload

Passed to `sdk.pay(params)` or `sdk.sandbox_pay(params)`.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `orderId` | `str` | Yes | Unique identifier for the order (e.g., "ORD-001"). |
| `amount` | `float` | Yes | Total transaction amount. |
| `items` | `List[Item]` | No | A list of items included in the order. |
| `callbackUrl` | `str` | No | URL where the webhook callback will be sent. |
| `customMessage` | `str` | No | Custom message to be attached to the transaction. |

**Item Object**

Used inside the `items` list of a Payment Request.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` | Yes | Name of the product/service. |
| `amount` | `float` | Yes | Price per unit. |
| `quantity` | `int` | Yes | Quantity of the item. |

### 2. Create a Payment

```python
try:
    payment_request = {
        "orderId": "ORD-LIVE-98765",
        "amount": 5000,
        "callbackUrl": "https://your-site.com/webhook/mmpay",
        "customMessage": "Your Custom Message",
        "items": [
            {
                "name": "Premium Subscription",
                "amount": 5000,
                "quantity": 1
            }
        ]
    }

    response = sdk.pay(payment_request)
    print(response.get('url'))

except Exception as e:
    print(e)
```

### 3. Retrieve a Payment 

```python
try:
    get_request = {
        "orderId": "ORD-SANDBOX-001"
    }

    response = sdk.get(get_request)
    print(response)
```

### 4. Handling Webhooks

When MyanMyanPay sends a callback to your `callbackUrl`[cite: 1], you must verify the request signature to ensure it is genuine. 
When you implement this method, our package automatically process the Hmac verification  

**Incoming Headers**

| Field Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `Content-Type` | `str` | Yes | `application/json` |
| `X-Mmpay-Signature` | `str` | Yes | Generated HMAC signature |
| `X-Mmpay-Nonce` | `str` | Yes | Unique nonce string |

```python

from mmpay.client import MMPaySDK

sdk = MMPaySDK({
    'appId': 'your_app_id',
    'publishableKey': 'pk_test_12345',
    'secretKey': 'your_secret_key',
    'apiBaseUrl': 'https://api.myanmyanpay.com'
})

def handle_create(tx):
    print("Created:", tx.get('orderId'))

def handle_success(tx):
    print("Success:", tx.get('orderId'))

def handle_fail(tx):
    print("Failed:", tx.get('orderId'))

def handle_refund(tx):
    print("Refunded:", tx.get('orderId'))

def handle_cancel(tx):
    print("Cancelled:", tx.get('orderId'))

def handle_expire(tx):
    print("Expired:", tx.get('orderId'))

def handle_heartbeat(tx):
    print("Heartbeat:", tx.get('orderId'))

def handle_unknown(tx):
    print("Unknown:", tx.get('status'))

def handle_error(error):
    print("Error:", error)

sdk.on_tx_create(handle_create)
sdk.on_tx_success(handle_success)
sdk.on_tx_fail(handle_fail)
sdk.on_tx_refund(handle_refund)
sdk.on_tx_cancel(handle_cancel)
sdk.on_tx_expire(handle_expire)
sdk.on_heartbeat(handle_heartbeat)
sdk.on('tx:unknown', handle_unknown)
sdk.on('error', handle_error)


@app.route('/webhooks/mmpay', methods=['POST'])
def mmpay_webhook():
    payload_str = request.data.decode('utf-8')
    nonce = request.headers.get('X-Mmpay-Nonce')
    signature = request.headers.get('X-Mmpay-Signature')

    if not nonce or not signature:
        return jsonify({"error": "Missing headers"}), 400

    sdk.listen(payload_str, nonce, signature)
    
    return jsonify({"received": True}), 200

if __name__ == '__main__':
    app.run(port=5000)

```

### 5. Verify Callback (Manually)

When MyanMyanPay sends a callback to your `callbackUrl`[cite: 1], you must verify the request signature to ensure it is genuine. 

**Incoming Headers**

| Field Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `Content-Type` | `str` | Yes | `application/json` |
| `X-Mmpay-Signature` | `str` | Yes | Generated HMAC signature |
| `X-Mmpay-Nonce` | `str` | Yes | Unique nonce string |

**Example Verification (Flask)**


```python
from flask import request

@app.route('/webhooks/mmpay', methods=['POST'])
def mmpay_webhook():
    payload_str = request.data.decode('utf-8')
    nonce = request.headers.get('X-Mmpay-Nonce')
    signature = request.headers.get('X-Mmpay-Signature')

    try:
        is_valid = sdk.verify_cb(payload_str, nonce, signature)
        
        if is_valid:
            return "Verified", 200
        else:
            return "Invalid Signature", 400

    except ValueError as e:
        return str(e), 400
```

## Error Codes

### API Key Layer (SERVER SDK)

| Code | Description |
| :--- | :--- |
| `KA0001` | Bearer Token Not Included |
| `KA0002` | API Key Not 'LIVE' |
| `KA0003` | Signature mismatch |
| `KA0004` | Internal Server Error |
| `KA0005` | IP Not whitelisted |
| `429` | Rate limit hit (1000 req/min) |

### JWT Layer (SERVER SDK)

| Code | Description |
| :--- | :--- |
| `BA001` | `Btoken` nonce token missing |
| `BA002` | `Btoken` nonce mismatch |

## License

MIT