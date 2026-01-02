from setuptools import setup, find_packages

setup(
    name="mmpay-python-sdk",
    version="0.1.0",
    description="Python SDK for MMPay (Ported from JS)",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    python_requires=">=3.6",
)