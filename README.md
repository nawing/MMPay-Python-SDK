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

#### **Implementation**

```python
from mmpay import MMPaySDK

options = {
    "appId": "YOUR_APP_ID",
    "publishableKey": "YOUR_PUBLISHABLE_KEY",
    "secretKey": "YOUR_SECRET_KEY",
    "apiBaseUrl": "https://xxx.myanmyanpay.com"
}

MMPay = MMPaySDK(options)
```
----

## Usage

### 1. Payment Request Payload

#### **Method Signature**
```python
from mmpay.types import PaymentRequest
payload: PaymentRequest = {}
MMPay.pay(payload)
```

#### **Request Body** (`payload` structure)

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `orderId` | `str` | Yes | Unique identifier for the order (e.g., "ORD-001"). |
| `amount` | `float` | Yes | Total transaction amount. |
| `currency` | `str` | No | Currency of the transaction 'Only Support MMK for now' |
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


#### **Implementation**

```python
from mmpay.types import PaymentRequest

try:
    pay_payload: PaymentRequest = {
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

    response = MMPay.pay(pay_payload)
    
    print(response.get('qr')) # this is your QR String [EMVCo String]
    print(response.get('orderId')) #this is your order ID
    print(response.get('transactionRefId')) #this is your QR Reference No
    print(response.get('vendorQrRefId')) #this is your QR Reference No
    print(response.get('amount')) #this is your requested amount

except Exception as e:
    print(e)
```

#### **Response Body** Code (`201`)

```json
{
  "orderId": "_trx_0012345",
  "status": "PENDING",
  "vendorQrRefId": "39233043003345",
  "transactionRefId": "39233043003345", // This is deprecated - transactionRefId will show only after payment is confirmed
  "amount": 2800,
  "currency": "MMK",
  "qr": "EMVco MMQR String => You_have_to_embed_as_qr_image_yourself"
}
```
---


### 2. Retrieve a Payment

#### **Method Signature**
```python
from mmpay.types import PayGetRequest
payload: PayGetRequest = {}
MMPay.get(payload)
```

#### **Request Body** (`payload` structure)

The request body should be a JSON object containing the transaction details.

| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`orderId`**         | `string` | **Yes**    | Your generated order ID for the order or system initiating the payment. | `"ORD-3983833"` |


#### **Implementation**
```python
from mmpay.types import PayGetRequest

try:
    get_payload: PayGetRequest = {
        "orderId": "ORD-SANDBOX-001"
    }

    response = MMPay.get(get_payload)
    print(response)

except Exception as e:
    print(e)
```

#### **Response Body** Code (`200`)

```json
{
  "orderId": "ORD-111111111",
  "appId": "MMP3883483",
  "amount": 1000,
  "vendor": "KBZPay",
  "method": "QR",
  "customMessage": "",
  "callbackUrl": "",
  "callbackUrlAt": "JSDateObject",
  "callbackUrlStatus": "SUCCESS",
  "status": "SUCCESS", //  'PENDING' | 'SUCCESS' | 'FAILED' | 'REFUNDED' | 'CANCELLED' | 'EXPIRED';
  "disbursementId": "289348734939",
  "disStatus": "SUCCESS",
  "condition": "TOUCHED", // TOUCHED | 'PRISTINE' | 'DIRTY' | 'EXPIRED'
  "createdAt": "JSDateObject",
  "transactionRefId": "939583046594",
  "vendorQrRefId": "48309449034",
  "qr": "EMVCo QR String::MMQR Standard",
}
```

----

### 3. Cancel a Payment 

#### **Method Signature**
```python
from mmpay.types import PayCancelRequest
payload: PayCancelRequest = {}
MMPay.cancel(payload)
```

#### **Request Body** (`payload` structure)

The request body should be a JSON object containing the transaction details.

| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`orderId`**         | `string` | **Yes**    | Your generated order ID for the order or system initiating the payment. | `"ORD-3983833"` |

#### **Implementation**
```python
from mmpay.types import PayCancelRequest

try:
    cancel_payload: PayGetRequest = {
        "orderId": "ORD-SANDBOX-001"
    }

    response = MMPay.cancel(cancel_payload)
    print(response)

except Exception as e:
    print(e)
```

#### **Response Body** Code (`200`)
```json
{
  "amount": 1000,
  "orderId": "ORD-111111111",
  "status": "CANCELLED",
  "vendorQrRefId": "289348734939",
}
```

----


### 4. Handling Webhooks

