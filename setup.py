from setuptools import setup, find_packages
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="mmpay-python-sdk",
    version="0.1.2",
    description="Python SDK for MyanMyanPay (Ported from JS)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Naw Ing",
    author_email="nawing@myanmyanpay.com",
    url="https://github.com/nawing/MMPay-Python-SDK", # Link to your repo
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
    ],
    python_requires=">=3.6",
)