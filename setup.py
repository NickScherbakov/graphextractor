from setuptools import setup, find_packages

setup(
    name="graphextractor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "opencv-python>=4.5.0",
        "networkx>=2.6.0",
        "scikit-image>=0.18.0",
        "matplotlib>=3.4.0",
        "torch>=1.9.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pillow>=8.2.0",
    ],
    author="GraphExtractor Team",
    description="A service for detecting and extracting graph structures from images",
    python_requires=">=3.8",
)
