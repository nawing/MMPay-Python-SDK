# MMPay Python SDK

A Python client library for integrating with the MMPay Payment Gateway. This SDK is a direct port of the official Node.js SDK, providing utilities for payment creation, transaction retrieval, handshake authentication, and callback verification for technical architects and developers.

## ⬇️ 1. Installation

```bash 
pip install mmpay-python-sdk 
```

## ⚙️ 2. Configuration

To use the SDK, you need your App ID, Publishable Key, and Secret Key provided by the MyanMyanPay dashboard.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| appId | str | Yes | Your unique Application ID. |
| publishableKey | str | Yes | Public key for authentication. |
| secretKey | str | Yes | Private key used for signing requests (HMAC). |
| apiBaseUrl | str | Yes | The base URL for the MMPay API. |

**Implementation**

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


## 💳 3. Make Payment

**Method Signature**
```python
from mmpay.types import PaymentRequest
payload: PaymentRequest = {}
MMPay.pay(payload)
```

**Implementation**

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

**Request Body** (`payload` structure)
The request body should be a JSON object containing the transaction details.

| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`orderId`**         | `string` | **Yes**    | Your generated order ID for the order or system initiating the payment. | `"ORD-3983833"` |
| **`amount`**          | `number` | **Yes**    | The total transaction amount. | `1500.50` |
| **`callbackUrl`**     | `string` | No         | The URL where the payment gateway will send transaction status updates. | `"https://yourserver.com/webhook"` |
| **`currency`**        | `string` | No         | The currency code (e.g., `'MMK'`). | `"MMK"` |
| **`customMessage`**   | `string` | No         | Your Customization String |
| **`items`**           | `Array<Object>` | No  | List of items included in the purchase. | `[{name: "Hat", amount: 1000, quantity: 1}]` |

**Item Object**


| Field | Type | Description |
| :--- | :--- | :--- |
| **`name`** | `string` | The name of the item. |
| **`amount`** | `number` | The unit price of the item. |
| **`quantity`** | `number` | The number of units purchased. |

**Response Body** Code (`201`)
The response body should be a JSON object containing the following information.

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


## 🚀 4. Retrieve Payment Information

**Method Signature**
```python
from mmpay.types import PayGetRequest
payload: PayGetRequest = {}
MMPay.get(payload)
```

**Implementation**
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

**Request Body** (`payload` structure)
The request body should be a JSON object containing the transaction details.

| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`orderId`**         | `string` | **Yes**    | Your generated order ID for the order or system initiating the payment. | `"ORD-3983833"` |

**Response Body** Code (`200`)
The response body should be a JSON object containing the following information.

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

## 🚀 5. Cancel Payment

**Method Signature**
```python
from mmpay.types import PayCancelRequest
payload: PayCancelRequest = {}
MMPay.cancel(payload)
```

**Implementation**
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

**Request Body** (`payload` structure)
The request body should be a JSON object containing the transaction details.

| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`orderId`**         | `string` | **Yes**    | Your generated order ID for the order or system initiating the payment. | `"ORD-3983833"` |

**Response Body** Code (`200`)
The response body should be a JSON object containing the following information.

```json
{
  "amount": 1000,
  "orderId": "ORD-111111111",
  "status": "CANCELLED",
  "vendorQrRefId": "289348734939",
}
```

----


## 🔐 6. Handling Webhooks

When MyanMyanPay sends a callback to your `callbackUrl`[cite: 1], you must verify the request signature to ensure it is genuine. 
When you implement this method, our package automatically process the Hmac verification  

**Incoming Headers**

| Field Name | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `Content-Type` | `str` | Yes | `application/json` |
| `X-Mmpay-Signature` | `str` | Yes | Generated HMAC signature |
| `X-Mmpay-Nonce` | `str` | Yes | Unique nonce string |

**Incoming Body**

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

**Example Implementation With Flask**

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

----


### 7. Verify Callback (Manually)

When MyanMyanPay sends a callback to your `callbackUrl`[cite: 1], you must verify the request signature to ensure it is genuine. 

**Example Implementation With Flask**

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

----


## 8. Error Codes

**HMac Layer (SERVER Side)**

| Code | Description |
| :--- | :--- |
| `KA0001` | Bearer Token Not Included |
| `KA0002` | API Key Not 'LIVE' |
| `KA0003` | Signature mismatch |
| `KA0004` | Internal Server Error |
| `KA0005` | IP Not whitelisted |
| `429` | Rate limit hit (1000 req/min) |

**JWT Layer (SERVER Side)**

| Code | Description |
| :--- | :--- |
| `BA001` | `Btoken` nonce token missing |
| `BA002` | `Btoken` nonce mismatch |


**Response Codes**

| Code | Status | Description |
| :--- | :--- | :--- |
| **`201`** | Created | Transaction initiated successfully. Response contains QR code URL/details. |
| **`401`** | Unauthorized | Invalid or missing Publishable Key. |
| **`400`** | Bad Request | Missing required body fields (validated by schema, if implemented). |
| **`503`** | Service Unavailable | Upstream payment API failed or is unreachable. |
| **`500`** | Internal Server Error | General server error during payment initiation. |


---

## License

MIT