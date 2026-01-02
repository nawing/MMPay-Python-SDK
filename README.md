
# MMPay Python SDK

A Python client library for integrating with the MMPay Payment Gateway. This SDK is a direct port of the official Node.js SDK, providing utilities for payment creation, handshake authentication, and callback verification.

## Features

- **Sandbox & Production Support**: dedicated methods for both environments.
- **HMAC SHA256 Signing**: Automatic signature generation for request integrity.
- **Callback Verification**: Utility to verify incoming webhooks from MMPay.
- **Type Definitions**: Includes `TypedDict` definitions for clear payload structuring.

## Installation

Install the package via pip:

```bash
pip install mmpay-python-sdk
```

## Configuration

To use the SDK, you need your **App ID**, **Publishable Key**, and **Secret Key** provided by the MMPay dashboard.

```python
from mmpay import MMPaySDK

# Initialize the SDK
options = {
    "appId": "YOUR_APP_ID",
    "publishableKey": "YOUR_PUBLISHABLE_KEY",
    "secretKey": "YOUR_SECRET_KEY",
    "apiBaseUrl": "[https://xxx.myanmyanpay.com](https://xxx.myanmyanpay.com)" # Replace with actual API Base URL [ Register With Us]
}

sdk = MMPaySDK(options)
```

## Usage

### 1. Create a Payment (Sandbox)

Use `sandbox_pay` to create a payment order in the Sandbox environment. This handles the handshake and signature generation automatically.

```python
try:
    payment_request = {
        "orderId": "ORD-SANDBOX-001",
        "amount": 5000,             # Amount in minor units (e.g., cents) or as required
        "currency": "MMK",
        "callbackUrl": "[https://your-site.com/webhook/mmpay](https://your-site.com/webhook/mmpay)",
        "items": [
            {
                "name": "Premium Subscription",
                "amount": 5000,
                "quantity": 1
            }
        ]
    }

    response = sdk.sandbox_pay(payment_request)
    print("Payment Response:", response)

except Exception as e:
    print("Error creating payment:", e)
```

### 2. Create a Payment (Production)

For production environments, use the `pay` method.

```python
try:
    payment_request = {
        "orderId": "ORD-LIVE-98765",
        "amount": 10000,
        "items": [
            {"name": "E-Commerce Item", "amount": 10000, "quantity": 1}
        ]
    }

    # Helper automatically handles the handshake and signing
    response = sdk.pay(payment_request)
    print("Production Payment URL:", response.get('url'))

except Exception as e:
    print("Error:", e)
```

### 3. Verify Callback (Webhook)

When MMPay sends a callback to your `callbackUrl`, you must verify the request signature to ensure it is genuine.

**Example using Flask:**

```python
from flask import request

@app.route('/webhook/mmpay', methods=['POST'])
def mmpay_webhook():
    # 1. Get the raw payload body as a string (Crucial for signature check)
    payload_str = request.data.decode('utf-8') 
    
    # 2. Get headers
    nonce = request.headers.get('X-Mmpay-Nonce')
    signature = request.headers.get('X-Mmpay-Signature')

    try:
        # 3. Verify
        is_valid = sdk.verify_cb(payload_str, nonce, signature)
        
        if is_valid:
            # Process the order (e.g., mark as paid in DB)
            return "Verified", 200
        else:
            return "Invalid Signature", 400

    except ValueError as e:
        return str(e), 400
```

## API Reference & Input Parameters

### 1. SDK Initialization (`SDKOptions`)

Used when instantiating `MMPaySDK(options)`.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `appId` | `str` | Yes | Your unique Application ID. |
| `publishableKey` | `str` | Yes | Public key for authentication. |
| `secretKey` | `str` | Yes | Private key used for signing requests (HMAC). |
| `apiBaseUrl` | `str` | Yes | The base URL for the MMPay API. |

### 2. Payment Request (`pay` / `sandbox_pay`)

Passed to `sdk.pay(params)` or `sdk.sandbox_pay(params)`.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `orderId` | `str` | Yes | Unique identifier for the order (e.g., "ORD-001"). |
| `amount` | `number` | Yes | Total transaction amount. |
| `items` | `List[Item]` | Yes | A list of items included in the order (see table below). |
| `currency` | `str` | No | Currency code (e.g., "MMK", "USD"). |
| `callbackUrl` | `str` | No | URL where the webhook callback will be sent. |

### 3. Item Object

Used inside the `items` list of a Payment Request.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | `str` | Yes | Name of the product or service. |
| `amount` | `number` | Yes | Price per unit. |
| `quantity` | `int` | Yes | Quantity of the item. |

### 4. Callback Verification (`verify_cb`)

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `payload` | `str` | The **raw** JSON string body of the incoming request. |
| `nonce` | `str` | The value of the `X-Mmpay-Nonce` header. |
| `expected_signature` | `str` | The value of the `X-Mmpay-Signature` header. |

## License

MIT