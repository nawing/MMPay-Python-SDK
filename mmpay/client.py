import time
import json
import hmac
import hashlib
import requests
from typing import List, Optional, TypedDict, Dict, Any, Union

class Item(TypedDict):
    name: str
    amount: float
    quantity: int

class _PaymentRequestRequired(TypedDict):
    orderId: str
    amount: float

class PaymentRequest(_PaymentRequestRequired, total=False):
    items: List[Item]
    currency: str
    callbackUrl: str
    customMessage: str

class _XPaymentRequestRequired(TypedDict):
    appId: str
    nonce: str

class XPaymentRequest(PaymentRequest, _XPaymentRequestRequired):
    pass

class HandShakeRequest(TypedDict):
    orderId: str
    nonce: str

class HandShakeResponse(TypedDict):
    token: str

class CallbackIncomingData(TypedDict):
    orderId: str
    amount: float
    method: str
    currency: str
    vendor: str
    status: str
    condition: str
    transactionRefId: str
    callbackUrl: Optional[str]
    customMessage: Optional[str]

class SDKOptions(TypedDict):
    appId: str
    publishableKey: str
    secretKey: str
    apiBaseUrl: str

class _PayGetRequestRequired(TypedDict):
    orderId: str

class PayGetRequest(_PayGetRequestRequired, total=False):
    nonce: str

class PayGetResponse(TypedDict, total=False):
    appId: str
    orderId: str
    amount: float
    vendor: str
    method: str
    customMessage: str
    callbackUrl: str
    callbackUrlStatus: str
    callbackAt: str
    disbursementId: str
    disStatus: str
    status: str
    condition: str
    createdAt: str
    transactionRefId: str
    qr: str
    url: str

class MMPaySDK:
    def __init__(self, options: SDKOptions):
        self._app_id = options['appId']
        self._publishable_key = options['publishableKey']
        self._secret_key = options['secretKey']
        self._api_base_url = options['apiBaseUrl'].rstrip('/')
        self._btoken: Optional[str] = None

    def _generate_signature(self, body_string: str, nonce: str) -> str:
        string_to_sign = f"{nonce}.{body_string}"
        return hmac.new(
            self._secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _get_nonce(self) -> str:
        return str(int(time.time() * 1000))

    def _json_stringify(self, data: Any) -> str:
        return json.dumps(data, separators=(',', ':'))

    def sandbox_handshake(self, payload: HandShakeRequest) -> Union[HandShakeResponse, Dict[str, Any]]:
        endpoint = f"{self._api_base_url}/payments/sandbox-handshake"
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
            return {"error": str(e), "details": getattr(e.response, 'text', '')}

    def sandbox_pay(self, params: PaymentRequest) -> Dict[str, Any]:
        endpoint = f"{self._api_base_url}/payments/sandbox-create"
        nonce = self._get_nonce()

        xpayload: Dict[str, Any] = {
            "appId": self._app_id,
            "nonce": nonce,
            "amount": params['amount'],
            "orderId": params['orderId'],
        }

        if 'items' in params:
            xpayload['items'] = params['items']
        if 'callbackUrl' in params:
            xpayload['callbackUrl'] = params['callbackUrl']
        if 'customMessage' in params:
            xpayload['customMessage'] = params['customMessage']

        body_string = self._json_stringify(xpayload)
        signature = self._generate_signature(body_string, nonce)

        handshake_payload: HandShakeRequest = {
            'orderId': str(xpayload['orderId']), 
            'nonce': str(xpayload['nonce'])
        }
        
        handshake_res = self.sandbox_handshake(handshake_payload)
        if 'error' in handshake_res:
            return handshake_res

        headers = {
            'Authorization': f"Bearer {self._publishable_key}",
            'X-Mmpay-Btoken': self._btoken or '',
            'X-Mmpay-Nonce': nonce,
            'X-Mmpay-Signature': signature,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(endpoint, data=body_string, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": getattr(e.response, 'text', '')}

    def sandbox_get(self, params: PayGetRequest) -> Union[PayGetResponse, Dict[str, Any]]:
        endpoint = f"{self._api_base_url}/payments/sandbox-get"
        nonce = self._get_nonce()

        xpayload: Dict[str, Any] = {
            "orderId": params['orderId'],
            "nonce": nonce
        }

        body_string = self._json_stringify(xpayload)
        signature = self._generate_signature(body_string, nonce)

        handshake_payload: HandShakeRequest = {
            'orderId': str(xpayload['orderId']),
            'nonce': str(xpayload['nonce'])
        }

        handshake_res = self.sandbox_handshake(handshake_payload)
        if 'error' in handshake_res:
            return handshake_res

        headers = {
            'Authorization': f"Bearer {self._publishable_key}",
            'X-Mmpay-Btoken': self._btoken or '',
            'X-Mmpay-Nonce': nonce,
            'X-Mmpay-Signature': signature,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(endpoint, data=body_string, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": getattr(e.response, 'text', '')}

    def handshake(self, payload: HandShakeRequest) -> Union[HandShakeResponse, Dict[str, Any]]:
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
            return {"error": str(e), "details": getattr(e.response, 'text', '')}

    def pay(self, params: PaymentRequest) -> Dict[str, Any]:
        endpoint = f"{self._api_base_url}/payments/create"
        nonce = self._get_nonce()

        xpayload: Dict[str, Any] = {
            "appId": self._app_id,
            "nonce": nonce,
            "amount": params['amount'],
            "orderId": params['orderId'],
        }

        if 'items' in params:
            xpayload['items'] = params['items']
        if 'callbackUrl' in params:
            xpayload['callbackUrl'] = params['callbackUrl']
        if 'customMessage' in params:
            xpayload['customMessage'] = params['customMessage']

        body_string = self._json_stringify(xpayload)
        signature = self._generate_signature(body_string, nonce)

        handshake_payload: HandShakeRequest = {
            'orderId': str(xpayload['orderId']), 
            'nonce': str(xpayload['nonce'])
        }
        
        handshake_res = self.handshake(handshake_payload)
        if 'error' in handshake_res:
            return handshake_res

        headers = {
            'Authorization': f"Bearer {self._publishable_key}",
            'X-Mmpay-Btoken': self._btoken or '',
            'X-Mmpay-Nonce': nonce,
            'X-Mmpay-Signature': signature,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(endpoint, data=body_string, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": getattr(e.response, 'text', '')}

    def get(self, params: PayGetRequest) -> Union[PayGetResponse, Dict[str, Any]]:
        endpoint = f"{self._api_base_url}/payments/get"
        nonce = self._get_nonce()

        xpayload: Dict[str, Any] = {
            "orderId": params['orderId'],
            "nonce": nonce
        }

        body_string = self._json_stringify(xpayload)
        signature = self._generate_signature(body_string, nonce)

        handshake_payload: HandShakeRequest = {
            'orderId': str(xpayload['orderId']),
            'nonce': str(xpayload['nonce'])
        }

        handshake_res = self.handshake(handshake_payload)
        if 'error' in handshake_res:
            return handshake_res

        headers = {
            'Authorization': f"Bearer {self._publishable_key}",
            'X-Mmpay-Btoken': self._btoken or '',
            'X-Mmpay-Nonce': nonce,
            'X-Mmpay-Signature': signature,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(endpoint, data=body_string, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": getattr(e.response, 'text', '')}

    def verify_cb(self, payload: str, nonce: str, expected_signature: str) -> bool:
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