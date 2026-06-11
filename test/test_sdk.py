import time
import os
import random
import string
from dotenv import load_dotenv
from mmpay.types import PaymentRequest

# from mmpay import MMPaySDK
from mmpay import MMPaySDK  

# Load environment variables from .env file
load_dotenv()

def generate_secure_random_string(length: int) -> str:
    """
    Generates a random alphanumeric string.
    """
    # Using random.choices to generate a string of requested length
    # This mimics the base36 behavior of the JS example
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

def start():
    """
    Executes the payment call and measures network latency.
    """
    # Initialize SDK
    # specific env keys matching your JS example
    mmpay = MMPaySDK({
        'appId': os.getenv('APP_ID', ''),
        'publishableKey': os.getenv('PUB_KEY', ''),
        'secretKey': os.getenv('SEC_KEY', ''),
        'apiBaseUrl': os.getenv('BASEURL', '')
    })

    # Generate Order ID
    order_id = generate_secure_random_string(6)

    # Start Timer
    # time.perf_counter() is the Python equivalent to performance.now()
    start_time = time.perf_counter()

    try:
        payload: PaymentRequest = {
            "orderId": order_id,
            "amount": 1500,
            "customMessage": "MyanMyanPay Is The Best",
            "items": [{"name": "Items", "amount": 3000, "quantity": 1}]
        }

        # Execute Payment (Synchronous in Python version)
        response = mmpay.pay(payload)

        # End Timer
        end_time = time.perf_counter()
        
        # Calculate latency in milliseconds
        latency_ms = (end_time - start_time) * 1000

        print(f"\n--- Transaction Request Successful ---")
        print(f"Order ID: {order_id}")
        print(f"**Network Latency: {latency_ms:.3f} ms**")
        print(f"Response: {response}")
        print(f"------------------------------\n")

    except Exception as error:
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        print(f"\n--- Transaction Request Failed ---")
        print(f"Order ID: {order_id}")
        print(f"**Network Latency: {latency_ms:.3f} ms**")
        print(f"Error Message: {str(error)}")
        print(f"--------------------------\n")

if __name__ == "__main__":
    start()