import time
import json
import hmac
import hashlib
import requests
from typing import Dict, Any, Union, Callable, List, Optional
from .types import (
    SDKOptions,
    HandShakeRequest,
    HandShakeResponse,
    PaymentRequest,
    PaymentResponse,
    PayGetRequest,
    PayGetResponse,
    PayCancelRequest,
    PayCancelResponse,
    CallbackIncomingData
)

class MMPaySDK:
    def __init__(self, options: SDKOptions):
        self._app_id = options['appId']
        self._publishable_key = options['publishableKey']
        self._secret_key = options['secretKey']
        self._api_base_url = options['apiBaseUrl'].rstrip('/')
        self._is_sandbox = '_test_' in self._publishable_key or '_test_' in self._secret_key
        self._btoken: Optional[str] = None
        self._listeners: Dict[str, List[Callable]] = {
            'tx:create': [],
            'tx:success': [],
            'tx:failed': [],
            'tx:refunded': [],
            'tx:cancel': [],
            'tx:expire': [],
            'tx:heartbeat': [],
            'tx:unknown': [],
            'error': []
        }

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

    def on(self, event: str, callback: Callable) -> 'MMPaySDK':
        if event in self._listeners:
            self._listeners[event].append(callback)
        return self

    def emit(self, event: str, *args, **kwargs) -> None:
        if event in self._listeners:
            for cb in self._listeners[event]:
                cb(*args, **kwargs)

    def handshake(self, payload: HandShakeRequest) -> Union[HandShakeResponse, Dict[str, Any]]:
        path = "/payments/sandbox-handshake" if self._is_sandbox else "/payments/handshake"
        endpoint = f"{self._api_base_url}{path}"
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

    def pay(self, params: PaymentRequest) -> Union[PaymentResponse, Dict[str, Any]]:
        path = "/payments/sandbox-create" if self._is_sandbox else "/payments/create"
        endpoint = f"{self._api_base_url}{path}"
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
        path = "/payments/sandbox-get" if self._is_sandbox else "/payments/get"
        endpoint = f"{self._api_base_url}{path}"
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

    def cancel(self, params: PayCancelRequest) -> Union[PayCancelResponse, Dict[str, Any]]:
        path = "/payments/sandbox-cancel" if self._is_sandbox else "/payments/cancel"
        endpoint = f"{self._api_base_url}{path}"
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
            return False
        return True

    def listen(self, payload: str, nonce: str, expected_signature: str) -> 'MMPaySDK':
        try:
            is_valid = self.verify_cb(payload, nonce, expected_signature)
            if not is_valid:
                self.emit('error', ValueError('Signature verification failed'))
                return self
            tx = json.loads(payload)
            status = tx.get('status')
            if status == 'PENDING':
                self.emit('tx:create', tx)
            elif status == 'SUCCESS':
                if tx.get('condition') == 'TOUCHED':
                    self.emit('tx:heartbeat', tx)
                else:
                    self.emit('tx:success', tx)
            elif status == 'FAILED':
                self.emit('tx:failed', tx)
            elif status == 'REFUNDED':
                self.emit('tx:refunded', tx)
            elif status == 'CANCELLED':
                self.emit('tx:cancel', tx)
            elif status == 'EXPIRED':
                self.emit('tx:expire', tx)
            else:
                self.emit('tx:unknown', tx)
        except Exception as err:
            self.emit('error', err)
        return self

    def on_tx_create(self, cb: Callable) -> 'MMPaySDK':
        return self.on('tx:create', cb)

    def on_tx_success(self, cb: Callable) -> 'MMPaySDK':
        return self.on('tx:success', cb)

    def on_tx_fail(self, cb: Callable) -> 'MMPaySDK':
        return self.on('tx:failed', cb)

    def on_tx_refund(self, cb: Callable) -> 'MMPaySDK':
        return self.on('tx:refunded', cb)

    def on_tx_cancel(self, cb: Callable) -> 'MMPaySDK':
        return self.on('tx:cancel', cb)

    def on_tx_expire(self, cb: Callable) -> 'MMPaySDK':
        return self.on('tx:expire', cb)

    def on_heartbeat(self, cb: Callable) -> 'MMPaySDK':
        return self.on('tx:heartbeat', cb)