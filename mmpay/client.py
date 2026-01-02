import time
import json
import hmac
import hashlib
import requests
from typing import List, Optional, TypedDict, Dict, Any

# --- Type Definitions to mirror your Interfaces ---

class Item(TypedDict):
    name: str
    amount: float
    quantity: int

class PaymentRequest(TypedDict):
    orderId: str
    amount: float
    items: List[Item]
    currency: Optional[str]
    callbackUrl: Optional[str]

class XPaymentRequest(PaymentRequest, total=False):
    appId: str
    nonce: str

class HandShakeRequest(TypedDict):
    orderId: str
    nonce: str

class SDKOptions(TypedDict):
    appId: str
    publishableKey: str
    secretKey: str
    apiBaseUrl: str

# --- Main SDK Class ---

class MMPaySDK:
    def __init__(self, options: SDKOptions):
        """
        Initializes the SDK with the merchant's keys and the API endpoint.
        """
        self._app_id = options['appId']
        self._publishable_key = options['publishableKey']
        self._secret_key = options['secretKey']
        self._api_base_url = options['apiBaseUrl'].rstrip('/')
        self._btoken: Optional[str] = None

    def _generate_signature(self, body_string: str, nonce: str) -> str:
        """
        Generates an HMAC SHA256 signature for request integrity.
        """
        string_to_sign = f"{nonce}.{body_string}"
        return hmac.new(
            self._secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _get_nonce(self) -> str:
        """Helper to get current timestamp as string (milliseconds)"""
        return str(int(time.time() * 1000))

    def _json_stringify(self, data: Any) -> str:
        """
        Mimics JS JSON.stringify exactly (no spaces).
        Crucial for signature verification.
        """
        return json.dumps(data, separators=(',', ':'))

    # --- Sandbox Methods ---

    def sandbox_handshake(self, payload: HandShakeRequest) -> Dict[str, Any]:
        endpoint = f"{self._api_base_url}/payments/sandbox-handshake"
        nonce = self._get_nonce()
        
        # Ensure payload is serialized exactly as the signature expects
        body_string = self._json_stringify(payload)
        signature = self._generate_signature(body_string, nonce)

        headers = {
            'Authorization': f"Bearer {self._publishable_key}",
            'X-Mmpay-Nonce': nonce,
            'X-Mmpay-Signature': signature,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(endpoint, data=body_string, headers=headers)
            response.raise_for_status()
            data = response.json()
            if 'token' in data:
                self._btoken = data['token']
            return data
        except requests.exceptions.RequestException as e:
            # In a real SDK, you might want to raise custom exceptions here
            return {"error": str(e), "details": response.text if response else None}

    def sandbox_pay(self, params: PaymentRequest) -> Dict[str, Any]:
        endpoint = f"{self._api_base_url}/payments/sandbox-create"
        nonce = self._get_nonce()

        # Construct payload
        xpayload: XPaymentRequest = {
            "appId": self._app_id,
            "nonce": nonce,
            "amount": params['amount'],
            "orderId": params['orderId'],
            "items": params['items'],
        }
        if 'callbackUrl' in params:
            xpayload['callbackUrl'] = params['callbackUrl']
        if 'currency' in params:
            xpayload['currency'] = params['currency']

        body_string = self._json_stringify(xpayload)
        signature = self._generate_signature(body_string, nonce)

        # Perform handshake first (as per TS logic)
        handshake_res = self.sandbox_handshake({'orderId': xpayload['orderId'], 'nonce': xpayload['nonce']})
        if 'error' in handshake_res:
            return handshake_res

        headers = {
            'Authorization': f"Bearer {self._publishable_key}",
            'X-Mmpay-Btoken': self._btoken,
            'X-Mmpay-Nonce': nonce,
            'X-Mmpay-Signature': signature,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(endpoint, data=body_string, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": response.text if response else None}

    # --- Production Methods ---

    def handshake(self, payload: HandShakeRequest) -> Dict[str, Any]:
        endpoint = f"{self._api_base_url}/payments/handshake"
        nonce = self._get_nonce()
        
        body_string = self._json_stringify(payload)
        signature = self._generate_signature(body_string, nonce)

        headers = {
            'Authorization': f"Bearer {self._publishable_key}",
            'X-Mmpay-Nonce': nonce,
            'X-Mmpay-Signature': signature,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(endpoint, data=body_string, headers=headers)
            response.raise_for_status()
            data = response.json()
            if 'token' in data:
                self._btoken = data['token']
            return data
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": response.text if response else None}

    def pay(self, params: PaymentRequest) -> Dict[str, Any]:
        endpoint = f"{self._api_base_url}/payments/create"
        nonce = self._get_nonce()

        xpayload: XPaymentRequest = {
            "appId": self._app_id,
            "nonce": nonce,
            "amount": params['amount'],
            "orderId": params['orderId'],
            "items": params['items'],
        }
        if 'callbackUrl' in params:
            xpayload['callbackUrl'] = params['callbackUrl']
        if 'currency' in params:
            xpayload['currency'] = params['currency']

        body_string = self._json_stringify(xpayload)
        signature = self._generate_signature(body_string, nonce)

        # Perform handshake
        handshake_res = self.handshake({'orderId': xpayload['orderId'], 'nonce': xpayload['nonce']})
        if 'error' in handshake_res:
            return handshake_res

        headers = {
            'Authorization': f"Bearer {self._publishable_key}",
            'X-Mmpay-Btoken': self._btoken,
            'X-Mmpay-Nonce': nonce,
            'X-Mmpay-Signature': signature,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(endpoint, data=body_string, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": response.text if response else None}

    # --- Verification ---

    def verify_cb(self, payload: str, nonce: str, expected_signature: str) -> bool:
        """
        Verifies the signature of a callback request.
        """
        if not payload or not nonce or not expected_signature:
            raise ValueError("Callback verification failed: Missing payload, nonce, or signature.")

        string_to_sign = f"{nonce}.{payload}"
        generated_signature = hmac.new(
            self._secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != expected_signature:
            print(f"Signature mismatch: gen={generated_signature}, exp={expected_signature}")
            return False
        
        return True