When MyanMyanPay sends a callback to your `callbackUrl`[cite: 1], you must verify the request signature to ensure it is genuine. 
When you implement this method, our package automatically process the Hmac verification  

#### **Incoming Headers**

| Field Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `Content-Type` | `str` | Yes | `application/json` |
| `X-Mmpay-Signature` | `str` | Yes | Generated HMAC signature |
| `X-Mmpay-Nonce` | `str` | Yes | Unique nonce string |

#### **Incoming Body**

| Field Name    | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| **orderId**           | `string` | Yes | Unique identifier for the specific order. |
| **amount**            | `number` | Yes | The transaction amount. |
| **currency**          | `string` | Yes | The 3-letter currency code (e.g., MMK, USD). |
| **vendor**            | `string` | Yes | Identifier for the vendor initiating the request. |
| **method**            | `'QR', 'PIN', 'PWA', 'CARD'`  | Yes | Identifier for the method. |
| **status**            | `'PENDING','SUCCESS','FAILED','REFUNDED', 'EXPIRED', 'CANCELLED'` | Yes | Current status of the transaction. |
| **condition**         | `'PRESTINE', 'TOUCHED', 'EXPIRED', 'DIRTY'`  | Yes | Used QR Code scan again or not |
| **transactionRefId**  | `string` | Yes | The reference ID generated by the payment provider after success payment |
| **vendorQrRefId**     | `string` | Yes | The MMQR reference ID generated by the payment provider. |
| **callbackUrl**       | `string` | No | Optional URL to receive webhooks or updates. |
| **customMessage**     | `string` | No | User provided custom message |

#### **Example Implementation With Flask**

```python

from mmpay.client import MMPaySDK

MMPay = MMPaySDK({
    'appId': 'your_app_id',
    'publishableKey': 'pk_test_12345',
    'secretKey': 'your_secret_key',
    'apiBaseUrl': 'https://api.myanmyanpay.com'
})

def handle_create(tx):
    # if you are using browser plugin MMPay.showPaymentModal() 
    # verify your source of truth here, you can do with an encrypted message in customMessage or just match the amount of order reqest
    # if the amount does not match 'CANCEL' the order immediately, to avoid payload manipulation attacks
    # MMPay.cancel( tx.orderId ) 
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

MMPay.on_tx_create(handle_create)
MMPay.on_tx_success(handle_success)
MMPay.on_tx_fail(handle_fail)
MMPay.on_tx_refund(handle_refund)
MMPay.on_tx_cancel(handle_cancel)
MMPay.on_tx_expire(handle_expire)
MMPay.on_heartbeat(handle_heartbeat)
MMPay.on('tx:unknown', handle_unknown)
MMPay.on('error', handle_error)


@app.route('/webhooks/mmpay', methods=['POST'])
def mmpay_webhook():
    payload_str = request.data.decode('utf-8')
    nonce = request.headers.get('X-Mmpay-Nonce')
    signature = request.headers.get('X-Mmpay-Signature')

    if not nonce or not signature:
        return jsonify({"error": "Missing headers"}), 400

    MMPay.listen(payload_str, nonce, signature)
    
    return jsonify({"received": True}), 200

if __name__ == '__main__':
    app.run(port=5000)

```

### 5. Verify Callback (Manually)

When MyanMyanPay sends a callback to your `callbackUrl`[cite: 1], you must verify the request signature to ensure it is genuine. 

#### **Example Implementation With Flask**

```python
from flask import request

@app.route('/webhooks/mmpay', methods=['POST'])
def mmpay_webhook():
    payload_str = request.data.decode('utf-8')
    nonce = request.headers.get('X-Mmpay-Nonce')
    signature = request.headers.get('X-Mmpay-Signature')

    try:
        is_valid = MMPay.verify_cb(payload_str, nonce, signature)
        
        if is_valid:
            return "Verified", 200
        else:
            return "Invalid Signature", 400

    except ValueError as e:
        return str(e), 400
```

## Error Codes

### API Key Layer (SERVER Side)

| Code | Description |
| :--- | :--- |
| `KA0001` | Bearer Token Not Included |
| `KA0002` | API Key Not 'LIVE' |
| `KA0003` | Signature mismatch |
| `KA0004` | Internal Server Error |
| `KA0005` | IP Not whitelisted |
| `429` | Rate limit hit (1000 req/min) |

### JWT Layer (SERVER Side)

| Code | Description |
| :--- | :--- |
| `BA001` | `Btoken` nonce token missing |
| `BA002` | `Btoken` nonce mismatch |

## License

MIT