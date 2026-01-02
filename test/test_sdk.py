from mmpay import MMPaySDK

# Initialize
sdk = MMPaySDK({
    "appId": "your_app_id",
    "publishableKey": "your_pub_key",
    "secretKey": "your_secret_key",
    "apiBaseUrl": "https://api.mmpay.com" # Example URL
})

# Create a Payment (Sandbox)
response = sdk.sandbox_pay({
    "orderId": "ORD-123456789",
    "amount": 1000,
    "callbackUrl": "https://yoursite.com/callback",
    "items": [
        {"name": "Test Item", "amount": 1000, "quantity": 1}
    ]
})

print(response)