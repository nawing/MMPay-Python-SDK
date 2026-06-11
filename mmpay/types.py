from typing import List, TypedDict

class Item(TypedDict):
    name: str
    amount: float
    quantity: int

class _PaymentRequestRequired(TypedDict):
    orderId: str
    amount: float

class PaymentRequest(_PaymentRequestRequired, total=False):
    currency: str
    callbackUrl: str
    customMessage: str
    items: List[Item]

class _XPaymentRequestRequired(TypedDict):
    appId: str
    nonce: str

class XPaymentRequest(PaymentRequest, _XPaymentRequestRequired):
    pass

class PaymentResponse(TypedDict):
    orderId: str
    amount: float
    currency: str
    status: str
    vendorQrRefId: str
    transactionRefId: str
    qr: str
    url: str

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
    vendorQrRefId: str
    qr: str
    url: str

class _PayCancelRequestRequired(TypedDict):
    orderId: str

class PayCancelRequest(_PayCancelRequestRequired, total=False):
    nonce: str

class _PayCancelResponseRequired(TypedDict):
    amount: float
    orderId: str
    status: str

class PayCancelResponse(_PayCancelResponseRequired, total=False):
    vendorQrRefId: str

class HandShakeRequest(TypedDict):
    orderId: str
    nonce: str

class HandShakeResponse(TypedDict):
    token: str

class _CallbackIncomingDataRequired(TypedDict):
    orderId: str
    amount: float
    method: str
    currency: str
    vendor: str
    status: str
    condition: str
    transactionRefId: str

class CallbackIncomingData(_CallbackIncomingDataRequired, total=False):
    callbackUrl: str
    customMessage: str

class SDKOptions(TypedDict):
    appId: str
    publishableKey: str
    secretKey: str
    apiBaseUrl: str