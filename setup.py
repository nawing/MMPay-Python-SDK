from setuptools import setup, find_packages

setup(
    name="mmpay-python-sdk",
    version="0.1.2",
    description="Python SDK for MyanMyanPay (Ported from JS)",
    author="Naw Ing",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    python_requires=">=3.6",
)