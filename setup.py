from setuptools import setup, find_packages

setup(
    name="mmpay-python-sdk",
    version="0.1.1",
    description="Python SDK for MMPay (Ported from JS)",
    author="MyanMyanPay",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    python_requires=">=3.6",
)